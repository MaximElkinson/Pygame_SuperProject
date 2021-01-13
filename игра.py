import pygame
import os
import sys
import random
from functions import *
from constants import *

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


class CellGame:
    # создание поля
    def __init__(self):
        # значения по умолчанию
        # 1) Позиция по х
        # 2) Позиция по у
        # 3) Размер стороны клетки
        self.left = 10
        self.top = 10
        self.cell_size = 30

    # настройка внешнего вида
    def set_view(self, left, top, cell_size):
        # Новые значения
        # 1) Позиция по х
        # 2) Позиция по у
        # 3) Размер стороны клетки
        self.left = left
        self.top = top
        self.cell_size = cell_size

    def render(self):
        for y in range(self.height):
            for x in range(self.width):
                x1 = x * self.cell_size + self.left
                y1 = y * self.cell_size + self.top
                pygame.draw.rect(screen, pygame.Color(255, 255, 255),
                                 (x1, y1, self.cell_size, self.cell_size), 1)

        for y in range(self.height):
            for x in range(self.width):
                x1 = x * self.cell_size + self.left
                y1 = y * self.cell_size + self.top
                l = (self.cell_size - 2) / 2
                screen.fill(self.colors[self.board[y][x]],
                            (x1, y1), (x1 + l, y1 + l))

    def generate_new_map(self, width, height, colors):
        # Генерация нового поля
        # и установка доп. значений:
        # 1) Кол-во клеток по х
        # 2) Кол-во клеток по у
        # 3) Словарь индексов цветов
        self.width = width
        self.height = height
        self.colors = colors
        # 4) Генерация поля
        self.board = [[0] * width for _ in range(height)]

    def on_click(self, cell):
        # ===============ВНИМАНИЕ===============
        # ДАННАЯ ФУНКЦИЯ ДОЛЖНА ПЕРЕОПРЕДЕЛЯТЬСЯ
        # ======================================
        # Данная функция изменяет поля
        # после нажатия на мышь
        pass

    def get_cell(self, mouse_pos):
        # Получение координат клетки
        x = (mouse_pos[0] - self.left) // self.cell_size
        y = (mouse_pos[1] - self.top) // self.cell_size
        # Проверка клетки на нахождения на поле
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return None
        return x, y

    def get_click(self, mouse_pos):
        # Проверка клетки на нахождения на поле
        cell = self.get_cell(mouse_pos)
        if cell:
            self.on_click(cell)


class GameStage:  # Надкласс для стадий игры, чтобы не создавать кучу повторяющихся циклов
    def __init__(self):
        self.elements = []
        self.args = None
        self.nextstage = None
        self.active = True

    def update(self):  # Изначально пустая функция для обновления спрайтов и т.п.
        pass

    def transform(self, stage=None, *args):  # Функция для перехода с одной стадии к другой
        self.active = False
        for i in self.elements:
            i.kill()
        if stage is None:
            return
        self.nextstage = stage
        self.args = args


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
        if doskip and self.step < (len(self.normaltext)) * self.rates[self.phrase]:
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
        elif self.step < (len(self.normaltext)) * self.rates[self.phrase]:
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
                self.step == (len(self.normaltext)) * self.rates[self.phrase]:
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
                    ["Кароче это типа вступление.",
                     "Ты кампуктир, для тебя время",
                     "идет на порядки медленнее,",
                     "бла-бла-бла..."],
                    ["В общем, ща буит демка, смари:"]],
                   cutscene=True, rate=4, stay=True)
        ]

    def to_main_menu(self):
        self.transform(MainMenu)

    def demo(self):
        self.transform(Reakcia)

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


class ReakTile(pygame.sprite.Sprite):
    def __init__(self, xy, func):
        super().__init__(sprites)
        self.image = pygame.Surface((pixel_size * 8, pixel_size * 8))
        color = pygame.Color(random.randint(0, 160),
                             random.randint(100, 230),
                             random.randint(0, 160))
        self.image.fill(color)
        color.hsva = (color.hsva[0], min(color.hsva[1], 100),
                      max(color.hsva[2] - 30, 0), min(color.hsva[3], 100))
        self.image.fill(color, pygame.Rect(pixel_size, pixel_size, 6 * pixel_size, 6 * pixel_size))
        self.rect = pygame.Rect(*xy, pixel_size * 8, pixel_size * 8)
        self.func = func
        self.red = False

    def update(self, mpos, click, *args):
        if in_rect((self.rect.x, self.rect.y, *self.rect.size), mpos) and click:
            self.func()

    def change_func(self, func2):
        self.func = func2
        color = pygame.Color(255, 0, 0)
        self.image.fill(color)
        color = pygame.Color(200, 0, 0)
        self.image.fill(color, pygame.Rect(pixel_size, pixel_size, 6 * pixel_size, 6 * pixel_size))
        self.red = True

    def is_red(self):
        return self.red

    def change_color(self, color=None):
        if color is None:
            color = pygame.Color(random.randint(0, 160),
                                 random.randint(100, 230),
                                 random.randint(0, 160))
        self.image.fill(color)
        try:
            color.hsva = (color.hsva[0], min(color.hsva[1], 100),
                          max(color.hsva[2] - 30, 0), min(color.hsva[3], 100))
        except ValueError:
            print(color.hsva, color.hsva[2] - 30)
        self.image.fill(color, pygame.Rect(pixel_size, pixel_size, 6 * pixel_size, 6 * pixel_size))

    def blacknwhite(self):
        color = self.image.get_at((0, 0))
        color.hsva = [color.hsva[0], 0, color.hsva[2], color.hsva[3]]
        self.change_color(color)


class Reakcia(GameStage):
    def __init__(self, not_first=False):
        super().__init__()
        for i in range(10):
            for j in range(10):
                self.elements.append(ReakTile(((width - pixel_size * 80) // 2 +
                                               j * 8 * pixel_size,
                                               (height - pixel_size * 80) // 2 +
                                               i * 8 * pixel_size), self.error))
        self.timer = 61
        self.updatetiles = 0
        self.game_started = False
        self.stop = True
        if not not_first:
            self.elements.append(
                Speech([["Дарова кампуктир!",
                         "Сейчас ты буишь прахадить тест на реакцию!",
                         "Тебе нужно как можно быстрее найти и указать на красный квадрат.",
                         "Поторопись, у тебя есть лишь одна миллисекунда!"],
                        ["Ну все, начинай!"]], func=self.start)
            )
        else:
            self.start()

    def start(self):
        self.game_started = True
        self.stop = False
        for i in range(100):
            self.elements[i].change_color()
        self.elements[random.randrange(0, len(self.elements))].change_func(self.win)

    def update(self):
        self.updatetiles += 1
        if self.game_started:
            if not self.stop:
                self.timer -= 1
            if self.timer == 0:
                self.error([["А ты че думал, это на время игра!", "Попробуй еще разок."]])
            bltext = MAIN_FONT.render(str(round(self.timer / 60, 2)), False, (0, 200, 0))
            screen.blit(bltext, ((width - MAIN_FONT.size(str(round(self.timer / 60, 2)))[0]) // 2, 0))
            screen.blit(bltext, (0, 0))
        elif self.updatetiles % 20 == 0:
            for i in range(100):
                self.elements[i].change_color()

    def error(self, phrase=None):
        if not self.stop:
            self.stop = True
            for i in range(100):
                self.elements[i].blacknwhite()
            if phrase is None:
                phrase = [["Прамахнулся! Папробуй еще разок."]]
            self.elements.append(Speech(phrase, func=self.retry))

    def win(self):
        if not self.stop:
            self.stop = True
            self.elements.append(Speech([["Молодчинка!!!!", "США в шоке!!!!"],
                                         ["А терь вали атсюда."]],
                                        func=self.to_menu))

    def to_menu(self):
        self.transform(MainMenu)

    def retry(self):
        self.transform(Reakcia, True)


if __name__ == '__main__':
    running = True
    # Теоретическое положение курсора по умолчанию
    mouse_pos = (0, 0)
    clock = pygame.time.Clock()
    stage = MainMenu()
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
        sprites.update(mouse_pos, click, pygame.key.get_pressed())
        screen.fill((0, 0, 0))
        sprites.draw(screen)
        nextstage = stage.nextstage
        if nextstage is not None:
            stage = nextstage(*stage.args)
        stage.update()
        # screen.blit(load_image("sans.png", scale=pixel_size), (0, 0))
        pygame.display.flip()
        clock.tick(fps)
    pygame.quit()
