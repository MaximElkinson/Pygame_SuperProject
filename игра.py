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


class CutScene:
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
                if event.type == pygame.MOUSEBUTTONUP:
                    running = False


if __name__ == '__main__':

    running = True
    # Инициализируем две кнопки
    buttons = pygame.sprite.Group()
    sprites = pygame.sprite.Group()
    Button(8, 8, btnimg.copy(), 'Играть', (0, 200, 0), exit, buttons, sprites)
    Button(8, 80, btnimg.copy(), 'Выход', (0, 200, 0), exit, buttons, sprites)
    # dialogue = Speech("It's me, SANS UNDERTALE", sprites)
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
    pygame.quit()
