#!/usr/bin/env python3

from subprocess import call
from time import sleep
from sys import argv

BLOCKED = ('chrome', 'google-chrome', 'chromium', 'chromium-browser', 'slack', 'Telegram', 'telegram')

def kill(what):
    user = ""
    if len(argv) == 2:
        user = " -u "+argv[1]

    call("killall -KILL {} {} 2> /dev/null".format(what, user), shell=True)

def main():
    while True:
        for i in BLOCKED:
            kill(i)
        sleep(2)
        print('tick')


if __name__ == '__main__':
    main()
