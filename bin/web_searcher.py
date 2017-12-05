#!/usr/bin/env python3
"""
Взаимодействие с поисковыми системами через dmenu.

Этот скрипт открывает файл ~/.db/wiki/search-engines.md,
позволяет выбрать поисковую систему из списка, спрашивает запрос.
"""

from os.path import expanduser, exists
import datetime
from socket import gethostname
import re
from csv import DictReader, DictWriter
import urllib.parse
import click
from pprint import pprint as pp

import helpers

ENGINES_PATH = expanduser('~/.db/wiki/search-engines.md')
HISTORY_PATH = expanduser('~/.db/wiki/search-history.csv')
CSV_FIELDS = ('engine', 'query', 'time', 'hostname')


class Engine():
    """Поисковик"""
    def __init__(self, line):
        self.line = line
    def name(self):
        """Получить название"""
        return re.match('(.*)(https?:.*)', self.line).groups()[0].strip()
    def url(self):
        """Получить ссылку"""
        return re.match('(.*)(https?:.*)', self.line).groups()[1].strip()


def isodatetime():
    """Получить iso строку времени"""
    return datetime.datetime.now(datetime.timezone.utc).isoformat()

def engines():
    """Получить список поисковых систем"""
    return [t.strip() for t in open(ENGINES_PATH).readlines()]

def old_queries(prefer=None):
    """Вернуть список запросов прошлых"""
    all_queries = list(reversed(list(DictReader(open(HISTORY_PATH)))))
    return ([t for t in all_queries if t['engine'] == prefer] +
            [t for t in all_queries if t['engine'] != prefer])

def save_query(obj):
    """Сохранить объект в базу"""
    obj['hostname'] = gethostname()
    obj['time'] = isodatetime()
    with open(HISTORY_PATH, 'a') as tfile:
        writer = DictWriter(tfile, CSV_FIELDS)
        writer.writerow(obj)


def get_engine(label='Выбор системы'):
    """Получить строку-поисковик"""
    return Engine(helpers.dmenu_file(expanduser(ENGINES_PATH), label=label))

def get_query(prefer=None, label='Запрос'):
    """Спросить поисковый запрос"""
    queries = []
    for itm in old_queries(prefer=prefer):
        if itm['query'] not in queries:
            queries.append(itm['query'])
    return helpers.dmenu_stdin(label, "\n".join(queries))

def ensure_history_file_exists():
    """Удостовериться что файл для истории запросов есть"""
    if not exists(HISTORY_PATH):
        with open(HISTORY_PATH, 'a+') as tfile:
            writer = DictWriter(tfile, CSV_FIELDS)
            writer.writeheader()

def last_query():
    """Получить последнюю запись из поиска"""
    return list(DictReader(open(HISTORY_PATH)))[-1]

def last_engine():
    """Получить последнюю поисковую систему"""
    name = last_query()['engine']
    for engine in engines():
        candidate = Engine(engine)
        if candidate.name() == name:
            return candidate

def save_and_open(engine, query):
    """Сохранить поисковый запрос в файл и открыть поиск в браузере"""
    if len(query):
        save_query({'engine': engine.name(), 'query': query})
        url = engine.url().replace("%s", urllib.parse.quote(query))
        helpers.open_in_browser(url)
        helpers.open_i3_workspace('www')

@click.group()
def cli():
    """Программа для открытия поисковика в браузере с заданным запросом"""
    pass

@cli.command()
def full_search():
    """Сделать всю работу"""
    engine = get_engine()
    query = get_query(prefer=engine.name(), label="Поиск в {}".format(engine.name()))
    save_and_open(engine, query)

@cli.command()
def last_engine_search():
    """Задать только запрос для поиска"""
    engine = last_engine()
    query = get_query(prefer=engine.name(), label="Поиск в {}".format(engine.name()))
    save_and_open(engine, query)

@cli.command()
def last_query_search():
    """Задать только систему поиска"""
    query = last_query()['query']
    engine = get_engine(label='Найти "{}" в'.format(query))
    save_and_open(engine, query)

if __name__ == '__main__':
    ensure_history_file_exists()
    cli()
