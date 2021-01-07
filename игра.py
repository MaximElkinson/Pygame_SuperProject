import pygame
import os
import sys
import random

pygame.init()
pygame.display.set_caption('Игра')
size = width, height = 1600, 800
screen = pygame.display.set_mode(size, pygame.FULLSCREEN)
pixel_size = height // 100
MAIN_FONT = pygame.font.Font("data/cool pixel font.ttf", 30)
mouse = False
mouseprev = False
click = False


def load_image(name, colorkey=None):
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


btnimg = load_image("кнопка.png")


def exit():
    pygame.quit()
    sys.exit()


def start():
    global screen
    global buttons
    del buttons[:]
    a = CutScene((0, 255, 0))
    a.add_fraze('adfs')
    a.add_fraze('bsfd')
    a.add_fraze('csdg')
    a.start(screen)


def in_rect(rect, xy):
    if rect[0] <= xy[0] < rect[0] + rect[2] and rect[1] <= xy[1] < rect[1] + rect[3]:
        return True
    return False


class Speech(pygame.sprite.Sprite):  # Я не помню, как это называется, но короче тут текст сидит
    def __init__(self, text, *group):
        super().__init__(*group)
        self.image = btnimg.copy()
        self.rect = pygame.Rect(pixel_size, height * 5 / 8, width - pixel_size,
                                height * 3 / 8 - pixel_size)
        self.text = text
        self.rate = 3
        self.step = 0

    def update(self, mpos, click):
        self.step += self.step < (len(self.text) - 1) * self.rate
        bltext = MAIN_FONT.render(self.text[self.step // self.rate], False, (0, 200, 0))
        self.image.blit(bltext, (pixel_size + MAIN_FONT.size(
            self.text[:self.step // self.rate + 1])[0], pixel_size))

    def set_text(self, text):
        self.image = btnimg.copy()
        self.text = text
        self.step = 0


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
        self.image = sprite
        self.rect = pygame.Rect(x, y, *self.image.get_size())
        self.image.blit(MAIN_FONT.render(self.text, False, tcolor),
                        ((self.rect.w - MAIN_FONT.size(text)[0]) / 2,
                         (self.rect.h - MAIN_FONT.get_height()) / 2))
        self.func = func

    def update(self, event, click):
        # Нажатие кнопки
        if event.type in [pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN] and \
                in_rect((self.rect.x, self.rect.y, *self.rect.size), event.pos) and click:
            self.func()


class Cut_Scean:
    def __init__(self, color, text=[]):
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
                        font = pygame.font.Font("cool pixel font.ttf", 30)
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
                if event1.type == pygame.MOUSEBUTTONUP:
                    running = False


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
        self.cut_sceans = [Cut_Scean((0, 255, 0), ['В данном тесте',
                                                   'мы проверим твою скорость обработки информации',
                                                   'Ты должен найти ,среди массива данных, файл',
                                                   'в котором есть слово "красный"',
                                                   'Попробуй уложиться в две милисекунды']),
                           Cut_Scean((0, 255, 0), ['Слишком медленно',
                                                   'Посмотрим что не так и попробуем сново']),
                           Cut_Scean((0, 255, 0), ['Ты ошибся',
                                                   'Посмотрим что не так и попробуем сново']),
                           Cut_Scean((0, 255, 0), ['Прекрасно',
                                                   'Ты справился. Идём дальше'])]
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
                    self.board[i][j] = (random.choice(range(155)),
                                        random.choice(range(255)),
                                        random.choice(range(255)))
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


def menu():
    global mouse_on_screen
    running = True
    # Инициализируем две кнопки
    buttons = pygame.sprite.Group()
    sprites = pygame.sprite.Group()
    Button(8, 8, btnimg.copy(), 'Играть', (0, 200, 0), exit, buttons, sprites)
    Button(8, 80, btnimg.copy(), 'Выход', (0, 200, 0), exit, buttons, sprites)
    # Теоретическое положение курсора
    # по умолчанию
    mouse_pos = (0, 0)
    mouse_on_screen = pygame.mouse.get_focused()
    clock = pygame.time.Clock()
    fps = 60
    while running:
        mouseprev = mouse
        mouse_on_screen = pygame.mouse.get_focused()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEMOTION:
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
        sprites.update(event, click)
        sprites.draw(screen)
        pygame.display.flip()
        clock.tick(fps)


if __name__ == '__main__':
    pygame.init()
    pygame.display.set_caption('Игра')
    size = width, height
    screen = pygame.display.set_mode(size)
    mouse_on_screen = None
    menu()
    pygame.quit()
