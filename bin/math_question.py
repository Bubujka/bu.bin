#!/usr/bin/env python3

from random import randint
from time import time

start = time()
a = randint(100,500)
b = randint(100,500)

answer = int(input("{} + {} = ?:".format(a, b)))

end = time()

if answer != a+b:
    print("Correct: {}".format(a+b))
    print('Ответ занял секунд: ', round(end - start, 1))
    exit(1)

print('Ответ занял секунд: ', round(end - start, 1))
