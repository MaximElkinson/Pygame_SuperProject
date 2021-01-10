import pygame
import os
import sys
import random
from lib.functions import *

settings = {
    "fullscreen": False
}
settings = set_settings(settings)
pygame.init()  # Основная инициализация, определеине размеров, создание констант
pygame.display.set_caption('Игра')
size = width, height = 1600, 800
if settings["fullscreen"]:
    screen = pygame.display.set_mode(size, pygame.FULLSCREEN)
else:
    screen = pygame.display.set_mode(size, pygame.RESIZABLE)
pixel_size = height // 800 * 8  # Игра пиксельная, поэтому определяется размер игрового пикселя
MAIN_FONT = pygame.font.Font("data/cool pixel font.ttf", pixel_size * 6)  # Основной шрифт
mouse = False  # Состояние нажатия мышкой
mouseprev = False  # Предыдущее состояние нажатия мышкой
click = False  # Кликнула ли мышка в данный игровой тик

# Инициализация основных групп спрайтов
buttons = pygame.sprite.Group()
sprites = pygame.sprite.Group()


def load_image(name, colorkey=None):  # Функция загрузки изображений из папки data
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
    if colorkey == -1:
        colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    image = pygame.transform.scale(
        image, (image.get_width() * pixel_size, image.get_height() * pixel_size))
    return image


btnimg = load_image("кнопка.png")  # Основной спрайт кнопки


def start():
    global screen
    global buttons
    del buttons[:]
    a = CutScene((0, 255, 0))
    a.add_fraze('adfs')
    a.add_fraze('bsfd')
    a.add_fraze('csdg')
    a.start(screen)


def in_rect(rect, xy):  # Функция проверки нахождения точки в прямоугольнике
    if rect[0] <= xy[0] < rect[0] + rect[2] and rect[1] <= xy[1] < rect[1] + rect[3]:
        return True
    return False


class GameStage:  # Надкласс для стадий игры, чтобы не создавать кучу повторяющихся циклов
    def __init__(self):
        self.elements = []
        self.active = True

    def update(self, *args):  # Изначально пустая функция для обновления спрайтов и т.п.
        pass

    def transform(self, Stage=None, *args):  # Функция для перехода с одной стадии к другой
        self.active = False
        for i in self.elements:
            i.kill()
        if Stage is None:
            del (self)
            return
        self = Stage(*args)


class Speech(pygame.sprite.Sprite):  # "Монологовое окно", отсюда приходит текст
    def __init__(self, text, *group, colorlib=None, func=None, cutscene=False, rate=3):
        super().__init__(*group)
        if colorlib is None:
            colorlib = {}
        if cutscene:
            self.image = pygame.Surface((width, height))
            self.rect = pygame.Rect(0, 0, width, height)
        else:
            self.image = load_image("dialogue.png")
            self.rect = pygame.Rect(pixel_size, pixel_size * 69, width - pixel_size,
                                    pixel_size * 30)
        # Далее - инициализация набора фраз разными способами
        if type(text) == str:
            self.fulltext = [text.rstrip().split("\n")]
        elif type(text[0]) == str:
            self.fulltext = [i.rstrip().split("\n") for i in text]
        else:
            self.fulltext = text
        self.text = self.fulltext[0]  # Текущая фраза
        if not cutscene:
            self.text[0] = '* ' + self.text[0]  # Просто по приколу
        self.normaltext = "".join(self.text)  # Фраза в виде одной строки
        self.colorlib = colorlib  # Если часть речи нужно выделить другим цветом, есть вотето
        self.maincolor = pygame.Color(0, 200, 0)  # Цвет речи
        self.phrase = 0  # Номер текущей фразы
        self.rate = rate  # Количество кадров для появления одного символа
        self.step = 0  # Шаг, грубо говоря, где "каретка" находится в тексте
        self.cutscene = cutscene  # Особый тип, на случай "кат-сцен"
        self.func = func  # Функция, запускающаяся после всех фраз
        if func is None:
            self.func = do_nothing()  # Заглушка, если ничего не нужно

    def update(self, mpos, click, keyboard):  # Функция для плавного появления текста и переходов
        doskip = click or keyboard[pygame.K_z] or keyboard[pygame.K_RETURN]  # Скипать ли текст
        # Изменение цвета в случае, если в colorlib записан другой
        if (self.phrase, self.step // self.rate) not in self.colorlib:
            color = self.maincolor
        else:
            color = self.colorlib[(self.phrase, self.step // self.rate)]
        # "Проматывание" текущего текста до конца, если лень смотреть анимацию
        if doskip and self.step < (len(self.normaltext)) * self.rate - 1:
            self.step = (len(self.normaltext) - 1) * self.rate
            bltext = [MAIN_FONT.render(i, False, color) for i in self.text]
            for i in range(len(bltext)):  # Цикл, потому что несколько строк
                self.image.blit(bltext[i], (
                    pixel_size * 4, pixel_size * 4 + MAIN_FONT.get_height() * i))
        elif doskip:  # Если текст уже доанимировался, нажатие запускает следующую фразу
            self.next_phrase()
        elif self.step < (len(self.normaltext)) * self.rate - 1:
            if self.step % self.rate == 0:
                # Если ничего не произошло, просто рендерим следующий символ
                bltext = MAIN_FONT.render(self.normaltext[self.step // self.rate], False, color)
                j = self.step // self.rate
                numline = 0
                for i in self.text:
                    if j >= len(i):
                        j -= len(i)
                        numline += 1
                    else:
                        break
                self.image.blit(bltext, (pixel_size * 4 + MAIN_FONT.size(
                    self.text[numline][:j])[0], pixel_size * 4 + MAIN_FONT.get_height() * numline))
            self.step += 1  # +1 шаг

    def set_text(self, text):  # Функция для переделки текста
        if self.cutscene:
            self.image = pygame.Surface((width, height))
        else:
            self.image = load_image("dialogue.png")
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
            self.kill()
        else:
            self.phrase += 1
            self.set_text(self.fulltext[self.phrase])


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
    def __init__(self, x, y, sprite, text, tcolor, func, *group):
        super().__init__(*group)
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


class CutScene:
    def __init__(self, color, text=None):
        if text is None:
            text = []
        self.frazes = text
        self.color = color

    def add_fraze(self, text):
        self.frazes.append(text)

    def start(self, screen):
        TIMEPRINT = pygame.USEREVENT + 1
        pygame.time.set_timer(TIMEPRINT, 300)
        screen.fill(pygame.Color(0, 0, 0))
        running = True
        x = 0
        y = 0
        s = 0
        l = 0
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == TIMEPRINT:
                    if s < len(self.frazes):
                        font = MAIN_FONT
                        text = font.render(self.frazes[s][l], True, self.color)
                        screen.blit(text, (x, y))
                        l += 1
                        x += 15
                        pygame.display.flip()
                        if l == len(self.frazes[s]):
                            s += 1
                            l = 0
                            x = 0
                            y += 30
                    else:
                        running = False
                if event.type == pygame.MOUSEBUTTONUP:
                    running = False


class MainMenu(GameStage):
    def __init__(self):
        super().__init__()
        btn = load_image("menubutton.png")
        self.elements = [Button((width - btn.get_width()) // 2,
                                (height - btn.get_height() * 3) // 2, btn.copy(),
                                "Попробовать демо", (0, 200, 0), self.play, buttons, sprites),
                         Button((width - btn.get_width()) // 2,
                                (height - btn.get_height() * 0) // 2, btn.copy(),
                                "Настройки", (0, 200, 0), self.settings, buttons, sprites),
                         Button((width - btn.get_width()) // 2,
                                (height + btn.get_height() * 3) // 2, btn.copy(),
                                "Выход", (0, 200, 0), exit, buttons, sprites)]

    def settings(self):
        self.transform(MainSettings)

    def play(self):
        self.transform(Intro)


class MainSettings(GameStage):
    def __init__(self):
        super().__init__()
        btn = load_image("menubutton.png")
        self.elements = [Button((width - btn.get_width()) // 2,
                                (height - btn.get_height() * 0) // 2, btn.copy(),
                                "Полный экран: " + "вкл" * settings["fullscreen"] +
                                "выкл" * (not settings["fullscreen"]), (0, 200, 0),
                                self.tgl_fullscreen, buttons, sprites),
                         Button((width - btn.get_width()) // 2,
                                (height + btn.get_height() * 3) // 2, btn.copy(),
                                "Готово", (0, 200, 0), self.savenback, buttons, sprites)]

    def tgl_fullscreen(self):
        settings["fullscreen"] = not settings["fullscreen"]
        if settings["fullscreen"]:
            pygame.display.set_mode(size, pygame.FULLSCREEN)
        else:
            pygame.display.toggle_fullscreen()
        self.elements[0].set_text("Полный экран: " + "вкл" * settings["fullscreen"] +
                                  "выкл" * (not settings["fullscreen"]))

    def savenback(self):
        save_settings(settings)
        self.transform(MainMenu)


class Intro(GameStage):
    def __init__(self):
        super().__init__()
        self.elements = [Speech([["Дарова."],
                                 ["Кароче это типа вступление, поэтому фона нету хыхя"],
                                 ["В общем, иди дорабатывай."]],
                                sprites, cutscene=True, rate=5, func=self.to_main_menu)]

    def to_main_menu(self):
        self.transform(MainMenu)


class Naperstki:
    def restart(self):
        self.boxes = []
        self.map = [0 for i in range(5)]
        col_vo = 2
        while col_vo != 0:
            index = random.choice(range(0, 4))
            if self.map[index] == 0:
                self.map[index] += col_vo
                col_vo -= 1
        for i in range(5):
            x = 10 * (i + 1)
            self.boxes.append(Button(x, 10, 110, 30, '', (0, 0, 0), (0, 255, 0), self.choise_boxes()))

    def choise_boxes(self):
        new_map = [0 for i in range(5)]
        col_vo = 2
        while col_vo != 0:
            index = random.choice(range(0, 4))
            if new_map[index] == 0 and self.map[index] == 0:
                new_map[index] += col_vo
                col_vo -= 1
        return new_map

    def add_eleps(self):
        clock = pygame.time.Clock()
        for j in range(1, 3):
            running = True
            eleps_x = 110 * (self.map.index(j) + 1) + 50
            print(self.map.index(j))
            eleps_y = 5
            while running:
                for event1 in pygame.event.get():
                    if event1.type == pygame.QUIT:
                        running = False
                pygame.draw.circle(screen, (0, 0, 0), (eleps_x, eleps_y - 5), 20)
                pygame.draw.circle(screen, (255, 0, 0), (eleps_x, eleps_y), 20)
                for i in self.boxes:
                    i.render((-1, -1))
                if eleps_y < 150:
                    eleps_y += 40 * clock.tick() / 1000
                else:
                    running = False
                pygame.display.flip()

    def render(self, new_map):
        for i in range(1, 3):
            running = True
            clock = pygame.time.Clock()
            box_a = self.map.index(i)
            box_b = new_map.index(i)
            pos_a = list(self.boxes[box_a].get_rect())
            pos_b = list(self.boxes[box_b].get_rect())
            finish = pos_b[0]
            x = (pos_b[0] - pos_a[0]) / 20
            while running:
                screen.fill((0, 0, 0))
                for event1 in pygame.event.get():
                    if event1.type == pygame.QUIT:
                        running = False
                for f in self.boxes:
                    f.render((-1, -1))
                if pos_a[1] > 0:
                    pos_a[1] -= 40 * clock.tick() / 1000
                    pos_b[1] -= 40 * clock.tick() / 1000
                    self.boxes[box_a].set_rect(*pos_a)
                    self.boxes[box_b].set_rect(*pos_b)
                else:
                    if pos_a[0] < finish:
                        pos_a[0] += x * clock.tick() / 500
                        pos_b[0] -= x * clock.tick() / 500
                        self.boxes[box_a].set_rect(*pos_a)
                        self.boxes[box_b].set_rect(*pos_b)
                    else:
                        if pos_a[1] < 120:
                            pos_a[1] += 40 * clock.tick() / 1000
                            pos_b[1] += 40 * clock.tick() / 1000
                            self.boxes[box_a].set_rect(*pos_a)
                            self.boxes[box_b].set_rect(*pos_b)
                        else:
                            self.boxes[box_a], self.boxes[box_b] = self.boxes[box_b], self.boxes[box_a]
                            running = False
                pygame.display.flip()

    def choise(self):
        pass

    def __init__(self):
        global screen
        screen.fill((0, 0, 0))
        self.restart()
        self.boxes = [Button(110 * (i + 1), 120, 110, 110, '', (0, 0, 0), (0, 255, 0), self.choise) for i in range(5)]
        pygame.display.flip()
        self.add_eleps()
        print(4)
        for i in range(5):
            self.render(self.choise_boxes())


class Reakcia:
    # создание поля
    def __init__(self):
        self.width = 5
        self.height = 5
        self.cut_sceans = [CutScene((0, 255, 0), ['В данном тесте',
                                                  'мы проверим твою скорость обработки информации.',
                                                  'Среди массива данных ты должен найти файл,',
                                                  'в котором есть слово "красный".',
                                                  'Попробуй уложиться в две миллисекунды.']),
                           CutScene((0, 255, 0), ['Слишком медленно!',
                                                  'Посмотрим что не так и попробуем снова.']),
                           CutScene((0, 255, 0), ['Ты ошибся!',
                                                  'Посмотрим что не так и попробуем снова.']),
                           CutScene((0, 255, 0), ['Прекрасно.',
                                                  'Ты справился. Идём дальше.'])]
        self.cut_sceans = [Speech(['В данном тесте',
                                   'мы проверим твою скорость обработки информации.',
                                   'Среди массива данных ты должен найти файл,',
                                   'в котором есть слово "красный".',
                                   'Попробуй уложиться в две миллисекунды.'], sprites),
                           Speech(['Слишком медленно!',
                                   'Посмотрим что не так и попробуем снова.'], sprites),
                           Speech(['Ты ошибся!',
                                   'Посмотрим что не так и попробуем снова.'], sprites),
                           Speech(['Прекрасно.',
                                   'Ты справился. Идём дальше.'], sprites)]
        # значения по умолчанию
        self.left = 10
        self.top = 10
        self.cell_size = 50
        res = 10
        i = 10
        self.cut_sceans[0].start(screen)
        while res != 0 and i != 4:
            for i in range(5):
                self.generate_map()
                res = self.level()
                if res != 3:
                    break
            self.cut_sceans[res].start(screen)

    def generate_map(self):
        self.pos = [random.choice(range(self.width)),
                    random.choice(range(self.height))]
        self.board = [[0] * width for _ in range(height)]
        for i in range(len(self.board)):
            for j in range(len(self.board[i])):
                if i != self.pos[1] or j != self.pos[0]:
                    self.board[i][j] = (random.randrange(155),
                                        random.randrange(255),
                                        random.randrange(255))
                else:
                    self.board[i][j] = (255, 0, 0)

    # настройка внешнего вида
    def set_view(self, left, top, cell_size):
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
                color = pygame.Color(*self.board[y][x])
                x1 = x * self.cell_size + self.left
                y1 = y * self.cell_size + self.top
                l = (self.cell_size - 2) / 2
                pygame.draw.rect(screen, color,
                                 pygame.Rect(x1 + 1, y1 + 1, self.cell_size - 2, self.cell_size - 2))

    def on_click(self, cell):
        if cell[0] == self.pos[0] and cell[1] == self.pos[1]:
            return True
        else:
            return False

    def get_cell(self, mouse_pos):
        x = (mouse_pos[0] - self.left) // self.cell_size
        y = (mouse_pos[1] - self.top) // self.cell_size
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return None
        return x, y

    def get_click(self, mouse_pos):
        cell = self.get_cell(mouse_pos)
        if cell:
            return self.on_click(cell)

    def level(self):
        TIMER = pygame.USEREVENT + 1
        pygame.time.set_timer(TIMER, 100)
        time = 1.50
        running = True
        res = False
        while running:
            for event_r in pygame.event.get():
                if event_r.type == pygame.QUIT:
                    running = False
                if event_r.type == pygame.MOUSEBUTTONUP:
                    if self.get_click(event_r.pos):
                        res = 3
                        running = False
                    else:
                        res = 2
                        running = False
                if event_r.type == TIMER:
                    if time > 0.1:
                        time -= 0.1
                    else:
                        res = 1
                        running = False
            screen.fill((0, 0, 0))
            self.render()
            font = pygame.font.Font(None, 50)
            text = font.render(str(time)[:3], True, (0, 255, 0))
            screen.blit(text, (300, 100))
            pygame.display.flip()
        return res


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
        sprites.update(mouse_pos, click, pygame.key.get_pressed())
        screen.fill((0, 0, 0))
        sprites.draw(screen)
        pygame.display.flip()
        clock.tick(fps)
    pygame.quit()
