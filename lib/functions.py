import pygame
import os
import sys
from lib.constants import *

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


def load_image(name, colorkey=None, fillcolor=None, scale=1):  # Функция загрузки изображений из папки data
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if fillcolor is not None:
        image.fill(fillcolor, special_flags=pygame.BLEND_MULT)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    image = pygame.transform.scale(
        image, (image.get_width() * scale, image.get_height() * scale))
    return image


def in_rect(rect, xy):  # Функция проверки нахождения точки в прямоугольнике
    if rect[0] <= xy[0] < rect[0] + rect[2] and rect[1] <= xy[1] < rect[1] + rect[3]:
        return True
    return False