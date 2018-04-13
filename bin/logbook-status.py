#!/usr/bin/env python3
"""Посчитать статус логбука"""
from glob import glob
from os.path import expanduser, basename, getsize
from datetime import datetime, timedelta

from colorama import Fore, Style, init
init()
def sorted_files():
    """Получить список файлов в logbook и их размер"""
    return {basename(t)[:-3]: getsize(t) for t in glob(expanduser('~/.db/wiki/logbook/*.md'))}

stats = sorted_files()

def to_d(d):
    """Преобразовать время в день"""
    return d.strftime('%Y-%m-%d')

def color_for(day):
    if stats_for(day) > 50:
        return Fore.GREEN
    return Fore.RED

def stats_for(day):
    return stats.get(to_d(day), 0)



def main():
    today = datetime.today()
    for i in range(30, -1, -1):
        day = today - timedelta(days=i)
        print(color_for(day) + to_d(day), str(stats_for(day)).rjust(5, ' '))

if __name__ == '__main__':
    main()
