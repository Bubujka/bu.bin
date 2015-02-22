alias ..='cd ../'

alias web-mail='cd ~/www/_mail'

alias tmp='cd ~/.db/tmp'
alias bin='cd ~/.bu.bin/bin'
alias www='cd /home/www'
alias aux='cd ~/.db/aux'
alias shared='cd /home/shared'
alias _='cd ~/.db/_'

function prog(){
        cd ~/.db/programming/$1
}

function prj(){
  if [ ! -d ~/.db/prj/$1 ] ; then
    mkdir ~/.db/prj/$1
  fi
  cd ~/.db/prj/$1
}

function life(){
        cd ~/.db/life/$1
}
