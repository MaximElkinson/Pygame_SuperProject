import pygame
import os
import sys
import random
from lib.functions import *
from lib.constants import *

settings = set_settings(defaultsettings)
pygame.init()  # Основная инициализация, определеине размеров, создание констант
pygame.display.set_caption('Игра')
if settings["fullscreen"]:
    screen = pygame.display.set_mode(psize, pygame.FULLSCREEN | pygame.SCALED)
else:
    screen = pygame.display.set_mode(psize)
size = width, height = screen.get_size()
pixel_size = height // 100
MAIN_FONT = pygame.font.Font("data/cool pixel font.ttf", pixel_size * 6)  # Основной шрифт
BIG_FONT = pygame.font.Font("data/cool pixel font.ttf", pixel_size * 8)  # Крупная версия

# Инициализация основных групп спрайтов
buttons = pygame.sprite.Group()
sprites = pygame.sprite.Group()


class GameStage:  # Надкласс для стадий игры, чтобы не создавать кучу повторяющихся циклов
    def __init__(self):
        self.elements = []
        self.nextstage = None
        self.active = True

    def update(self):  # Изначально пустая функция для обновления спрайтов и т.п.
        pass

    def transform(self, stage=None):  # Функция для перехода с одной стадии к другой
        self.active = False
        for i in self.elements:
            i.kill()
        if stage is None:
            return
        self.nextstage = stage


class MySprite(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.blimage = self.image

    def change_rgb(self, rgb):
        self.image.fill(rgb)


class Speech(pygame.sprite.Sprite):  # "Монологовое окно", отсюда приходит текст
    def __init__(self, text, colorlib=None, stay=False, func=do_nothing, cutscene=False,
                 rate=2, chars=None, rates=None):
        super().__init__(sprites)
        if colorlib is None:
            colorlib = {}
        # Далее - инициализация набора фраз разными способами
        if type(text) == str:
            self.fulltext = [text.rstrip().split("\n")]
        elif type(text[0]) == str:
            self.fulltext = [i.rstrip().split("\n") for i in text]
        else:
            self.fulltext = text
        self.text = self.fulltext[0]  # Текущая фраза
        # Картинки персонажей, если есть
        if chars is None:
            self.chars = [None for _ in range(len(self.fulltext))]
        else:
            self.chars = chars
        self.character = self.chars[0]
        if self.character is not None:
            self.charrect = self.character.get_rect()
            self.charrect.move(pixel_size * 4, pixel_size * 4)
        else:
            self.charrect = pygame.Rect(0, 0, 0, 0)
        if cutscene:
            self.image = pygame.Surface((width, height))
            self.rect = pygame.Rect(0, 0, width, height)
        else:
            self.image = load_image("dialogue.png", scale=pixel_size)
            if self.character is not None:
                self.image.blit(self.character, self.charrect)
            self.rect = pygame.Rect(pixel_size, height - self.image.get_height() - pixel_size * 1,
                                    width - pixel_size, self.image.get_height())
        if rates is None:
            self.rates = [rate for _ in range(len(self.fulltext))]
        else:
            self.rates = rates
        if not cutscene:
            self.text[0] = '* ' + self.text[0]  # Просто по приколу
        self.normaltext = "".join(self.text)  # Фраза в виде одной строки
        self.colorlib = colorlib  # Если часть речи нужно выделить другим цветом, есть вотето
        self.maincolor = pygame.Color(0, 200, 0)  # Цвет речи
        self.phrase = 0  # Номер текущей фразы
        self.step = 0  # Шаг, грубо говоря, где "каретка" находится в тексте
        self.cutscene = cutscene  # Особый тип, на случай "кат-сцен"
        self.func = func  # Функция, запускающаяся после всех фраз
        self.stay = stay  # Если включено, объект можно будет удалить только вручную
        if cutscene:
            self.font = BIG_FONT
        else:
            self.font = MAIN_FONT
        if func is None:
            self.func = do_nothing()  # Заглушка, если ничего не нужно

    def update(self, mpos, click, keyboard):  # Функция для плавного появления текста и переходов
        doskip = click or keyboard[pygame.K_z] or keyboard[pygame.K_RETURN]  # Скипать ли текст
        # Изменение цвета в случае, если в colorlib записан другой
        if (self.phrase, self.step // self.rates[self.phrase]) not in self.colorlib:
            color = self.maincolor
        else:
            color = self.colorlib[(self.phrase, self.step // self.rates[self.phrase])]
        # "Проматывание" текущего текста до конца, если лень смотреть анимацию
        if doskip and self.step < (len(self.normaltext)) * self.rates[self.phrase] - 1:
            self.step = (len(self.normaltext) - 1) * self.rates[self.phrase]
            bltext = [self.font.render(i, False, color) for i in self.text]
            for i in range(len(bltext)):  # Цикл, потому что несколько строк
                if self.cutscene:
                    x = (width - self.font.size(self.text[i])[0]) // 2
                else:
                    x = pixel_size * 4 + self.charrect.x + self.charrect.w
                self.image.blit(bltext[i], (
                    x, pixel_size * (4 + 20 * self.cutscene) + self.font.get_height() * i))
        elif doskip:  # Если текст уже доанимировался, нажатие запускает следующую фразу
            self.next_phrase()
        elif self.step < (len(self.normaltext)) * self.rates[self.phrase] - 1:
            if self.step % self.rates[self.phrase] == 0:
                # Если ничего не произошло, просто рендерим следующий символ
                bltext = self.font.render(
                    self.normaltext[self.step // self.rates[self.phrase]], False, color)
                j = self.step // self.rates[self.phrase]
                numline = 0
                for i in self.text:
                    if j >= len(i):
                        j -= len(i)
                        numline += 1
                    else:
                        break
                if self.cutscene:
                    x = (width - self.font.size(self.text[numline])[0]) // 2
                else:
                    x = pixel_size * 4 + self.charrect.x + self.charrect.w
                self.image.blit(bltext, (x + self.font.size(
                    self.text[numline][:j])[0], pixel_size * (4 + 20 * self.cutscene) +
                                         self.font.get_height() * numline))
            self.step += 1  # +1 шаг

    def set_text(self, text):  # Функция для переделки текста
        if self.cutscene:
            self.image = pygame.Surface((width, height))
        else:
            self.image = load_image("dialogue.png", scale=pixel_size)
            if self.character is not None:
                self.image.blit(self.character, self.charrect)
        if type(text) == str:
            self.text = text.rstrip().split("\n")
        else:
            self.text = text
        if not self.cutscene:
            self.text[0] = '* ' + self.text[0]
        self.normaltext = "".join(self.text)
        self.step = 0

    def next_phrase(self):  # Переход к следующей фразе
        if self.phrase >= len(self.fulltext) - 1:
            self.func()
            if not self.stay:
                self.kill()
        else:
            self.phrase += 1
            self.character = self.chars[self.phrase]
            if self.character is not None:
                self.charrect = self.character.get_rect()
                self.charrect = self.charrect.move(pixel_size * 4, pixel_size * 4)
            else:
                self.charrect = pygame.Rect(0, 0, 0, 0)
            self.set_text(self.fulltext[self.phrase])

    def is_complete(self):  # Если весь текст прокручен, то True
        if self.phrase == len(self.fulltext) - 1 and \
                self.step == (len(self.normaltext)) * self.rates[self.phrase] - 1:
            return True
        return False


class Tile(pygame.sprite.Sprite):
    def __init__(self, rect, *groups, life=1):
        super().__init__(*groups)
        self.image = pygame.Surface(rect[2:])
        self.rect = pygame.Rect(rect)
        self.life = life
        color = pygame.Color(0, 220, 0)
        color.hsva = ((color.hsva[0] + random.randint(-20, 20)) % 360, color.hsva[1],
                      random.randint(30, 70), color.hsva[3])
        pygame.draw.rect(self.image, color, (0, 0, rect[2], rect[3]))

    def collide(self):
        self.life -= 1
        if self.life == 0:
            self.kill()


class Ball(pygame.sprite.Sprite):
    def __init__(self):
        global sprites
        super().__init__(sprites)
        self.image = pygame.Surface(())


class HackingGame:
    def __init__(self, difficulty=1):
        self.tiles = pygame.sprite.Group()
        h = int(5 * 1.5 ** difficulty)
        w = int(6 * 1.5 ** difficulty)
        tsize = ((width - pixel_size * (w + 1)) // w, (height // 2 - pixel_size * (h + 1)) // h,
                 (width - pixel_size * (w + 2)) // (w + 1))
        for i in range(h):
            for j in range(w + (i % 2)):
                Tile((pixel_size + (tsize[2 * (i % 2)] + 8) * j, pixel_size + (tsize[1] + 8) * i,
                      tsize[2 * (i % 2)], tsize[1]), self.tiles, sprites)


class Button(pygame.sprite.Sprite):
    # Поскольку в Pygame нет готовых кнопок, делаем их с помощю класса
    def __init__(self, x, y, sprite, text, tcolor, func):
        super().__init__(buttons, sprites)
        self.text = text
        self.sprite = sprite
        self.image = self.sprite.copy()
        self.tcolor = tcolor
        self.rect = pygame.Rect(x, y, *self.image.get_size())
        self.image.blit(MAIN_FONT.render(self.text, False, tcolor),
                        ((self.rect.w - MAIN_FONT.size(text)[0]) / 2,
                         (self.rect.h - MAIN_FONT.get_height()) / 2))
        self.func = func

    def update(self, mpos, click, *args):
        # Нажатие кнопки
        if in_rect((self.rect.x, self.rect.y, *self.rect.size), mpos) and click:
            self.func()

    def set_text(self, text):
        self.text = text
        self.image = self.sprite.copy()
        self.image.blit(MAIN_FONT.render(self.text, False, self.tcolor),
                        ((self.rect.w - MAIN_FONT.size(text)[0]) / 2,
                         (self.rect.h - MAIN_FONT.get_height()) / 2))


class MainMenu(GameStage):  # Главное меню
    def __init__(self):
        super().__init__()
        btn = load_image("menubutton.png", scale=pixel_size)
        self.elements = [Button((width - btn.get_width()) // 2,
                                (height - btn.get_height() * 3) // 2, btn.copy(),
                                "Попробовать демо", (0, 200, 0), self.play),
                         Button((width - btn.get_width()) // 2,
                                (height - btn.get_height() * 0) // 2, btn.copy(),
                                "Настройки", (0, 200, 0), self.settings),
                         Button((width - btn.get_width()) // 2,
                                (height + btn.get_height() * 3) // 2, btn.copy(),
                                "Выход", (0, 200, 0), exit)]

    def settings(self):
        self.transform(MainSettings)

    def play(self):
        self.transform(Intro)


class MainSettings(GameStage):  # Настройки в главном меню. Их мало, но по приколу они есть
    def __init__(self):
        super().__init__()
        btn = load_image("menubutton.png", scale=pixel_size)
        self.elements = [Button((width - btn.get_width()) // 2,
                                (height - btn.get_height() * 0) // 2, btn.copy(),
                                "Полный экран: " + "вкл" * settings["fullscreen"] +
                                "выкл" * (not settings["fullscreen"]), (0, 200, 0),
                                self.tgl_fullscreen),
                         Button((width - btn.get_width()) // 2,
                                (height + btn.get_height() * 3) // 2, btn.copy(),
                                "Готово", (0, 200, 0), self.savenback)]

    def tgl_fullscreen(self):
        global size, width, height, pixel_size
        settings["fullscreen"] = not settings["fullscreen"]
        if settings["fullscreen"]:
            pygame.display.set_mode(psize, pygame.FULLSCREEN | pygame.SCALED)
            size = width, height = screen.get_size()
            pixel_size = height // 100
        else:
            pygame.display.toggle_fullscreen()
            size = width, height = psize
            pixel_size = ppixel_size
        self.elements[0].set_text("Полный экран: " + "вкл" * settings["fullscreen"] +
                                  "выкл" * (not settings["fullscreen"]))
        save_settings(settings)
        self.transform(MainSettings)

    def savenback(self):
        save_settings(settings)
        self.transform(MainMenu)


class Intro(GameStage):
    def __init__(self):
        super().__init__()
        self.funytimer = 20
        self.wasnt = True
        self.elements = [
            Speech([["Дарова."],
                    ["Кароче это типа вступление,", "поэтому фона нету хыхя"],
                    ["В общем, ща буит демка, смари:"]],
                   cutscene=True, rate=4, stay=True)
        ]

    def to_main_menu(self):
        self.transform(MainMenu)

    def demo(self):
        self.transform(Demo)

    def update(self, *args):
        if self.elements[0].is_complete() and self.wasnt:
            self.funytimer -= 1
        if self.funytimer == 0:
            btn = load_image("кнопка.png", scale=pixel_size)
            self.wasnt = False
            self.elements.append(Button((width - btn.get_width()) // 2,
                                        (height - btn.get_height()) // 2,
                                        btn, "нажми", (0, 200, 0), self.demo))


class Demo(GameStage):
    def __init__(self):
        super().__init__()
        self.elements = [
            Speech([["Ч е л о в е к ."],
                    ["Н е у ж е л и  т ы  н е  з н а е ш ь ,",
                     "к а к  в с т р е ч а т ь  н о в о г о", "п р и я т е л я ?"],
                    ["Я SANS from UNDERTALE УООО-"]],
                   rates=[4, 4, 2], chars=[
                    None, None, load_image("sans.png", scale=pixel_size)], func=exit)
        ]


if __name__ == '__main__':
    running = True
    # Теоретическое положение курсора по умолчанию
    mouse_pos = (0, 0)
    clock = pygame.time.Clock()
    stage = MainMenu()
    fps = 60
    while running:
        mouseprev = mouse
        mouse_on_screen = pygame.mouse.get_focused()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEMOTION and mouse_on_screen:
                # Заносим положение курсора в переменную
                mouse_pos = event.pos
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse = True
            if event.type == pygame.MOUSEBUTTONUP:
                mouse = False
        if not mouseprev and mouse:
            click = True
        else:
            click = False
        nextstage = stage.nextstage
        if nextstage is not None:
            del stage
            stage = nextstage()
        stage.update()
        sprites.update(mouse_pos, click, pygame.key.get_pressed())
        screen.fill((0, 0, 0))
        sprites.draw(screen)
        # screen.blit(load_image("sans.png", scale=pixel_size), (0, 0))
        pygame.display.flip()
        clock.tick(fps)
    pygame.quit()
