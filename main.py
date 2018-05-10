import argparse
import sys
import os
from json import load, dump

DEFAULT_CONFIG = """
{
  "shortcuts": {
    "home": "~"
  }
}
""".lstrip('\n\r')

def get_default_parser(name):
  parser = argparse.ArgumentParser(description=name,
    formatter_class=argparse.RawTextHelpFormatter)
  parser.add_argument('-c', '--config', default=None, help='Config file to use')
  return parser

def get_config_file_path(config_file_path):
  if not config_file_path:
    config_file_path = os.path.join(os.environ['HOME'], '.config', 'cd_shortcuts_config.json')

  return config_file_path

def get_config(config_file_path):
  config_file_path = get_config_file_path(config_file_path)

  if not os.path.exists(config_file_path):
    print 'Could not find config at %s' % config_file_path
    sys.exit(1)

  json_stream = open(config_file_path, 'r')
  data = load(json_stream)
  json_stream.close()
  return data, config_file_path

def save_config(config_file_path, config):
  json_stream = open(config_file_path, 'w')
  dump(config, json_stream, indent=2)
  json_stream.write('\n')
  json_stream.close()

def folder(argv):
  parser = get_default_parser('cd_shortcuts.folder')
  parser.add_argument('-f', '--folder', default=None, help='folder to print', required=True)
  args = parser.parse_args(argv)

  config, config_file_path = get_config(args.config)

  shortcuts = config['shortcuts']
  if args.folder in shortcuts:
    folder_value = shortcuts[args.folder]
    folder_value = os.path.expanduser(folder_value)
    print folder_value
    return

  alt_folder = os.path.expanduser(args.folder)
  if os.path.isdir(alt_folder):
    print alt_folder
    return

  error_message = '"%s" was not found in shortcut file %s\n\n' % (args.folder, config_file_path)
  sys.stderr.write(error_message)
  cds_all(['--stream', 'stderr'])
  sys.exit(1)

# pylint: disable=unused-argument
def cds_all(argv):
  parser = get_default_parser('cd_shortcuts.all')
  parser.add_argument('-s', '--stream', default='stderr', help='print to stderr or stdout')
  parser.add_argument('-f', '--format', default='json', help='print as json or spaced')
  parser.add_argument('-m', '--matching', default=None, help='matching a substring')
  args = parser.parse_args(argv)

  stream = None
  if args.stream == 'stderr':
    stream = sys.stderr
  elif args.stream == 'stdout':
    stream = sys.stdout
  else:
    raise Exception('unknown stream %s' % args.stream)

  config, _ = get_config(args.config)
  if args.format == 'json':
    dump(config, stream, indent=2)
    stream.write('\n')
  elif args.format == 'spaced':
    line = config['shortcuts'].keys()

    if args.matching:
      next_line = []
      for key in line:
        if args.matching in key:
          next_line.append(key)
      line = next_line

    stream.write(' '.join(line) + '\n')

def cds_init(argv):
  parser = get_default_parser('cd_shortcuts.init')
  args = parser.parse_args(argv)

  config_file_path = get_config_file_path(args.config)
  config_file_path_dir = os.path.dirname(config_file_path)

  if os.path.exists(config_file_path):
    return

  try:
    os.makedirs(config_file_path_dir)
  except OSError:
    pass

  with open(config_file_path, 'w') as config_handle:
    config_handle.write(DEFAULT_CONFIG)

def print_default(_):
  sys.stdout.write(DEFAULT_CONFIG)

def remove(argv):
  parser = get_default_parser('cd_shortcuts.remove')
  parser.add_argument('-n', '--name', default=None, help='key to remove', required=True)
  args = parser.parse_args(argv)

  config, config_file_path = get_config(args.config)
  shortcuts = config['shortcuts']

  if args.name not in shortcuts:
    print 'name %s does not exists' % args.name
    sys.exit(1)

  del shortcuts[args.name]

  save_config(config_file_path, config)

def rename(argv):
  parser = get_default_parser('cd_shortcuts.rename')
  parser.add_argument('-p', '--prev', default=None, help='prev name', required=True)
  parser.add_argument('-n', '--next', default=None, help='next name', required=True)
  args = parser.parse_args(argv)

  config, config_file_path = get_config(args.config)
  shortcuts = config['shortcuts']

  if args.prev not in shortcuts:
    print 'prev %s does not exists' % args.prev
    sys.exit(1)

  if args.next in shortcuts:
    print 'next %s already exists' % args.next
    sys.exit(1)

  shortcut_to = shortcuts[args.prev]
  del shortcuts[args.prev]
  shortcuts[args.next] = shortcut_to

  save_config(config_file_path, config)

def add(argv):
  parser = get_default_parser('cd_shortcuts.add')
  parser.add_argument('-n', '--name', default=None, help='key to add', required=True)
  parser.add_argument('-v', '--value', default=None, help='value to add', required=True)
  args = parser.parse_args(argv)

  config, config_file_path = get_config(args.config)
  shortcuts = config['shortcuts']

  if args.name in shortcuts:
    print 'name %s already exists' % args.name
    sys.exit(1)

  shortcuts[args.name] = args.value

  save_config(config_file_path, config)

ACTION_MAP = None

def print_help(argv):
  print 'Display help for an action with'
  print '[action] -h'
  print ''
  print 'Actions:'
  for key in ACTION_MAP.iterkeys():
    print '  %s' % key

ALIAS_MAP = {
  '-h': 'help',
  '--help': 'help',
}

ACTION_MAP = {
  'all': cds_all,
  'print_default': print_default,
  'folder': folder,
  'help': print_help,
  'add': add,
  'remove': remove,
  'rename': rename,
  'init': cds_init,
}

def main():
  action = None
  if len(sys.argv) >= 2:
    action = sys.argv[1]
  else:
    action = 'help'

  if action in ALIAS_MAP:
    action = ALIAS_MAP[action]

  if action in ACTION_MAP:
    ACTION_MAP[action](sys.argv[2:])
  else:
    print 'Action %s not found' % action
    print 'ACTION_MAP:'
    for key in ACTION_MAP.iterkeys():
      print key
    sys.exit(1)

if __name__ == '__main__':
  main()
