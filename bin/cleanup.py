#!/usr/bin/env python3

"""Глобальная чистка на компьютере"""

from glob import glob
from os.path import expanduser, basename


from colorama import Fore, Style, init
init()


OK_CODE = '✓'
FAIL_CODE = '✗'

HOME_WHITELISTED = ('_', 'mnt', 'venv')

def list_print(items):
    """Напечатать список строк """
    print(*['- '+t for t in items], sep='\n')

def fail_print(msg):
    """Напечатать сообщение об ошибке"""
    print(Fore.RED+FAIL_CODE+Style.RESET_ALL, msg)

def ok_print(msg):
    """Напечатать сообщение об успехе"""
    print(Fore.GREEN+OK_CODE+Style.RESET_ALL, msg)

def check_home_empty():
    """Проверить что в домашнем каталоге чисто"""
    all_files = [basename(f) for f in glob(expanduser('~/*'))]
    files = [f for f in all_files if f not in HOME_WHITELISTED]
    if files:
        fail_print("В домашнем каталоге есть мусор")
        list_print(files)
    else:
        ok_print("В домашнем каталоге чисто")


def main():
    """Произвести проверку системы на чистоту"""
    check_home_empty()

if __name__ == '__main__':
    main()
