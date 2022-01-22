#!/usr/bin/env python3
#---
#title: Глобальная чистка на компьютере
#tags: [workspace, cleanup]
#refs: []
#---

"""Глобальная чистка на компьютере"""

from glob import glob
from os.path import expanduser, basename, dirname, exists, isdir, islink
from subprocess import check_output
import shlex
from multiprocessing import Pool
import yaml

OK_CODE = "✓"
FAIL_CODE = "✗"

HOME_WHITELISTED = ("_", "mnt", "venv", 'Рабочий стол')

IGNORE_WIKI_INDEX = ("prj/", "letters/", "logbook/", "contacts/", ".snippet.md")

IGNORE_WIKI_TITLE = (
    "plan.md",
    "meme.md",
    "learning-links.md",
    "gallery.md",
    "search-engines.md",
    "tasklists.md",
    "noproxy.md",
    "gtk-bookmarks.md",
)

IGNORE_MISSED_README = (
    "laravel",
)

STATE = {"errors": 0}


def add_error():
    """Увеличить число ошибок"""
    STATE["errors"] += 1


def list_print(items):
    """Напечатать список строк """
    print(*[" - " + t for t in items], sep="\n")


def bool_to_code(var):
    """Превратить True/False в красивую иконку"""
    if var:
        return OK_CODE
    return FAIL_CODE


def fail_print(msg):
    """Напечатать сообщение об ошибке"""
    print(bool_to_code(False), msg)


def ok_print(msg):
    """Напечатать сообщение об успехе"""
    print(bool_to_code(True), msg)


def check_directory_empty(directory, whitelisted=()):
    """Проверить что в каталоге чисто"""
    all_files = [basename(f) for f in glob(directory + "/*")]
    files = [f for f in all_files if f not in whitelisted]
    if files:
        fail_print("В каталоге '{}' есть мусор".format(directory))
        list_print(files)
        add_error()


def reps():
    """Список каталогов где репы есть"""
    dirs = (
        check_output(
            [
                "find",
                expanduser("~/.password-store"),
                expanduser("~/.db"),
                expanduser("~/.bu.bin"),
                "-type",
                "d",
                "-name",
                ".git",
            ]
        )
        .decode("utf-8")
        .splitlines()
    )
    return [dirname(f) for f in dirs]


class RepStatus:
    """Статус проверки репозитория"""

    def __init__(self, pth):
        self.pth = pth
        self.exists = None

        self.have_origin = None
        self.commited = None
        self.pushed = None

        self.run_checks()

    def is_ok(self):
        """Всё ли хорошо с репозиторием"""
        return self.exists and self.have_origin and self.commited and self.pushed

    def bash(self, cmd):
        """Выполнить команду внутри репозитория"""
        full_cmd = ("cd {}; " + cmd).format(shlex.quote(self.pth))
        return check_output(full_cmd, shell=True).decode("utf-8").strip()

    def run_checks(self):
        """Проверить репозиторий на чистоту"""

        if not exists(self.pth):
            self.exists = False
            return
        else:
            self.exists = True
        if self.bash("git status --porcelain") == "":
            self.commited = True

        if self.bash("""cat .git/config | grep 'remote "origin"' | wc -l""") == "0":
            self.have_origin = False
        else:
            self.have_origin = True

        self.pushed = self.bash("""git log --branches --not --remotes | wc -l""") == "0"


def check_rep_clean_and_pushed(pth):
    """Проверить что репозиторий чист и запушен"""
    return RepStatus(pth)


def check_all_reps_pushed():
    """Проверить что все репозитории запушены"""
    with Pool() as pool:
        for repstat in pool.map(check_rep_clean_and_pushed, reps()):
            if not repstat.is_ok():
                add_error()
                print(bool_to_code(repstat.is_ok()), repstat.pth)
                print(" have origin", bool_to_code(repstat.have_origin))
                print(" commited", bool_to_code(repstat.commited))
                print(" pushed", bool_to_code(repstat.pushed))


def must_be_indexed(pth):
    """Надо ли вообще индексировать этот файл в wiki?"""
    for ptrn in IGNORE_WIKI_INDEX:
        if ptrn in pth:
            return False
    return True


def check_wiki_indexed():
    """Проверить что вики проиндексирована"""
    index = open(expanduser("~/.db/wiki/index.md")).read()
    files = [
        f.replace(expanduser("~/.db/wiki/"), "")
        for f in glob(expanduser("~/.db/wiki/**/*.md"), recursive=True)
    ]

    not_found = [f for f in files if must_be_indexed(f) and f not in index]
    if not_found:
        fail_print("Не все файлы в вики проиндексированы")
        list_print(not_found)
        add_error()


def check_db_indexed():
    """Проверить что все каталоги в db проиндексированы"""
    index = open(expanduser("~/.db/wiki/index.md")).read()

    files = [basename(f) for f in glob(expanduser("~/.db/*"))]

    not_found = [f for f in files if f not in index]
    if not_found:
        fail_print("Не все папки в ~/.db проиндексированы")
        list_print(not_found)
        add_error()


def check_all_on_git():
    """Проверить что все проекты под гитом"""
    for root_dir in ("beta", "prj", "warpa", "omega"):
        contents = glob(expanduser("~/.db/{}/*".format(root_dir)))
        for something in contents:
            if '_files' in something:
                continue
            if '_bin' in something:
                continue
            if islink(something):
                continue
            if not isdir(something):
                fail_print("Что-то не то в каталоге лежит '{}'".format(something))
                add_error()
                continue
            if not exists(something + "/.git"):
                fail_print("Каталог '{}' не под git".format(something))
                add_error()


def check_files_indexed():
    """Проверить что все статичные файлы проиндексированы"""

    with open(expanduser("~/.db/wiki/static-files.md")) as tfile:
        txt = tfile.read()
        for directory in glob(expanduser("~/.db/files/*")):
            if isdir(directory):
                if basename(directory) not in txt:
                    fail_print("Каталог {} не проиндексирован".format(directory))


def have_yfm(pth):
    """Проверить есть ли yfm секция в файле"""
    content = open(pth).readline()
    if content[:3] == '---':
        return True
    return False


def extractyfm(pth):
    """Достать yfm из файла"""
    t = open(pth).readlines()
    c = ""
    for line in t[1:]:
        if '---' in line:
            return yaml.safe_load(c)
        c = c + line

def have_title_in_yfm(pth):
    if 'title' in extractyfm(pth):
        return True
    return False

def have_markdown_title(pth):
    """Есть ли у файла заголовок в начале файла"""
    content = open(pth).readline()
    if have_yfm(pth):
        if have_title_in_yfm(pth):
            return True
        return False
    if content[:2] == "# ":
        return True
    return False


def check_wiki_have_title():
    """Проверить что все файлы в вики имеют заголовок"""
    files = glob(expanduser("~/.db/wiki/*.md"))
    not_found = [
        f
        for f in files
        if not have_markdown_title(f) and basename(f) not in IGNORE_WIKI_TITLE
    ]
    if not_found:
        fail_print("Файлы не содержат заголовки")
        list_print(not_found)
        add_error()


def check_read_clean():
    """Проверить что нет файлов на чтение"""
    files = glob(expanduser("~/.db/read/**/*.*"), recursive=True)
    if files:
        fail_print("Есть файлы для чтения")
        list_print([t.replace(expanduser("~/.db/"), "@") for t in files])
        add_error()

def check_each_project_have_readme():
    """Проверить что каждый проект содержит readme"""
    errors = []
    for root_dir in ("beta", "prj", "omega"):
        files = glob(expanduser("~/.db/{}/*".format(root_dir)))
        for file in files:
            if not islink(file):
                if not exists(file+'/README.md'):
                    if basename(file) not in IGNORE_MISSED_README:
                        errors.append(file)
    if errors:
        fail_print("У проектов нет README.md файла")
        list_print([t.replace(expanduser("~/.db/"), "@") for t in sorted(errors)])
        add_error()


def main():
    """Произвести проверку системы на чистоту"""
    #check_read_clean()
    #check_each_project_have_readme()
    check_wiki_have_title()
    check_directory_empty(expanduser("~"), whitelisted=HOME_WHITELISTED)
    check_directory_empty(expanduser("~/_"))
    #check_files_indexed() # Переделать
    check_all_on_git()
    #check_wiki_indexed()
    check_db_indexed()
    check_all_reps_pushed()
    exit(min(1, STATE["errors"]))


if __name__ == "__main__":
    main()
