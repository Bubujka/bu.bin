#!/usr/bin/env python3
#---
#title: Добавление строки в секцию # [unsorted] у файла
#tags: [plan.md]
#refs: []
#---

"""Добавление строки в секцию # [unsorted] у файла"""

from sys import argv
from os.path import exists

LINE = argv[1].strip()
DEST_FILE = argv[2]

UNSORTED_LINE = "## [unsorted]"

def check_file_exists():
    """Проверить существование файла"""
    if not exists(DEST_FILE):
        print("File '{}' not exists!".format(DEST_FILE))
        exit(1)


def main():
    """Сделать всё"""
    check_file_exists()
    data = open(DEST_FILE).read()
    if UNSORTED_LINE not in data:
        data = UNSORTED_LINE+'\n\n'+data

    data = data.replace(UNSORTED_LINE, UNSORTED_LINE+'\n'+LINE)

    open(DEST_FILE, 'w').write(data)


if __name__ == '__main__':
    main()
