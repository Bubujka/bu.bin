"""
Вспомогательные методы для моих личных команд
"""

from os.path import expanduser
from subprocess import CalledProcessError, check_output, call
from subprocess import Popen, PIPE
import shlex

def read_file(pth):
    """
    Считать и вернуть содержимое файла
    """
    with open(expanduser(pth)) as file:
        return file.read()

def dmenu_file(file, label='Open'):
    """
    Прогнать файл через dmenu и получить результат
    """
    try:
        line = check_output("""
            cat {} | grep -v '^$' | ~/.bu.bin/bin/dmenu-wrapper {} 20
        """.format(file, shlex.quote(label)), shell=True)
        return line.decode('utf-8')
    except CalledProcessError:
        print(' =( ')

def dmenu_ask(label):
    """
    Спросить от человека строку текста
    """
    try:
        line = check_output("""
            echo | ~/.bu.bin/bin/dmenu-wrapper {} 20
        """.format(label), shell=True)
        return line.decode('utf-8').strip()
    except CalledProcessError:
        print(' =( ')

def dmenu_stdin(label, stdin, lines=20):
    """Получить вывод от dmenu, передав ему данные на вход"""
    proc = Popen([expanduser('~/.bu.bin/bin/dmenu-wrapper'), label, str(lines)],
                 stdout=PIPE,
                 stdin=PIPE,
                 stderr=PIPE)

    stdout_data = proc.communicate(input=stdin.encode('utf-8'))[0]
    return stdout_data.decode('utf-8').strip()

def open_in_browser(url):
    """
    Открыть ссылку в браузере
    """
    check_output(['br', url])

def open_i3_workspace(name):
    """
    Переключить рабочий стол в i3
    """
    check_output("i3-workspace {}".format(name), shell=True)

def copy_to_clipboard(what):
    """
    Скопировать что то в буфер обмена
    """
    call(['/home/bubujka/.bu.bin/bin/xc', what])
