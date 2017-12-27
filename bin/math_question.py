#!/usr/bin/env python3

from random import randint

a = randint(100,500)
b = randint(100,500)

answer = int(input("{} + {} = ?:".format(a, b)))

if answer != a+b:
    print("Correct: {}".format(a+b))
    exit(1)
