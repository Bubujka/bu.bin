#!/usr/bin/env python3

"""Глобальная чистка на компьютере"""

from glob import glob
from os.path import expanduser, basename, dirname, exists
from subprocess import check_output, CalledProcessError
import shlex
from multiprocessing import Pool



from colorama import Fore, Style, init
init()


OK_CODE = '✓'
FAIL_CODE = '✗'

HOME_WHITELISTED = ('_', 'mnt', 'venv')

def list_print(items):
    """Напечатать список строк """
    print(*['- '+t for t in items], sep='\n')

def bool_to_code(t):
    """Превратить True/False в красивую иконку"""
    if t:
        return Fore.GREEN+OK_CODE+Style.RESET_ALL
    return Fore.RED+FAIL_CODE+Style.RESET_ALL

def fail_print(msg):
    """Напечатать сообщение об ошибке"""
    print(bool_to_code(False), msg)

def ok_print(msg):
    """Напечатать сообщение об успехе"""
    print(bool_to_code(True), msg)



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
        'find', expanduser('~/.db'), expanduser("~/.bu.bin"),
        '-type', 'd', '-name', '.git']).decode('utf-8').splitlines()
    return [dirname(f) for f in dirs]



class RepStatus():

    def __init__(self, pth):
        self.pth = pth
        self.exists = None

        self.have_origin = None
        self.commited = None
        self.pushed = None

        self.run_checks()


    def is_ok(self):
        return (self.exists and
                self.have_origin and
                self.pushed)

    def bash(self, cmd):
        return check_output(('cd {}; '+cmd).format(shlex.quote(self.pth)), shell=True).decode('utf-8').strip()

    def run_checks(self):
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
        if self.bash("""git log --branches --not --remotes | wc -l""") == '0':
            self.pushed = True
        else:
            self.pushed = False


def check_rep_clean_and_pushed(pth):
    """Проверить что репозиторий чист и запушен"""
    return RepStatus(pth)
    #try:
    #    check_output('test -z $(cd {}; git status --porcelain)'.format(shlex.quote(pth)), shell=True)
    #    with Pool() as p:
    #        print(p.map(f, [1, 2, 3]))
    #    ok_print("В каталоге {} всё чисто".format(pth))
    #except CalledProcessError:
    #    fail_print("В каталоге {} не закомичено".format(pth))

def check_all_reps_pushed():
    """Проверить что все репозитории запушены"""
    with Pool() as p:
        data = p.map(check_rep_clean_and_pushed, reps())
        for d in data:
            if not d.is_ok():
                print(bool_to_code(d.is_ok()), d.pth)
                print(" have origin", bool_to_code(d.have_origin))
                print(" commited", bool_to_code(d.commited))
                print(" pushed", bool_to_code(d.pushed))

def main():
    """Произвести проверку системы на чистоту"""
    check_home_empty()
    check_all_reps_pushed()

if __name__ == '__main__':
    main()
