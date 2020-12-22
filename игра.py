import pygame

pygame.init()
main_font = pygame.font.Font("cool pixel font.ttf", 30)


class Button:
    def __init__(self, pos_x, pos_y, size_x, size_y,
                 text="", color1=(0, 0, 0), color2=(255, 255, 255)):
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
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.size_x = size_x
        self.size_y = size_y
        self.text = text
        self.color1 = color1
        self.color2 = color2

    def updata(self, mouse_pos):
        color1 = self.color1
        color2 = self.color2
        # Если курсор на кнопке
        # то меняем её цвет
        if self.pos_x <= mouse_pos[0] <= self.pos_x + self.size_x and \
                self.pos_y <= mouse_pos[1] <= self.pos_y + self.size_y:
            color1, color2 = color2, color1
        # Отрисовываем кнопку
        screen.fill(pygame.Color(color1), pygame.Rect(self.pos_x, self.pos_y,
                                                      self.size_x, self.size_y))
        # Пишем текст на кнопке
        text = main_font.render(self.text, True, color2)
        screen.blit(text, (self.pos_x, self.pos_y))

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

    def push(self):
        # Нажатие кнопки
        pass


if __name__ == '__main__':
    pygame.display.set_caption('Игра')
    size = width, height = 800, 400
    screen = pygame.display.set_mode(size, pygame.RESIZABLE)

    running = True
    # Инициализируем две кнопки
    buttons = [Button(10, 10, 100, 25, 'Играть', (0, 0, 0), (0, 255, 0)),
               Button(10, 35, 100, 25, 'Выход', (0, 0, 0), (0, 255, 0))]
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
        for i in buttons:
            # Обновляем каждую кнопку
            i.updata(mouse_pos)
        pygame.display.flip()
    pygame.quit()
