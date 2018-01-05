#!/usr/bin/env python3
"""
Перехват логов активности в i3
"""

from subprocess import check_output
from json import loads
from time import sleep, time
from datetime import datetime
from csv import DictWriter, DictReader
from os.path import expanduser, exists, basename
from os import makedirs
from socket import gethostname
from glob import glob

import re


COLS = ('hostname', 'time', 'workspace', 'software', 'title')
INTERVAL = 2
IDLE_LIMIT_SECONDS = 120
DIRECTORY = expanduser('~/.db/i3-logs')


def get_focused(tree):
    """Получить список активных нод"""
    ret = []
    for node in tree['nodes'] + tree['floating_nodes']:
        for i in get_focused(node):
            ret.append(i)
    if len(ret):
        ret.insert(0, tree)
    if tree['focused']:
        ret.append(tree)
    return ret

def idlerow():
    """Запись для простоя"""
    return {
        "time": time(),
        "workspace": None,
        "software": 'Idle...',
        "title": None,
        "hostname": gethostname()
    }

def parse_line(line):
    """Разобрать строку в словарь"""
    ret = {
        "time": time(),
        "workspace": None,
        "software": None,
        "title": None,
        "hostname": gethostname()
    }
    if len(line) == 4:
        ret['workspace'] = line[3]['name']
        return ret
    elif len(line) == 5:
        ret['workspace'] = line[3]['name']
        ret['software'] = line[4]['window_properties']['instance']
        ret['title'] = line[4]['name']
        return ret
    elif len(line) == 6:
        ret['workspace'] = line[3]['name']
        ret['software'] = line[5]['window_properties']['instance']
        ret['title'] = line[5]['name']
        return ret


def get_line(line):
    """Получить представление"""
    if len(line) == 4:
        return line[3]['name']
    elif len(line) == 5:
        return "{} -> {} ({})".format(
            line[3]['name'],
            line[4]['window_properties']['instance'],
            line[4]['name'])

    else:
        return " -> ".join([str(t['name']) for t in line])


def idletime():
    """Получить время в миллисекундах, сколько за компом не работаю"""
    return int(check_output('xprintidle').decode('utf-8').strip())


def do_magic():
    """main loop"""
    prev = None
    is_idle = False
    prev_date = None
    while True:
        if prev_date != today():
            prev_date = today()
            check_directory_and_file_exists()
            log_file = DictWriter(open(log_path(), 'a', 1), COLS)
        out = loads(check_output(['i3-msg', '-t', 'get_tree']).decode('utf-8'))
        focused = get_focused(out)
        line = get_line(focused)
        if line != prev:
            prev = line
            print(datetime.now(), line)
            log_file.writerow(parse_line(focused))

        if idletime() > IDLE_LIMIT_SECONDS * 1000:
            if not is_idle:
                print(datetime.now(), "idle...")
                log_file.writerow(idlerow())
                is_idle = True
        else:
            is_idle = False
        sleep(INTERVAL)


def today():
    """Сегодняшняя дата"""
    return datetime.now().date()


def log_path(day=today(), host=gethostname()):
    """Получить путь до лог файла"""
    return '{}/{}-{}.csv'.format(DIRECTORY, day, host)


def log_reader(pth=log_path()):
    """Получить DictReader на текущий лог"""
    return DictReader(open(pth))


def check_directory_and_file_exists():
    """Проверить что есть каталог для логов и файл"""
    makedirs(DIRECTORY, exist_ok=True)
    pth = log_path()
    if not exists(pth):
        with open(pth, 'w') as tfile:
            csv = DictWriter(tfile, COLS)
            csv.writeheader()

class LogFile():
    def __init__(self, pth):
        self.pth = pth

    def day(self):
        """День за который лог"""
        return re.sub(r'(\d+-\d+-\d+)-(.*)', r'\1', basename(self.pth))

    def host(self):
        """Хост у лога"""
        return re.sub(r'(\d+-\d+-\d+)-(.*)', r'\2', basename(self.pth))

    def reader(self):
        """Получить ридер у данного лога"""
        return log_reader(self.pth)

def all_logs():
    """Получить список логов"""
    return [LogFile(l) for l in sorted(glob(DIRECTORY + '/*.csv'))]


if __name__ == '__main__':
    check_directory_and_file_exists()
    do_magic()
