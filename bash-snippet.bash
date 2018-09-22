type cds-mod 2>/dev/null

if [ $? -eq 0 ]; then
  return
fi

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
    return
  fi
  cd $FD
  unset FD
}
