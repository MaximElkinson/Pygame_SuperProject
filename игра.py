import pygame

pygame.init()
MAIN_FONT = pygame.font.Font("cool pixel font.ttf", 30)


def exit():
    pygame.quit()


def start():
    global screen
    global buttons
    del buttons[:]
    a = Cut_Scean((0, 255, 0))
    a.add_fraze('a')
    a.add_fraze('b')
    a.add_fraze('c')
    a.start(screen)


class Button:
    def __init__(self, pos_x, pos_y, size_x, size_y, text, color1, color2, func):
        # По скольку в пайгейм нет готовых кнопок
        # то делаем их с помощю класса
        # Считываем данные:
        # 1) Позиция по горизонтали
        # 2) Позиция по вертикали
        # 3) Размер по горизонтали
        # 4) Размер по вертикали
        # 5) Текст на кнопке
        # 6) Цвет кнопки
        # 7) Цвет текста
        # 8) Функция кнопки
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.size_x = size_x
        self.size_y = size_y
        self.text = text
        self.color1 = color1
        self.color2 = color2
        self.func = func

    def updata(self, mouse_pos):
        color1 = self.color1
        color2 = self.color2
        # Если курсор на кнопке
        # то меняем её цвет
        if self.pos_x <= mouse_pos[0] and self.pos_x + self.size_x > mouse_pos[0]:
            if self.pos_y <= mouse_pos[1] and self.pos_y + self.size_y > mouse_pos[1]:
                color1 = self.color2
                color2 = self.color1
        # Отрисовываем кнопку
        screen.fill(pygame.Color(color1[0], color1[1], color1[2]), pygame.Rect(self.pos_x, self.pos_y,
                                                                               self.pos_x + self.size_x,
                                                                               self.pos_y + self.size_y))
        # Пишем текст на кнопке
        text = MAIN_FONT.render(self.text, True, color2)
        screen.blit(text, (self.pos_x + 5, self.pos_y))

    def get_pos(self):
        # Возвращаем все данные
        # о положении и размере кнопки
        return (self.pos_x, self.pos_y, self.size_x, self.size_y)

    def set_pos(self, x, y, sx=None, sy=None):
        self.pos_x = x
        self.pos_y = y
        if sx is not None and sy is not None:
            self.size_x = sx
            self.size_y = sy

    def push(self, mouse_pos):
        # Нажатие кнопки
        if self.pos_x < mouse_pos[0] and self.pos_x + self.size_x > mouse_pos[0]:
            if self.pos_y < mouse_pos[1] and self.pos_y + self.size_y > mouse_pos[1]:
                self.func()


class Cut_Scean:
    def __init__(self, color):
        self.frazes = []
        self.color = color

    def add_fraze(self, text):
        self.frazes.append(text)

    def start(self, screen):
        TIMEPRINT = pygame.USEREVENT + 1
        pygame.time.set_timer(TIMEPRINT, 1000)
        screen.fill(pygame.Color(0, 0, 0))
        running = True
        y = 0
        s = 0
        while running:
            for event1 in pygame.event.get():
                if event1.type == pygame.QUIT:
                    running = False
                if event1.type == TIMEPRINT:
                    font = pygame.font.Font("cool pixel font.ttf", 30)
                    text = font.render(self.frazes[s], True, self.color)
                    screen.blit(text, (0, y))
                    s += 1
                    y += 30
                    pygame.display.flip()
                    if s == len(self.frazes):
                        running = False


if __name__ == '__main__':
    pygame.init()
    pygame.display.set_caption('Игра')
    size = width, height = 800, 400
    screen = pygame.display.set_mode(size)

    running = True
    # Инициализируем две кнопки
    buttons = [Button(10, 10, 100, 25, 'Играть', (0, 0, 0), (0, 255, 0), start),
               Button(10, 35, 100, 15, 'Выход', (0, 0, 0), (0, 255, 0), exit)]
    # Теоретическое положение курсора
    # по умолчанию
    mouse_pos = (0, 0)
    while running:
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
            i.updata(mouse_pos)
        pygame.display.flip()
    pygame.quit()