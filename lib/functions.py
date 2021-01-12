import pygame
import os
import sys
from lib.constants import *


def do_nothing():  # Название говорит само за себя, функция-заглушка
    pass


def set_file(file, path):
    if os.path.exists(path):
        fl = False
        with open(path, "r", encoding="utf8") as f:
            for i in f.readlines():
                j = i.rstrip().split("\t")
                if j[0] in file:
                    stg = j[1]
                    if stg in ("True", "False"):
                        stg = (stg == "True")
                    elif stg.isdigit():
                        stg = int(stg)
                    file[j[0]] = stg
    save_file(file, path)
    return file



def save_file(file, path):
    with open(path, "w", encoding="utf8") as f:
        for i in file.keys():
            f.write(i + "\t" + str(file[i]) + "\n")


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
    rect = pygame.Rect(rect)
    if rect[0] <= xy[0] < rect[0] + rect[2] and rect[1] <= xy[1] < rect[1] + rect[3]:
        return True
    return False