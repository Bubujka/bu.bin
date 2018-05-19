#!/usr/bin/env python3
"""Напечатать список проектов, по которым не определены дальнейшие действия в taskwarrior"""

from os.path import expanduser
from subprocess import check_output

from pyexcel_ods import get_data

DATA = get_data(expanduser("~/.db/wiki/excel/prj.ods"))

def check_learning():
    """Проверить все направления изучения"""
    for [code, _type, desc, *_] in DATA['Learning'][1:]:
        if _type != 'Книга':
            have = have_tasks(code)
            if not have:
                print("task add project:"+code)

class PrjRow():
    """Проект личный, по работе"""
    def __init__(self, row):
        self.row = row

    def have_data(self):
        """Есть ли данные в строке"""
        return len(self.row) > 0

    def finished(self):
        """Закончен ли проект"""
        if self.completed() != "":
            return True
        return False

    def completed(self):
        """Дата завершения проекта"""
        try:
            return self.row[3]
        except IndexError:
            return ''


    def code(self):
        """Код проекта"""
        return self.row[0]

    def desc(self):
        """Описание проекта"""
        return self.row[1]


def check_prj(prj):
    """Проверить вкладку проекта"""
    for row in [PrjRow(t) for t in DATA[prj][1:]]:
        if row.have_data():
            if not row.finished():
                if not have_tasks(row.code()):
                    print("task add", ("project:"+row.code()).ljust(50), '   # '+row.desc())

def have_tasks(prj):
    """Проверить есть ли задачи по проекту"""
    return check_output(['task', 'project:{}'.format(prj), 'count']).decode('utf-8').strip() != '0'

def main():
    """Проверить все проекты"""
    print("Нужно придумать задачи по следующим проектам")
    check_learning()
    check_prj('Personal')
    check_prj('Beta')

if __name__ == '__main__':
    main()
