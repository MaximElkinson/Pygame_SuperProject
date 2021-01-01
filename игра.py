import pygame

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
    global running
    running = False


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


if __name__ == '__main__':
    pygame.display.set_caption('Игра')
    size = width, height
    screen = pygame.display.set_mode(size)

    running = True
    # Инициализируем две кнопки
    buttons = [Button(10, 10, 110, 30, 'Играть', (0, 0, 0), (0, 255, 0), exit),
               Button(10, 40, 110, 30, 'Выход', (0, 0, 0), (0, 255, 0), exit)]
    dialogue = Speech(200, text="It's me, SANS UNDERTALE", boundcolor=(0, 255, 0), textcolor=(0, 255, 0), reverse=True)
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
        for i in buttons:
            # Обновляем каждую кнопку
            i.render(mouse_pos)
        dialogue.render(mouse_pos)
        pygame.display.flip()
    pygame.quit()
