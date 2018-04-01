#!/usr/bin/env python3
from os.path import expanduser
import re
from random import choice
from subprocess import call
import sys


def notify(msg):
    call(['notify-flash', 'Readlist', msg])

class Document():
    def __init__(self):
        self.sections = []

    def print(self):
        for s in self.sections:
            s.print()

    def section_by_name(self, name):
        for i in self.sections:
            if i.name() == name:
                return i

    def save(self):
        oldstdout = sys.stdout
        sys.stdout = open(expanduser('~/.db/wiki/readlist.md'), 'w')
        self.print()
        sys.stdout = oldstdout()

class Section():
    def __init__(self, line):
        self.line = line
        self.lines = []

    def name(self):
        return self.line.text.replace('# ', '')

    def print(self):
        print('#', self.name())
        for l in self.lines:
            l.print()
        print()

    def random_line(self):
        return choice(self.lines)

    def remove_line(self, line):
        self.lines.remove(line)

    def append_line(self, line):
        self.lines.append(line)

class Line():
    def __init__(self, text):
        self.text = text.strip()

    def is_section(self):
        return re.match('^# ', self.text)

    def print(self):
        print(self.text)

    def url(self):
        return re.search("(?P<url>https?://[^\s]+)", self.text).group("url")


def parse_file(obj):
    d = Document()
    s = None
    for text_line in obj.readlines():
        if text_line.strip():
            line = Line(text_line)

            if line.is_section():
                if s:
                    d.sections.append(s)
                s = Section(line)
            else:
                s.lines.append(line)
    d.sections.append(s)

    return d


def main():
    pass

def read_random():
    document = parse_file(open(expanduser('~/.db/wiki/readlist.md')))
    section = document.section_by_name('Unread')
    line = section.random_line()
    call(['br', line.url()])
    section.remove_line(line)
    readed = document.section_by_name('Readed')
    readed.append_line(line)

    notify('Прочитал ' + line.url())

    document.save()


def unread_last():
    document = parse_file(open(expanduser('~/.db/wiki/readlist.md')))
    readed = document.section_by_name('Readed')
    unread = document.section_by_name('Unread')

    line = readed.lines[-1]
    notify('Убрал ' + line.url())
    readed.remove_line(line)
    unread.append_line(line)

    document.save()

if __name__ == '__main__':
    if len(sys.argv) == 1:
        main()
    else:
        if sys.argv[1] == 'next':
            read_random()
        if sys.argv[1] == 'unread':
            unread_last()
