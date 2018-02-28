#!/usr/bin/env python3

"""Глобальная чистка на компьютере"""

from glob import glob
from os.path import expanduser, basename, dirname, exists
from subprocess import check_output
import shlex
from multiprocessing import Pool



from colorama import Fore, Style, init
init()


OK_CODE = '✓'
FAIL_CODE = '✗'

ERRORS = 0

HOME_WHITELISTED = ('_', 'mnt', 'venv')

def list_print(items):
    """Напечатать список строк """
    print(*[' - '+t for t in items], sep='\n')

def bool_to_code(var):
    """Превратить True/False в красивую иконку"""
    if var:
        return Fore.GREEN+OK_CODE+Style.RESET_ALL
    return Fore.RED+FAIL_CODE+Style.RESET_ALL

def fail_print(msg):
    """Напечатать сообщение об ошибке"""
    print(bool_to_code(False), msg)

def ok_print(msg):
    """Напечатать сообщение об успехе"""
    print(bool_to_code(True), msg)



def check_directory_empty(directory, whitelisted=()):
    """Проверить что в каталоге чисто"""
    global ERRORS
    all_files = [basename(f) for f in glob(directory+'/*')]
    files = [f for f in all_files if f not in whitelisted]
    if files:
        fail_print("В каталоге '{}' есть мусор".format(directory))
        list_print(files)
        ERRORS += 1
    else:
        ok_print("В каталоге '{}' чисто".format(directory))


def reps():
    """Список каталогов где репы есть"""
    dirs = check_output([
        'find', expanduser('~/.db'), expanduser("~/.bu.bin"),
        '-type', 'd', '-name', '.git']).decode('utf-8').splitlines()
    return [dirname(f) for f in dirs]



class RepStatus():
    """Статус проверки репозитория"""
    def __init__(self, pth):
        self.pth = pth
        self.exists = None

        self.have_origin = None
        self.commited = None
        self.pushed = None

        self.run_checks()


    def is_ok(self):
        """Всё ли хорошо с репозиторием"""
        return (self.exists and
                self.have_origin and
                self.commited and
                self.pushed)

    def bash(self, cmd):
        """Выполнить команду внутри репозитория"""
        return check_output(('cd {}; '+cmd).format(shlex.quote(self.pth)), shell=True).decode('utf-8').strip()

    def run_checks(self):
        """Проверить репозиторий на чистоту"""

        if not exists(self.pth):
            self.exists = False
            return
        else:
            self.exists = True
        if self.bash('git status --porcelain') == '':
            self.commited = True

        if self.bash("""cat .git/config | grep 'remote "origin"' | wc -l""") == '0':
            self.have_origin = False
        else:
            self.have_origin = True

        self.pushed = self.bash("""git log --branches --not --remotes | wc -l""") == '0'


def check_rep_clean_and_pushed(pth):
    """Проверить что репозиторий чист и запушен"""
    return RepStatus(pth)

def check_all_reps_pushed():
    """Проверить что все репозитории запушены"""
    global ERRORS
    with Pool() as pool:
        for repstat in pool.map(check_rep_clean_and_pushed, reps()):
            if not repstat.is_ok():
                ERRORS += 1
                print(bool_to_code(repstat.is_ok()), repstat.pth)
                print(" have origin", bool_to_code(repstat.have_origin))
                print(" commited", bool_to_code(repstat.commited))
                print(" pushed", bool_to_code(repstat.pushed))


def check_letters_indexed():
    """Проверить что письма проиндексированы"""
    global ERRORS
    index = open(expanduser('~/.db/wiki/letters-index.md')).read()
    files = ['letters/'+basename(f) for f in glob(expanduser('~/.db/wiki/letters/*.md'))]
    not_found = [f for f in files if f not in index]
    if not_found:
        fail_print("Не все письма проиндексированы")
        list_print(files)
        ERRORS += 1
    else:
        ok_print("Все письма проиндексированы")



def main():
    """Произвести проверку системы на чистоту"""
    check_directory_empty(expanduser('~'), whitelisted=HOME_WHITELISTED)
    check_directory_empty(expanduser('~/_'))
    check_letters_indexed()
    check_all_reps_pushed()
    exit(min(1, ERRORS))

if __name__ == '__main__':
    main()
