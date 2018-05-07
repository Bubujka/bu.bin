#!/usr/bin/env python3

"""Печать списка названий из моей вики"""

from glob import glob
from os.path import expanduser
from re import match

def slice_raw_definition(line):
    """Разрезать строку на определение и слово"""
    matches = match('^- (.*):(.*)', line.strip()).groups()
    return (matches[0].strip(), matches[1].strip())

class WikiFile():
    """Мой файл в wiki. Типо markdown"""
    def __init__(self, pth):
        self.pth = pth
        self.contents = open(pth).read()

    def has_names(self):
        """Содержит ли файл секцию names?"""
        return "## names" in self.contents

    def title(self):
        """Вернуть заголовок файла"""
        line = self.contents.splitlines()[0]
        return line.strip().replace('# ', '')

    def names(self):
        """Получить список имён из файла"""
        raw = []
        collecting = False
        for line in self.contents.splitlines():
            if "## names" in line:
                collecting = True
                continue
            if collecting:
                if match('^- ', line):
                    raw.append(line)
                else:
                    collecting = False
        return [slice_raw_definition(t) for t in raw]


def main():
    """Вывести всё в консоль"""
    all_files = [WikiFile(f) for f in sorted(glob(expanduser('~/.db/wiki/*.md')))]
    correct_files = [f for f in all_files if f.has_names()]
    for wikifile in correct_files:
        for (name, definition) in wikifile.names():
            print(wikifile.title(), name, definition, sep=' → ')

if __name__ == '__main__':
    main()
