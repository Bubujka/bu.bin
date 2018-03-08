#!/usr/bin/env python3
"""
Менеджер привычек
"""

import json
import sys
import tty
import termios
from functools import lru_cache
from os.path import expanduser, exists
from datetime import date, timedelta
from subprocess import call

import click
from colorama import Fore, Style, init as init_colorama, ansi
from prompt_toolkit import prompt

def getch():
    """Get a single character from stdin, Unix version\nhttps://gist.github.com/payne92/11090057"""
    stdin = sys.stdin.fileno()
    old_settings = termios.tcgetattr(stdin)
    try:
        tty.setraw(sys.stdin.fileno())
        char = sys.stdin.read(1)
    finally:
        termios.tcsetattr(stdin, termios.TCSADRAIN, old_settings)
    return char

CFG_FILE = expanduser("~/.db/wiki/habit-config.json")
DATA_FILE = expanduser("~/.db/wiki/habits.json")

OK_CODE = '✓'
FAIL_CODE = '✗'
BLANK_CODE = '·'
STORE = []
DATE = None

init_colorama()


def is_global_hotkey(answer):
    """Данный хоткей относится к глобальным?"""
    if answer == 'Q':
        return True
    if answer == 'C':
        return True
    return False

def do_global_action(answer):
    """Выполнить действие из любого скрина"""
    if answer == 'Q':
        exit()
    if answer == 'C':
        call(['vim', expanduser('~/.db/wiki/habit-config.json')])

class Store():
    """Хранилище данных"""
    data = []

    @classmethod
    def load(cls):
        """Считать данные с файла"""
        if exists(DATA_FILE):
            cls.data = json.loads(open(DATA_FILE).read())

    @classmethod
    def save(cls):
        """Записать всё на диск"""
        open(DATA_FILE, 'w').write(json.dumps(cls.data, indent=2))


class Application():
    """Состояние приложения"""

    def __init__(self, tdate):
        self.date = tdate

    def print_header(self):
        """Напечатать строку заголовка"""
        suffix = ""
        if date.today() == self.date:
            suffix = " (Сегодня)"
        elif (date.today() - timedelta(days=1)) == self.date:
            suffix = " (Вчера)"
        print(Fore.YELLOW + str(self.date) + suffix, Style.RESET_ALL)

    def print_stats(self):
        """Напечатать статистику за день"""
        self.print_header()

        items = habits()
        ok_items = [h for h in items if h.is_ok()]
        fail_items = [h for h in items if not h.is_ok()]

        mappings = {}

        i = 0
        if fail_items:
            print(Fore.RED+"Надо сделать:"+Style.RESET_ALL)
            for habit in fail_items:
                i += 1
                mappings[i] = habit
                print_with_number(habit, i)
        #if ok_items:
        #    print(Fore.GREEN+"Сделано:"+Style.RESET_ALL)
        #    for habit in ok_items:
        #        i += 1
        #        mappings[i] = habit
        #        print_with_number(habit, i)
        return mappings


class Habit():
    """Привычка"""

    def __init__(self, config_obj):
        self.config = config_obj
        self.name = config_obj['name']
        self.tag = config_obj['tag']
        self.code = config_obj['name']

    def per_interval(self):
        """Сколько событий за интервал"""
        return int(self.config['interval'].split('/')[0])

    def interval_length(self):
        """Длина интервала"""
        return int(self.config['interval'].split('/')[1])

    def interval_for_print(self):
        """Вывести интервал для печати"""
        candidate = self.config.get('interval', '7/7')
        if candidate != '7/7':
            return candidate
        return ''

    def stats(self):
        """Получить статистику"""
        r = []
        today = today_date()
        for i in range(0, 30):
            day = today - timedelta(days=i)
            t = get_stats_for(self,  day)
            if t:
                r.append(t)
            elif self.reached_limit(day):
                r.append({'code': 'auto'})
            else:
                r.append(None)
        return r


    def reached_limit(self, day=None):
        """Достигнут недельный лимит"""
        if 'interval' not in self.config:
            return False
        if day is None:
            day = today_date()
        stats = [get_stats_for(self, day - timedelta(days=i))
                 for i
                 in range(0, self.interval_length()-1)]
        return len([s for s in stats if s]) >= self.per_interval()

    def is_ok(self):
        """Выполнено ли на сегодня?"""
        if get_stats_for(self, today_date()):
            return True
        if self.reached_limit():
            return True
        return False


    def skip(self):
        """Пропустить это"""
        Store.data.append({'code': self.code, 'date': str(today_date()), 'skip': True})

    def toggle(self):
        """Переключить состояние у привычки на текущую дату"""
        if self.is_ok():
            self.remove_today()
        else:
            Store.data.append({'code': self.code, 'date': str(today_date())})

    def done(self):
        """Пометить выполненным"""
        Store.data.append({'code': self.code, 'date': str(today_date())})

    def undone(self):
        """Развыполнить"""
        self.remove_today()

    def remove_today(self):
        """Удалить из истории сегодняшнюю запись"""
        for log in Store.data:
            if log['code'] == self.code:
                if log['date'] == str(today_date()):
                    Store.data.remove(log)


def clear_screen():
    """Зачистить экран"""
    print(ansi.clear_screen())



def to_code(state):
    """Превратить буль в код"""
    if state is None:
        ret = BLANK_CODE
    elif state:
        if state.get('skip'):
            ret = 's'
        elif state.get('code') == 'auto':
            ret = OK_CODE
        else:
            ret = Fore.GREEN + OK_CODE
    else:
        ret = Fore.RED + FAIL_CODE
    return ret + Style.RESET_ALL


def color_stats(stats):
    """Вывести статистику в виде цветной строки"""
    return "".join([to_code(t) for t in stats])

def get_stats_for(habit, day):
    """Получить статистику за дату"""
    for log in Store.data:
        if log['code'] == habit.code:
            if log['date'] == str(day):
                return log
    return None


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



def today_date():
    """Дата, над которой мы сейчас работаем"""
    global DATE

    if DATE:
        return DATE

    return date.today()


@click.group(invoke_without_command=True)
def main():
    """Менеджер привычек"""
    if len(sys.argv) == 1:
        repl_loop(Application(date.today()))


def nice_number(current):
    """Цифра с отступом"""
    return str(current).ljust(4)


def color_tag(tag):
    """Раскрасить тэг"""
    prefix = ""
    if tag == 'home':
        prefix = Style.BRIGHT+Fore.GREEN
    if tag == 'comp':
        prefix = Style.BRIGHT+Fore.BLUE
    if tag == 'food':
        prefix = Style.BRIGHT+Fore.MAGENTA
    return prefix+tag+Style.RESET_ALL


def print_with_number(habit, number):
    """Напечатать строку и её номер"""
    print(color_tag(habit.tag).ljust(7, " "),
          nice_number(number),
          habit.name.ljust(max_name_length() + 5, " "),
          color_stats(habit.stats()),
          habit.interval_for_print())

def nice_print(habit):
    """Напечатать строку и её номер"""
    print(color_tag(habit.tag).ljust(7, " "),
          habit.name.ljust(max_name_length() + 5, " "),
          color_stats(habit.stats()),
          habit.interval_for_print())


def ask_what_todo():
    """Запросить команду от человека"""
    return prompt("Что делать будем: ")


def ask_what_to_skip():
    """Запросить что нужно скипнуть"""
    return prompt("Пропустить: ")


def repl_loop(app):
    """Главный цикл"""

    while True:
        clear_screen()
        mappings = app.print_stats()
        answer = char_input()

        if is_global_hotkey(answer):
            do_global_action(answer)
            continue

        if answer == 's':
            second_answer = ask_what_to_skip()
            for number in second_answer.strip().split(" "):
                print(number)
                habit = mappings[int(number)]
                habit.skip()
            continue

        if answer == 'Q':
            exit()
        if answer == 'q':
            Store.save()
            exit()
        if answer == 't':
            Store.save()
            repl_loop(Application(date.today()))
            continue
        if answer == 'y':
            Store.save()
            repl_loop(Application(date.today() - timedelta(days=1)))
            continue
        if answer == 'p':
            Store.save()
            repl_loop(Application(app.date - timedelta(days=1)))
            continue
        if answer == 'n':
            Store.save()
            repl_loop(Application(app.date + timedelta(days=1)))
            continue
        if answer == '':
            continue
        number = int(answer)
        habit = mappings[number]
        habit.toggle()


@main.command()
def today():
    """Отредактировать сегодняшний день"""
    repl_loop(Application(date.today()))


@main.command()
def yesterday():
    """Отредактировать вчерашний день"""
    repl_loop(Application(date.today() - timedelta(days=1)))


def char_input(prompt="$ "):
    """Получить 1 символ от человека"""
    print(prompt, end="", flush=True)
    return getch()


@main.command()
def one_by_one():
    """По одной карточке спросить что делать"""
    items = habits()

    fail_items = [h for h in items if not h.is_ok()]
    app = Application(date.today())
    for habit in fail_items:
        do_action(habit, app)

@main.command()
def one_by_one_all():
    """По одной карточке спросить что делать для всех"""
    app = Application(date.today())
    for habit in habits():
        do_action(habit, app)

def do_action(habit, app):
    """Произвести действие по команде"""
    while True:
        clear_screen()
        app.print_header()
        nice_print(habit)
        answer = char_input()

        if is_global_hotkey(answer):
            do_global_action(answer)
            continue

        if answer == 'C':
            call(['vim', expanduser('~/.db/wiki/habit-config.json')])
        if answer == 's':
            habit.skip()
            Store.save()
            break
        if answer == 'd':
            habit.done()
            Store.save()
            break
        if answer == 'u':
            habit.undone()
            Store.save()
            break
        if answer == 'l':
            break
        if answer == 'q':
            exit()



if __name__ == '__main__':
    Store.load()
    main()
