import pygame
import random

pygame.init()
width, height = 800, 400
MAIN_FONT = pygame.font.Font("cool pixel font.ttf", 30)
SPEECH_SOUND = pygame.mixer.Sound("voice_sans.wav")
DEFAULT_DESIGN = {  # Дизайн по умолчанию (ставятся именно эти параметры, если не указано иначе)
    "size": (50, 50),  # Размер
    "color": (0, 0, 0),  # Цвет области
    "boundaries": True,  # Есть ли границы
    "boundwidth": 2,  # Ширина границ (Общий размер остается неизменным)
    "boundcolor": (255, 255, 255),  # Цвет границ
    "dotext": False,  # Есть ли текст
    "text": "Тестовый текст",  # Собсна сам текст
    "textpos": (0, 0),  # Позиция текста ОТНОСИТЕЛЬНО ВНУТРЕННЕЙ ЧАСТИ ОБЪЕКТА
    "font": MAIN_FONT,  # Шрифт текста
    "boundtext": True,  # Равен ли цвет текста цвету границ  (если границы есть кншн)
    "textcolor": (255, 255, 255),  # Цвет текста
    "selectable": False,  # Меняется ли цвет объекта при наведении на него курсора
    "reverse": True,  # Если объект выделен, меняются ли основной и дополнительные цвета
    "color2": (255, 255, 255),  # Если reverse поставлен на False,
    "boundcolor2": (0, 0, 0),  # нужно выбрать кастомный цвет
    "textcolor2": (0, 0, 0)  # для каждой части
}


def exit():
    pygame.quit()


def start():
    global screen
    global buttons
    del buttons[:]
    a = Cut_Scean((0, 255, 0))
    a.add_fraze('adfs')
    a.add_fraze('bsfd')
    a.add_fraze('csdg')
    a.start(screen)


def in_rect(rect, xy):
    if rect[0] <= xy[0] < rect[0] + rect[2] and rect[1] <= xy[1] < rect[1] + rect[3]:
        return True
    return False


class RectDesign:
    # Класс, создающий кастомный дизайн
    def __init__(self, **struct):
        self.struct = DEFAULT_DESIGN
        self.change(**struct)

    def __getitem__(self, item):
        return self.struct[item]

    def change(self, **dstruct):
        self.struct = self.get_changed(**dstruct)

    def get_changed(self, **dstruct):
        ans = self.struct.copy()
        for i in dstruct.keys():
            if i in self.struct and type(self.struct[i]) == type(dstruct[i]):
                ans[i] = dstruct[i]
        return ans


class GameRect:
    # Дабы не копировать строки по миллиону раз на каждый класс, существует вотетот надкласс
    def __init__(self, x, y, design=None):
        # Считываем данные:
        if design is None:
            design = DEFAULT_DESIGN
        self.pos = (x, y)  # Позиция объекта
        self.design = design  # Дизайн объекта. Вкратце - все параметры, кроме позиции

    def change_design(self, **kwargs):  # Изменение дизайна объекта
        self.design.change(**kwargs)

    def get_rect(self):
        # Возвращаем все данные о положении и размере объекта
        return *self.pos, *self.design["size"]

    def set_rect(self, x, y, sx=None, sy=None):
        self.pos = (x, y)
        if sx is not None and sy is not None:
            self.change_design(size=(sx, sy))

    def render(self, mpos):  # Рисовка объекта
        x, y = self.pos  # Подготовка переменных координат и размеров для более гибкой работы
        w = self.design["boundwidth"]
        sx, sy = self.design["size"]

        selected = False  # Подготовка и предварительное изменение цветов
        color1 = self.design["color"]  # Основной цвет
        color2 = self.design["boundcolor"]  # Цвет рамки
        color3 = self.design["textcolor"]  # Цвет текста
        # Изменение цветов в случае наведения курсора
        if mouse_on_screen and self.design["selectable"] and \
                in_rect((*self.pos, *self.design["size"]), mpos):
            selected = True
            if self.design["reverse"]:
                color1, color3 = color2, color1
            else:
                color1 = self.design["color2"]
                color2 = self.design["boundcolor2"]
                color3 = self.design["textcolor2"]

        if self.design["boundaries"]:  # Зарисовка основной формы и рамок
            screen.fill(color2, (x, y, sx, sy))
            x += w
            y += w
            sx -= 2 * w
            sy -= 2 * w
        screen.fill(color1, (x, y, sx, sy))

        if self.design["dotext"]:  # Зарисовка текста
            if self.design["boundtext"] and not selected:
                color = color2
            else:
                color = color3
            text = self.design["font"].render(self.design["text"], False, color)
            x, y = self.design["textpos"]
            screen.blit(text, (x + self.pos[0] + w * self.design["boundaries"],
                               y + self.pos[1] + w * self.design["boundaries"]))


class Speech(GameRect):  # Я не помню, как эта штука называется, но короче тут текст сидит
    def __init__(self, y, speech=SPEECH_SOUND, *args, **kwargs):
        if len(args) == 1 and type(args[0]) == RectDesign and len(kwargs) == 0:
            super().__init__(0, height - y, args[0])
        elif len(args) == 1 and type(args[0]) == RectDesign and len(kwargs) > 0:
            super().__init__(0, height - y, args[0].get_changed(**kwargs))
        elif len(kwargs) > 0:
            super().__init__(0, height - y, RectDesign(**kwargs))
        else:
            super().__init__(0, height - y)
        self.change_design(selectable=False, size=(width, y), dotext=True)
        self.text = self.design["text"]
        self.rate = 130
        self.step = 0
        self.speech = speech

    def render(self, mpos):
        self.change_design(text=self.text[:self.step // self.rate])
        super().render(mpos)
        if self.step % self.rate == 0 and self.text[self.step // self.rate - 1] not in " ,.":
            self.speech.play()
        self.step += len(self.text) * self.rate + 1 > self.step

    def set_text(self, text):
        self.text = text
        self.step = 0


class Button(GameRect):
    # Поскольку в Pygame нет готовых кнопок, делаем их с помощю класса
    def __init__(self, x, y, sx, sy, text, color, bcolor, func):
        super().__init__(x, y, RectDesign(size=(sx, sy), color=color, boundcolor=bcolor))
        self.change_design(dotext=True, text=text, boundtext=True, selectable=True)
        self.func = func

    def push(self, mousepos):
        # Нажатие кнопки
        if in_rect((*self.pos, *self.design["size"]), mousepos):
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
            for event1 in pygame.event.get():
                if event1.type == pygame.QUIT:
                    running = False
                if event1.type == TIMEPRINT:
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
    buttons = [Button(10, 10, 110, 30, 'Играть', (0, 0, 0), (0, 255, 0), Reakcia),
               Button(10, 40, 110, 30, 'Выход', (0, 0, 0), (0, 255, 0), exit)]
    # dialogue = Speech(200, text="It's me, SANS UNDERTALE", boundcolor=(0, 255, 0), textcolor=(0, 255, 0), reverse=True)
    # Теоретическое положение курсора
    # по умолчанию
    mouse_pos = (0, 0)
    mouse_on_screen = pygame.mouse.get_focused()
    while running:
        mouse_on_screen = pygame.mouse.get_focused()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEMOTION:
                if mouse_pos != event.pos:
                    # Заносим положение курсора в переменную
                    mouse_pos = event.pos
            if event.type == pygame.MOUSEBUTTONUP:
                for i in buttons:
                    # Обновляем каждую кнопку
                    i.push(mouse_pos)
        screen.fill((0, 0, 0))
        for i in buttons:
            # Обновляем каждую кнопку
            i.render(mouse_pos)
        # dialogue.render(mouse_pos)
        pygame.display.flip()


if __name__ == '__main__':
    pygame.init()
    pygame.display.set_caption('Игра')
    size = width, height
    screen = pygame.display.set_mode(size)
    mouse_on_screen = None
    menu()
    pygame.quit()
