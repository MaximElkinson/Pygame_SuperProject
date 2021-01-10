import pygame
import os
import sys


def exit():  # Удобная функция выхода из игры
    pygame.quit()
    sys.exit()


def do_nothing():  # Название говорит само за себя, функция-заглушка
    pass


def set_settings(settings):  # Функция для загрузки или создания файла с настройками
    if os.path.exists("settings.txt"):
        with open("settings.txt", "r", encoding="utf8") as f:
            for i in f.readlines():
                j = i.rstrip().split("\t")
                if j[0] in settings:
                    stg = j[1]
                    if stg in ("True", "False"):
                        stg = (stg == "True")
                    elif stg.isdigit():
                        stg = int(stg)
                    settings[j[0]] = stg
    else:
        save_settings(settings)
    return settings


def save_settings(settings):
    with open("settings.txt", "w", encoding="utf8") as f:
        for i in settings.keys():
            f.write(i + "\t" + str(settings[i]) + "\n")