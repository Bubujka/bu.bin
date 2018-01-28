#!/usr/bin/env python3
"""Напечатать документацию по всем моим командам"""

from glob import glob
from os.path import expanduser, islink, basename, isdir
from os import readlink
import re
import functools

from colorama import Fore, Style, init

DIR = expanduser("~/.bu.bin/bin")
LANG_SIGNATURE = {
    '#!/bin/bash': 'bash',
    '#!/bin/bash -xe': 'bash',
    '#!/usr/bin/env python3': 'python3',
    '#!/usr/bin/env ruby': 'ruby',
    '#!/usr/bin/env node': 'node',
    '#!/usr/bin/env bash': 'bash',
    '#!/usr/bin/env php': 'php'
}

init()

class Command():
    """Команда в моих скриптах"""

    def __init__(self, pth):
        self.pth = pth
        with open(self.pth) as file:
            self.intro = [t.strip() for t in file.readlines()[:2]]

    def name(self):
        """Получить название команды"""
        return basename(self.pth)

    def lang(self):
        """Получить язык, на котором написана команда"""
        hashbang = self.intro[0]
        for sig, lang in LANG_SIGNATURE.items():
            if hashbang == sig:
                return lang
        return hashbang


    def have_doc(self):
        """Есть ли у данной команды блок с описанием?"""

        if len(self.intro) == 2:
            if self.lang() == 'php':
                if re.match(r'^<\?php #.*', self.intro[1]):
                    return True
            if re.match('^#.*', self.intro[1]):
                return True
        return False


    def doc(self):
        """Получить описание команды"""
        if self.have_doc():
            if self.lang() == 'php':
                return self.intro[1][7:].strip()
            return self.intro[1][1:].strip()
        return None

    def aliases(self):
        """Получить список алиасов у команды"""
        return [t for t in symlinks() if t.origin() == self.name()]

    def have_aliases(self):
        """Есть ли у данной команды алиас"""
        return len(self.aliases())

class Symlink:
    """Алиас для команды"""
    def __init__(self, pth):
        self.pth = pth

    def name(self):
        """Получить название симлинка"""
        return basename(self.pth)

    def origin(self):
        """Получить основную команду"""
        return basename(readlink(self.pth))


def is_cmd(cmd):
    """Проверить что это файл"""
    return not islink(cmd) and not isdir(cmd)

def is_cmd_link(cmd):
    """Проверить что это симлинк на команду"""
    return islink(cmd) and not isdir(readlink(cmd))

def commands():
    """Вернуть список команд"""
    return [Command(p) for p in glob(DIR+'/*') if is_cmd(p)]

@functools.lru_cache()
def symlinks():
    """Вернуть список команд"""
    return [Symlink(p) for p in glob(DIR+'/*') if is_cmd_link(p)]

def print_cmd(cmd):
    """Напечатать 1 команду в консоль"""
    doc = ''

    if cmd.have_doc():
        doc = ' - ' + str(cmd.doc())

    aliases = ""

    if cmd.have_aliases():
        aliases = " "+Fore.GREEN +" ".join([t.name() for t in cmd.aliases()])

    print("- "+
          Fore.YELLOW+cmd.name() +
          aliases +
          Fore.BLUE + ' ('+cmd.lang()+')' +
          Style.RESET_ALL + doc)

def main():
    """Напечатать список всех моих команд и их краткое описание"""

    all = commands();
    documented = [t for t in all if t.have_doc()]
    undocumented = [t for t in all if not t.have_doc()]
    if len(documented):
        print("# Задокументированные\n")
        for cmd in sorted(documented, key=lambda t: t.name()):
            print_cmd(cmd)
    if len(undocumented):
        print("\n\n# Непойми что\n")
        for cmd in sorted(undocumented, key=lambda t: t.name()):
            print_cmd(cmd)



if __name__ == '__main__':
    main()
