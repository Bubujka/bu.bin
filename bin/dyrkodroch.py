#!/usr/bin/env python3
#---
#title: Включать-выключать интерфейс на микротике, пока он не заработает на 100 мбитах
#tags: [mikrotik]
#refs: []
#---

from subprocess import check_output
from time import sleep

def interface_down():
    return 'ether1-gateway' in check_output(['ssh',
        'mikrotik-office',
        '/interface ethernet print where name=ether1-gateway disabled=yes']).decode('utf8')

def enable_interface():
    print('Включаю интерфейс')
    check_output(['ssh', 'mikrotik-office', '/interface ethernet enable ether1-gateway'])

def disable_interface():
    print('Выключаю интерфейс')
    check_output(['ssh', 'mikrotik-office', '/interface ethernet disable ether1-gateway'])


def rate():
    return check_output(['ssh', 'mikrotik-office', ':put ([/interface ethernet monitor ether1-gateway  once as-value ]->"rate")']).decode('utf-8').strip()

def wait(count):
    print("Жду {} секунд".format(count), end='')
    for i in range(1, count):
        print('.', end='', flush=True)
        sleep(1)
    print();


def ether_get(what):
    return check_output(['ssh', 'mikrotik-office', ':put ([/interface ethernet monitor ether1-gateway  once as-value ]->"{}")'.format(what)]).decode('utf-8').strip()

def good_connection():
    return ((ether_get('rate') == '100Mbps') and
            (ether_get('auto-negotiation') == 'done') and
            (ether_get('status') == 'link-ok'))

def stable_good_connection():
    stable_connection = True
    for i in range(1, 4):
        if not good_connection():
            print("Интернет не на 100 мбитах (или вообще не подключился)")
            stable_connection = False
        else:
            print("Инет нормальный ...", i)
        wait(5)
    return stable_connection

def restart_connection():
    disable_interface()
    enable_interface()


def main():
    if interface_down():
        print("Порт был выключен, включаю...")
        enable_interface()
        return

    if stable_good_connection():
        print("Всё хорошо с интернетом. Нечего больше делать")
        exit()

    restart_connection()
    wait(40)


if __name__ == '__main__':
    while True:
        main()

