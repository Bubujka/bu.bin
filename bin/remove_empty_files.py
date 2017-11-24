#!/usr/bin/env python3

"""Удалить пустые файлы из каталога"""

from glob import glob
from sys import argv, stderr
from os.path import isdir, getsize
from os import unlink

def clear_directory():
    """Получить путь, который нужно почистить"""
    return argv[1]

def is_file_empty(pth):
    """Проверить - является ли файл пустым"""
    return bool(getsize(pth))

def check_command_parameters():
    """Нужно удостовериться что есть с чем работать"""
    if len(argv) is 1:
        stderr.write('Нужно передать путь до каталога, в котором требуется удалить файлы')
        exit(1)

    if not isdir(clear_directory()):
        stderr.write('Переданный путь ({}) не является каталогом'.format(clear_directory()))
        exit(2)

def each_file_in(pth):
    """Вернуть список файлов из заданного каталога"""
    return glob(pth + '/*')

def do_magic():
    """Сделать всё..."""
    check_command_parameters()

    for pth in each_file_in(clear_directory()):
        if not is_file_empty(pth):
            unlink(pth)

if __name__ == '__main__':
    do_magic()
