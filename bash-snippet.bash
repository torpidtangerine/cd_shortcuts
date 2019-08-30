cds-mod() {
  python ~/.cd_shortcuts "$@"
}

cds() {
  if [ "$1" == "" ]; then
    cds-mod all
    echo use 'cds-mod' to modify
    return
  fi

  if [ -d "$1" ]; then
    cd "$1"
    return
  fi

  FD=`python ~/.cd_shortcuts folder -f "$1"`
  if [ $? != 0 ]
  then
    unset FD
    cd "$1"
    return
  fi
  cd $FD
  unset FD
}

__cds_complete() {
  PREV="${COMP_WORDS[COMP_CWORD]}"
  PART="$(python ~/.cd_shortcuts all -s stdout -f spaced)"
  COMPREPLY=( $(compgen -W "$PART" -- "$PREV") )
  unset PART
  unset PREV
  return 0
}

complete -F __cds_complete cds

cds-or() {
  if [ "$1" == "" ]; then
    cd
    return
  fi

  if [ -d "$1" ]; then
    cd "$1"
    return
  fi

  FD=`python ~/.cd_shortcuts folder_noerr -f "$1"`
  if [ $? != 0 ]
  then
    unset FD
    cd "$1"
    return
  fi
  cd $FD
  unset FD
}
