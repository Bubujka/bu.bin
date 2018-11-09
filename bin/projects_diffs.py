#!/usr/bin/env python3
"""Проверить разницу между файлами проектов"""

from os.path import expanduser, basename
from glob import glob
from pprint import pprint
import difflib

from pyexcel_ods import get_data

try:
    from colorama import Fore, Back, Style, init
    init()
except ImportError:  # fallback so that the imported classes always exist
    class ColorFallback():
        __getattr__ = lambda self, name: ''
    Fore = Back = Style = ColorFallback()

def color_diff(diff):
    for line in diff:
        if line.startswith('+'):
            yield Fore.GREEN + line + Fore.RESET
        elif line.startswith('-'):
            yield Fore.RED + line + Fore.RESET
        elif line.startswith('^'):
            yield Fore.BLUE + line + Fore.RESET
        else:
            yield line

class Project:
    def __init__(self, pth):
        self.pth = pth
        self.data = get_data(pth)

    def tabs(self):
        return self.data.keys()

    def name(self):
        return basename(self.pth).replace(".ods", '')

    def row(self, tab, num):
        return self.data[tab][num]

    def col(self, tab, col):
        return [t[col] for t in self.data[tab] if len(t) >= col]

    def cols(self, tab, cols):
        return [cols_as_str(t, cols) for t in self.data[tab] if len(t) > 0]

def cols_as_str(t, cols):
    r = []
    for i in cols:
        if i >= len(t):
            r.append("")
        else:
            r.append(t[i].replace("\n", " "))
    return "\t".join(r)



def files():
    return [t for t in glob(expanduser('~/.db/wiki/excel-prj/*.ods')) if 'tpl-prj.ods' not in t]

TPL = Project(expanduser("~/.db/wiki/excel-prj/tpl-prj.ods"))
PROJECTS = { basename(pth): Project(pth) for pth in files() }

def check_structure_tabs():
    """Проверка числа вкладок"""
    for _, p in PROJECTS.items():
        if p.tabs() != TPL.tabs():
            print('--------------------')
            print(p.name(), 'расходится c шаблоном по вкладкам')
            print('', '  файл:', ", ".join(p.tabs()))
            print('', 'шаблон:', ", ".join(TPL.tabs()))

def have_exact_rows(prj, tab, row):
    a = prj.row(tab, row)
    b = TPL.row(tab, row)
    if a != b:
        print()
        print('--------------------')
        print()
        print(prj.name(), 'расходится по строкам {}:{}'.format(tab,row))
        print("\n".join(color_diff(difflib.unified_diff(a,b, fromfile=prj.name(), tofile='tpl'))))

def have_exact_cols(prj, tab, cols):
    a = prj.cols(tab, cols)
    b = TPL.cols(tab, cols)
    if a != b:
        print()
        print('--------------------')
        print()
        print(prj.name(), 'расходится по колонкам {}:{}'.format(tab, cols))
        print("\n".join(color_diff(difflib.unified_diff(a,b, fromfile=prj.name(), tofile='tpl'))))


def check_structure():
    check_structure_tabs()
    for _, p in PROJECTS.items():
        have_exact_rows(p, 'models', 0)
        have_exact_rows(p, 'models', 1)
        for tab in ('mechanics', 'stages', 'questions', 'fixes'):
            have_exact_rows(p, tab, 0)


def check_stages():
    for _, p in PROJECTS.items():
        have_exact_cols(p, 'stages', [1,2])
        have_exact_cols(p, 'questions', [0, 1, 2, 3])

def main():
    check_structure()
    check_stages()

if __name__ == '__main__':
    main()
