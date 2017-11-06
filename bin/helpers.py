"""
Вспомогательные методы для моих личных команд
"""

from os.path import expanduser
from subprocess import CalledProcessError, check_output, call

def read_file(pth):
    """
    Считать и вернуть содержимое файла
    """
    with open(expanduser(pth)) as file:
        return file.read()

def dmenu_file(file):
    """
    Прогнать файл через dmenu и получить результат
    """
    try:
        line = check_output("""
            cat {} | grep -v '^$' | ~/.bu.bin/bin/dmenu-wrapper Open 20
        """.format(file), shell=True)
        return line.decode('utf-8')
    except CalledProcessError:
        print(' =( ')

def open_in_browser(url):
    """
    Открыть ссылку в браузере
    """
    check_output(['chromium-browser', url])

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
