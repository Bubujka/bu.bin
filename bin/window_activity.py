#!/usr/bin/env python3

from subprocess import check_output
from json import loads, dumps
from time import sleep
from datetime import datetime

INTERVAL=2
IDLE_LIMIT_SECONDS=120




def get_focused(tree):
    """Получить список активных нод"""
    l = []
    for node in tree['nodes'] + tree['floating_nodes']:
        for i in get_focused(node):
            l.append(i)
    if len(l):
        l.insert(0, tree)
    if tree['focused']:
        l.append(tree)
    return l

def get_line(line):
    """Получить представление"""
    if len(line) == 4:
        return line[3]['name']
    elif len(line) == 5:
        return "{} -> {} ({})".format(line[3]['name'],line[4]['window_properties']['instance'], line[4]['name'])

    else:
        return " -> ".join([str(t['name']) for t in line])

def idletime():
    return int(check_output('xprintidle').decode('utf-8').strip())

prev = None
is_idle = False
while True:
    out = loads(check_output(['i3-msg', '-t', 'get_tree']).decode('utf-8'))
    focused = get_focused(out)
    line = get_line(focused)
    if line != prev:
        prev = line
        print(datetime.now(), line)
    if idletime() > IDLE_LIMIT_SECONDS * 1000:
        if not is_idle:
            print(datetime.now(), "idle...")
            is_idle = True
    else:
        is_idle = False
    sleep(INTERVAL)

