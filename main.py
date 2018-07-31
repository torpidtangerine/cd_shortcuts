import argparse
import sys
import os
from json import load, dump

DEFAULT_CONFIG = """
{
  "shortcuts": {
    "home": "~"
  },
  "archive": { },
}
""".lstrip('\n\r')

class ExitException(Exception):
  def __init__(self, message, exit_code):
    super(ExitException, self).__init__(message)
    self.exit_code = exit_code

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
    raise ExitException('Could not find config at %s' % config_file_path, 1)

  json_stream = open(config_file_path, 'r')
  data = load(json_stream)
  json_stream.close()

  if 'archive' not in data:
    data['archive'] = {}
  if 'shortcuts' not in data:
    data['shortcuts'] = {}

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

  cds_all(['--stream', 'stderr'])

  error_message = '\n"%s" was not found in shortcut file %s' % (args.folder, config_file_path)
  raise ExitException(error_message, 1)

# pylint: disable=unused-argument
def cds_all(argv):
  parser = get_default_parser('cd_shortcuts.all')
  parser.add_argument('-s', '--stream', default='stderr', help='print to stderr or stdout')
  parser.add_argument('-f', '--format', default='json', help='print as json or spaced')
  parser.add_argument('-a', '--archive-display',
    default=False,
    help='show archive',
    action='store_true')
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

  if not args.archive_display:
    config = dict(config)
    del config['archive']

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
    raise ExitException('name %s does not exists' % args.name, 1)

  del shortcuts[args.name]

  save_config(config_file_path, config)

def archive_nm(argv):
  parser = get_default_parser('cd_shortcuts.archive')
  parser.add_argument('-n', '--name', default=None, help='key to archive', required=True)
  args = parser.parse_args(argv)

  config, config_file_path = get_config(args.config)
  shortcuts = config['shortcuts']
  archive = config['archive']

  if args.name not in shortcuts:
    raise ExitException('name %s does not exist' % args.name, 1)

  if args.name in archive:
    raise ExitException('name %s already exists in archive' % args.name, 1)

  archive[args.name] = shortcuts[args.name]
  del shortcuts[args.name]

  save_config(config_file_path, config)

def unarchive_nm(argv):
  parser = get_default_parser('cd_shortcuts.archive')
  parser.add_argument('-n', '--name', default=None, help='key to unarchive', required=True)
  args = parser.parse_args(argv)

  config, config_file_path = get_config(args.config)
  shortcuts = config['shortcuts']
  archive = config['archive']

  if args.name in shortcuts:
    raise ExitException('name %s does already exist' % args.name, 1)

  if args.name not in archive:
    raise ExitException('name %s not in archive' % args.name, 1)

  shortcuts[args.name] = archive[args.name]
  del archive[args.name]

  save_config(config_file_path, config)

def rename(argv):
  parser = get_default_parser('cd_shortcuts.rename')
  parser.add_argument('-p', '--prev', default=None, help='prev name', required=True)
  parser.add_argument('-n', '--next', default=None, help='next name', required=True)
  args = parser.parse_args(argv)

  config, config_file_path = get_config(args.config)
  shortcuts = config['shortcuts']

  if args.prev not in shortcuts:
    raise ExitException('prev %s does not exists' % args.prev, 1)

  if args.next in shortcuts:
    raise ExitException('next %s already exists' % args.next, 1)

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
    raise ExitException('name %s already exists' % args.name, 1)

  shortcuts[args.name] = args.value

  save_config(config_file_path, config)

def set_folder(argv):
  parser = get_default_parser('cd_shortcuts.set')
  parser.add_argument('-n', '--name', default=None, help='key to change', required=True)
  parser.add_argument('-v', '--value', default=None, help='value to change to', required=True)
  args = parser.parse_args(argv)

  config, config_file_path = get_config(args.config)
  shortcuts = config['shortcuts']
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
  'set': set_folder,
  'remove': remove,
  'rename': rename,
  'archive': archive_nm,
  'unarchive': unarchive_nm,
  'init': cds_init,
}

def main():
  argv = sys.argv[:]
  if len(argv) < 2:
    argv = [__file__, 'help']

  action = argv[1]

  action = ALIAS_MAP.get(action, action)
  action_fn = ACTION_MAP.get(action, print_help)

  try:
    action_fn(argv[2:])
  except ExitException as exit_ex:
    sys.stderr.write('%s\n' % exit_ex.message)
    sys.exit(exit_ex.exit_code)

if __name__ == '__main__':
  main()
