#!/usr/bin/env python3

"""Глобальная чистка на компьютере"""

from glob import glob
from os.path import expanduser, basename, dirname
from os import walk
from subprocess import check_output, CalledProcessError



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


def reps():
    """Список каталогов где репы есть"""
    dirs = check_output([
        'find', expanduser('~/.db'),
        '-type', 'd', '-name', '.git']).decode('utf-8').splitlines()
    return [dirname(f) for f in dirs]


def check_rep_clean_and_pushed(pth):
    """Проверить что репозиторий чист и запушен"""
    try:
        ok_print("В каталоге {} всё чисто".format(pth))
    except CalledProcessError as e:
        fail_print("В каталоге {} не закомичено".format(pth))

def check_all_reps_pushed():
    """Проверить что все репозитории запушены"""
    for rep in reps():
        check_rep_clean_and_pushed(rep)

def main():
    """Произвести проверку системы на чистоту"""
    check_home_empty()
    check_all_reps_pushed()

if __name__ == '__main__':
    main()
