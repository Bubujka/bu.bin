#!/usr/bin/env python3
"""
Запускалка сайтов через dmenu
"""

import sys
import urllib.parse
from subprocess import check_output
from os.path import expanduser

import helpers

DEFAULT_FILES = ["~/.sites", "~/.sites-private"]

def rebuild_combined():
    """
    Пересоздание общего файла
    """
    with open(expanduser("~/.sites-combined"), "w") as file:
        text = check_output("md-to-links ~/.db/prj/websites/my/links.md", shell=True)
        file.write("\n".join(helpers.read_file(f) for f in DEFAULT_FILES))
        file.write(text.decode('utf-8'))

def filename():
    """
    Получить имя файла, с которого ссылки берём
    """
    if len(sys.argv) > 1:
        return sys.argv[1]

    rebuild_combined()
    return "~/.sites-combined"

def extract_url(line):
    """
    Из строки вытащить url
    """
    return line.split(' ')[-1].strip()

def do_work():
    """
    Сделать всё
    """
    line = helpers.dmenu_file(filename())
    if line:
        url = extract_url(line)
        if "%s" in url:
            url = url.replace("%s", urllib.parse.quote(helpers.dmenu_ask('Value')))
        helpers.open_in_browser(url)
        helpers.open_i3_workspace('www')

if __name__ == '__main__':
    do_work()
