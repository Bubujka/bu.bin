#!/usr/bin/env python3
# Менеджер привычек

import json
from functools import lru_cache
from os.path import expanduser, exists
from datetime import date, timedelta

import click
from colorama import Fore, Style, init, ansi


CFG_FILE = expanduser("~/.db/wiki/habit-config.json")
DATA_FILE = expanduser("~/.db/wiki/habits.json")

OK_CODE = '✓'
FAIL_CODE = '✗'
BLANK_CODE = '·'
STORE = []

init()

def clear_screen():
    print(ansi.clear_screen())


def load_data():
    """Загрузить данные из файла"""
    if exists(DATA_FILE):
        return json.loads(open(DATA_FILE).read())
    return []



def save():
    """Сохранить состояние store"""
    open(DATA_FILE, 'w').write(json.dumps(STORE, indent=2))


def to_code(state):
    """Превратить буль в код"""
    if state is None:
        ret = BLANK_CODE
    elif state:
        ret = Fore.GREEN + OK_CODE
    else:
        ret = Fore.RED + FAIL_CODE
    return ret + Style.RESET_ALL


class Habit():
    """Привычка"""

    def __init__(self, config_obj):
        self.repeat = config_obj.get('repeat', 7)
        self.name = config_obj['name']
        self.code = config_obj['name']

    def stats(self):
        """Получить статистику"""
        today = today_date()
        return [get_stats_for(self, today - timedelta(days=i)) for i in range(0,13)]


    def reached_week_limit(self):
        """Достигнут недельный лимит"""
        today = today_date()
        stats = [get_stats_for(self, today - timedelta(days=i)) for i in range(0, 6)]
        return len([s for s in stats if s]) >= self.repeat


    def is_ok(self):
        """Выполнено ли на сегодня?"""
        if get_stats_for(self, today_date()):
            return True
        if self.reached_week_limit():
            return True



    def toggle(self):
        """"""
        if self.is_ok():
            self.remove_today()
        else:
            STORE.append({ 'code': self.code, 'date': str(today_date()) })

    def remove_today(self):
        """Удалить из истории сегодняшнюю запись"""
        for s in STORE:
            if s['code'] == self.code:
                if s['date'] == str(today_date()):
                    STORE.remove(s)



def get_stats_for(habit, day):
    for s in STORE:
        if s['code'] == habit.code:
            if s['date'] == str(day):
                return True


@lru_cache()
def cfg():
    """Прочитать конфиг"""
    return json.loads(open(CFG_FILE).read())


@lru_cache()
def habits():
    """Вернуть список привычек"""
    return [Habit(c) for c in cfg()['items']]

@lru_cache()
def max_name_length():
    """Вернуть максимальную длину названий"""
    return max([len(i['name']) for i in cfg()['items']])


def color_stats(stats):
    return "".join([to_code(t) for t in stats])


def today_date():
    return date.today()


@click.group()
def main():
    """Менеджер привычек"""


def nice_number(current):
    return str(current).ljust(4)

def print_stats():
    """"""
    print(Fore.YELLOW + str(today_date()), Style.RESET_ALL)

    items = habits()
    ok_items = [h for h in items if h.is_ok()]
    fail_items = [h for h in items if not h.is_ok()]

    mappings = {}

    i = 0
    if len(fail_items):
        print(Fore.RED+"Надо сделать:"+Style.RESET_ALL)
        for h in fail_items:
            i += 1
            mappings[i] = h
            print(nice_number(i), h.name.ljust(max_name_length() + 5, " "),  color_stats(h.stats()))
    if len(ok_items):
        print(Fore.GREEN+"Сделано:"+Style.RESET_ALL)
        for h in ok_items:
            i += 1
            mappings[i] = h
            print(nice_number(i), h.name.ljust(max_name_length() + 5, " "),  color_stats(h.stats()))
    return mappings

def ask_what_todo():
    return input("Что делать будем: ")

def repl_loop():
    """"""
    clear_screen()
    mappings = print_stats()
    answer = ask_what_todo()
    if answer == 'q':
        save()
        exit()
    number = int(answer)
    habit = mappings[number]
    habit.toggle()
    save()
    repl_loop()


@main.command()
def today():
    """Отредактировать сегодняшний день"""
    repl_loop()


if __name__ == '__main__':
    STORE = load_data()
    main()

