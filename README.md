# cd_shortcuts

Creates a bash function

`cds`

which can be used to jump to directories which have been added using `cds-mod`

Install
```bash
git clone https://github.com/torpidtangerine/cd_shortcuts.git ~/.cd_shortcuts
python ~/.cd_shortcuts/ init
echo '[ -f ~/.cd_shortcuts/bash-snippet.bash ] && source ~/.cd_shortcuts/bash-snippet.bash' >> ~/.bash_profile
```

Uninstall
```bash
rm -rf ~/.cd_shortcuts
```
