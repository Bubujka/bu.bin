#!/usr/bin/env python3
"""Получить статистику за сегодня"""

import time
from itertools import groupby
from datetime import timedelta

from window_activity import log_reader


data = list(log_reader())
prev = None
for row in data:
    if prev is None:
        prev = row
        continue
    prev['duration'] = float(row['time']) - float(prev['time'])
    prev = row
prev['duration'] = time.time() - float(prev['time'])

def keyfn(itm):
    return itm['software']

data = sorted(data, key=keyfn)
grouped = groupby(data, key=keyfn)
humaned = []
for group, dat in grouped:
    dat = list(dat)
    seconds = int(sum([t['duration'] for t in dat]))
    humaned.append({'name': group, 'human': timedelta(seconds=seconds), 'seconds': seconds, 'data': dat})

for t in sorted(humaned, key=lambda t: t['seconds']):
    if t['name']:
        print(t['name'], t['human'])
        #for tt in t['data']:
        #    print('-', tt['title'])

