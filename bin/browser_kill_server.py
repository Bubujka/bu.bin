#!/usr/bin/env python3
"""Сервер, который прибивает все запущенные процессы по списку названий"""

from subprocess import call
from time import sleep
from sys import argv

BLOCKED = ('chrome', 'google-chrome', 'chromium', 'chromium-browser',
           'firefox',
           'slack', 'Telegram', 'telegram')

TIMEOUT = 2

def kill(what):
    """Отправить сигнал на умирание процессу"""
    user = ""
    if len(argv) == 2:
        user = " -u "+argv[1]

    call("killall -KILL {} {} 2> /dev/null".format(what, user), shell=True)

def main():
    """Запустить сервер"""
    while True:
        for i in BLOCKED:
            kill(i)
        sleep(TIMEOUT)
        print('tick')

if __name__ == '__main__':
    main()
