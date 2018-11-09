#!/usr/bin/env python3

from os.path import expanduser
import dateutil.parser
import datetime

def main():
    d = open(expanduser("~/.db/alive.log")).read().splitlines()
    prev = None
    for dat in d:
        current = dateutil.parser.parse(dat)
        if prev:
            diff = current - prev
            print(diff.total_seconds())
            #help(diff)
            exit(1)
            print(dat, current - prev)
        prev = current
if __name__ == '__main__':
    main()
