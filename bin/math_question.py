#!/usr/bin/env python3
"""Команда для создания паузы у человека для 'подумать' """

from random import randint
from time import time

def main():
    """Спросить решение простого математического выражения"""
    start = time()
    var_a = randint(100, 500)
    var_b = randint(100, 500)

    answer = int(input("{} + {} = ?:".format(var_a, var_b)))

    end = time()

    if answer != var_a + var_b:
        print("Correct: {}".format(var_a + var_b))
        print('Ответ занял секунд: ', round(end - start, 1))
        exit(1)

    print('Ответ занял секунд: ', round(end - start, 1))

if __name__ == '__main__':
    main()
