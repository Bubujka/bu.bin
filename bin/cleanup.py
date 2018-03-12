#!/usr/bin/env python3

"""Глобальная чистка на компьютере"""

from glob import glob
from os.path import expanduser, basename, dirname, exists, isdir, islink
from subprocess import check_output
import shlex
from multiprocessing import Pool

OK_CODE = '✓'
FAIL_CODE = '✗'

ERRORS = 0

HOME_WHITELISTED = ('_', 'mnt', 'venv')

IGNORE_WIKI_INDEX = ("letters/", "logbook/", "contacts/", ".snippet.md")

def list_print(items):
    """Напечатать список строк """
    print(*[' - '+t for t in items], sep='\n')

def bool_to_code(var):
    """Превратить True/False в красивую иконку"""
    if var:
        return OK_CODE
    return FAIL_CODE

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

def must_be_indexed(pth):
    """Надо ли вообще индексировать этот файл в wiki?"""
    for ptrn in IGNORE_WIKI_INDEX:
        if ptrn in pth:
            return False
    return True

def check_wiki_indexed():
    """Проверить что вики проиндексирована"""
    global ERRORS
    index = open(expanduser('~/.db/wiki/index.md')).read()
    files = [f.replace(expanduser('~/.db/wiki/'), '')
             for f
             in glob(expanduser('~/.db/wiki/**/*.md'), recursive=True)]

    not_found = [f for f in files if must_be_indexed(f) and f not in index]
    if not_found:
        fail_print("Не все файлы в вики проиндексированы")
        list_print(not_found)
        ERRORS += 1

def check_db_indexed():
    """Проверить что все каталоги в db проиндексированы"""
    global ERRORS
    index = open(expanduser('~/.db/wiki/index.md')).read()

    files = [basename(f)
             for f
             in glob(expanduser('~/.db/*'))]

    if files:
        fail_print("Не все папки в ~/.db проиндексированы")
        list_print(files)
        ERRORS += 1
def check_all_on_git():
    """Проверить что все проекты под гитом"""
    global ERRORS
    for root_dir in ('beta', 'prj', 'omega'):
        contents = glob(expanduser('~/.db/{}/*'.format(root_dir)))
        for something in contents:
            if islink(something):
                continue
            if not isdir(something):
                fail_print("Что-то не то в каталоге лежит '{}'".format(something))
                ERRORS += 1
                continue
            if not exists(something+'/.git'):
                fail_print("Каталог '{}' не под git".format(something))
                ERRORS += 1


def check_files_indexed():
    """Проверить что все статичные файлы проиндексированы"""
    global ERRORS

    with open(expanduser('~/.db/wiki/static-files.md')) as tfile:
        txt = tfile.read()
        for directory in glob(expanduser('~/.db/files/*')):
            if isdir(directory):
                if basename(directory) not in txt:
                    fail_print('Каталог {} не проиндексирован'.format(directory))




def main():
    """Произвести проверку системы на чистоту"""
    check_directory_empty(expanduser('~'), whitelisted=HOME_WHITELISTED)
    check_directory_empty(expanduser('~/_'))
    check_files_indexed()
    check_all_on_git()
    check_wiki_indexed()
    check_db_indexed()
    check_all_reps_pushed()
    exit(min(1, ERRORS))

if __name__ == '__main__':
    main()
