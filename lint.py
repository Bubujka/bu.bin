#!/usr/bin/env python3
"""Проверить все скрипты подходящим линтером"""

from glob import glob
from subprocess import check_output, CalledProcessError
from os.path import islink, isfile
from multiprocessing import Pool


def files():
    """Список скриптов для проверки"""
    return [f for f in glob('bin/*') if isfile(f) and not islink(f)]

def firstline(file):
    """Получить первую строку из файла"""
    return open(file).readline().strip()


def is_python_file(file):
    """Является ли файл - python скриптом"""
    return firstline(file) in ('#!/usr/bin/env python3',)

def is_bash_file(file):
    """Является ли файл - bash скриптом"""
    return firstline(file) in ('#!/usr/bin/env bash', '#!/bin/bash')

def checkwith(linter, file):
    """Проверить файл линтером и вернуть результат"""
    try:
        check_output([linter, file])
        return True
    except CalledProcessError as err:
        print("-"*80)
        print("\n\n# ", file)
        print(err.stdout.decode())
        return False



def check_file(file):
    """Проверить один файл"""
    if is_python_file(file):
        return checkwith('pylint3', file)
    if is_bash_file(file):
        return checkwith('shellcheck', file)
    return None


def main():
    """Проверить всё"""
    have_errors = False

    errors = 0
    skipped = 0
    with Pool() as pool:
        for result in pool.map(check_file, files()):
            if result is False:
                errors += 1
                have_errors = True

            if result is None:
                skipped += 1

    print("\n\n\n")
    print("Total files: ", len(files()))
    print("Errors: ", errors)
    print("Skipped: ", skipped)

    if have_errors:
        exit(1)

if __name__ == '__main__':
    main()
