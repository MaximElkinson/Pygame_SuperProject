import random
from lib.functions import *

# d = datetime.now().strftime("%H:%M:%S %d-%m-%Y")

settings = set_file(defaultsettings, "settings.txt")
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


def exit():  # Удобная функция выхода из игры. Она не с остальными функциями,
    # потому что в ней так же происходит сохранение всех настроек
    save_file(settings, "settings.txt")
    pygame.quit()
    sys.exit()


class GameStage:  # Надкласс для стадий игры, чтобы не создавать кучу повторяющихся циклов
    def __init__(self):
        self.elements = []
        self.sprites = pygame.sprite.Group()
        self.args = None
        self.nextstage = None
        self.active = True

    def do_things(self, *args):  # "Истинное обновление". Update перопределяется, поэтому есть вотето
        if self.active:
            self.update()
            self.sprites.update(*args)
        self.sprites.draw(screen)

    def append(self, *objects):  # Функция добавления спрайта. Нужна,
        # Чтобы во время паузы спрайты не обновлялись
        for object in objects:
            object.remove(*object.groups())
            object.add(self.sprites)
            self.elements.append(object)

    def update(self):  # Изначально пустая функция для обновления спрайтов и т.п.
        pass

    def pause(self):
        self.active = False

    def unpause(self):
        self.active = True

    def toggle_pause(self):
        self.active = not self.active

    def transform(self, stage=None, *args):  # Функция для перехода с одной стадии к другой
        self.active = False
        for _ in range(len(self.elements)):
            self.elements[-1].kill()
            i = self.elements.pop()
            del i
        if stage is None:
            return
        self.nextstage = stage
        self.args = args


class Speech(pygame.sprite.Sprite):  # "Монологовое окно", отсюда приходит текст
    def __init__(self, text, colorlib=None, stay=False, func=do_nothing, cutscene=False,
                 rate=2, chars=None, rates=None, italic=False, italics=None):
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
            self.rect = pygame.Rect(0, height - self.image.get_height(),
                                    width, self.image.get_height())
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
        if func is None:
            self.func = do_nothing()  # Заглушка, если ничего не нужно
        else:
            self.func = func  # Функция, запускающаяся после всех фраз
        self.stay = stay  # Если включено, объект можно будет удалить только вручную
        if cutscene:  # Изменение шрифта в зависимости от типа Речи
            self.font = BIG_FONT
        else:
            self.font = MAIN_FONT
        if italic:  # Некоторые части могут быть курсивом - это типа мысли ИИ
            self.italics = [True for _ in range(len(self.fulltext))]
        elif italics is not None:
            self.italics = italics
        else:
            self.italics = [False for _ in range(len(self.fulltext))]

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
                    x = pixel_size * 6 + self.charrect.x + self.charrect.w
                self.image.blit(bltext[i], (
                    x, pixel_size * (5 + 20 * self.cutscene) + self.font.get_height() * i))
        elif doskip:  # Если текст уже доанимировался, нажатие запускает следующую фразу
            self.next_phrase()
        elif self.step < (len(self.normaltext)) * self.rates[self.phrase]:
            if self.step % self.rates[self.phrase] == 0:
                # Если ничего не произошло, просто рендерим следующий символ
                # А еще, если шрифт курсивный, то рендерим не символ, а всю фразу
                # ДО символа включительно
                j = self.step // self.rates[self.phrase]
                numline = 0
                for i in self.text:
                    if j >= len(i):
                        j -= len(i)
                        numline += 1
                    else:
                        break
                pizza = False
                if self.italics[self.phrase]:
                    pizza = True
                    self.font.set_italic(1)
                if pizza:
                    bltext = self.font.render(
                        self.text[numline][:j + 1], False, color)
                else:
                    bltext = self.font.render(
                        self.normaltext[self.step // self.rates[self.phrase]], False, color)
                if self.cutscene:
                    x = (width - self.font.size(self.text[numline])[0]) // 2
                else:
                    x = pixel_size * 6 + self.charrect.x + self.charrect.w
                self.image.blit(bltext, (x + self.font.size(
                    self.text[numline][:j])[0] * (not pizza),
                                         pixel_size * (5 + 20 * self.cutscene) +
                                         self.font.get_height() * numline))
            if self.italics[self.phrase]:
                self.font.set_italic(0)
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
                self.charrect = self.charrect.move(pixel_size * 5, pixel_size * 5)
            else:
                self.charrect = pygame.Rect(0, 0, 0, 0)
            self.set_text(self.fulltext[self.phrase])

    def is_complete(self):  # Если весь текст прокручен, то True
        if self.phrase == len(self.fulltext) - 1 and \
                self.step == (len(self.normaltext)) * self.rates[self.phrase]:
            return True
        return False


class Tile(pygame.sprite.Sprite):
    def __init__(self, rect, color, text=None, tcolor=None, func=do_nothing, suicide=False):
        super().__init__(sprites)
        self.image = pygame.Surface(rect[2:], pygame.SRCALPHA)
        self.rect = pygame.Rect(rect)
        self.image.fill(color)
        self.func = func
        self.suicide = suicide
        if text is None:
            self.text = [""]
        elif type(text) == str:
            self.text = text.split("\n")
        else:
            self.text = text
        if tcolor is None:
            self.tcolor = pygame.Color(0, 200, 0, 150)
        else:
            self.tcolor = tcolor
        for i in range(len(self.text)):
            bltext = MAIN_FONT.render(self.text[i], False, self.tcolor)
            self.image.blit(bltext, (pixel_size, pixel_size +
                                     (self.rect.height - pixel_size * 2) / len(self.text) * i))

    def update(self, mpos, click, *args):
        if in_rect(self.rect, mpos) and click:
            self.func()
            if self.suicide:
                self.kill()


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
        if settings["first"]:
            self.append(
                Tile(screen.get_rect(), (0, 0, 0, 0), [
                    "z или enter: выполнить/подтвердить",
                    "x или shift: пропустить/отменить",
                    "c или control: открытие меню"
                ], func=self.generate_menu, suicide=True)
            )
            settings["first"] = False
        else:
            self.generate_menu()

    def generate_menu(self):
        btn = load_image("menubutton.png", scale=pixel_size)
        self.append(Button((width - btn.get_width()) // 2,
                           (height - btn.get_height() * 3) // 2, btn.copy(),
                           "Попробовать демо", (0, 200, 0), self.play),
                    Button((width - btn.get_width()) // 2,
                           (height - btn.get_height() * 0) // 2, btn.copy(),
                           "Настройки", (0, 200, 0), self.settings),
                    Button((width - btn.get_width()) // 2,
                           (height + btn.get_height() * 3) // 2, btn.copy(),
                           "Выход", (0, 200, 0), exit))

    def settings(self):
        self.transform(MainSettings)

    def play(self):
        self.transform(Intro)


class MainSettings(GameStage):  # Настройки в главном меню. Их мало, но по приколу они есть
    def __init__(self):
        super().__init__()
        btn = load_image("menubutton.png", scale=pixel_size)
        self.append(Button((width - btn.get_width()) // 2,
                           (height - btn.get_height() * 0) // 2, btn.copy(),
                           "Полный экран: " + "вкл" * settings["fullscreen"] +
                           "выкл" * (not settings["fullscreen"]), (0, 200, 0),
                           self.tgl_fullscreen),
                    Button((width - btn.get_width()) // 2,
                           (height + btn.get_height() * 3) // 2, btn.copy(),
                           "Готово", (0, 200, 0), self.savenback))

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
        save_file(settings, "settings.txt")
        self.transform(MainSettings)

    def savenback(self):
        save_file(settings, "settings.txt")
        self.transform(MainMenu)


class Intro(GameStage):
    def __init__(self):
        super().__init__()
        self.funytimer = 40
        self.wasnt = True
        self.append(
            Speech([["Дисклеймер:",
                     "Текст еще не сделан, поэтому тут он",
                     "просто для заполнения пустоты."],
                    ["Так вот."],
                    ["Это типа вступление.",
                     "Ты компьютер, для тебя время",
                     "идет на порядки медленнее,",
                     "бла-бла-бла..."],
                    ["В общем, ща буит демка:"]],
                   cutscene=True, rate=3, stay=True)
        )

    def to_main_menu(self):
        self.transform(MainMenu)

    def demo(self):
        self.transform(Reakcia)

    def update(self, *args):
        if self.elements[0].is_complete() and self.wasnt:
            self.funytimer -= 1
        if self.funytimer == 0:
            btn = load_image("button.png", scale=pixel_size)
            self.wasnt = False
            self.append(Button((width - btn.get_width()) // 2,
                               (height - btn.get_height()) // 2,
                               btn, "нажми", (0, 200, 0), self.demo))


class Demo(GameStage):
    def __init__(self):
        super().__init__()
        self.append(
            Speech([["Ч е л о в е к ."],
                    ["Н е у ж е л и  т ы  н е  з н а е ш ь ,",
                     "к а к  в с т р е ч а т ь  н о в о г о", "п р и я т е л я ?"],
                    ["Я SANS from UNDERTALE УООО-"]],
                   rates=[4, 4, 2], chars=[
                    None, None, load_image("sans.png", scale=pixel_size)], func=exit)
        )


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


class Timer(pygame.sprite.Sprite):
    def __init__(self, x, y, seconds, color=(0, 200, 0), func=do_nothing(), stay=False):
        super().__init__()
        self.timer: float = seconds
        self.clock = pygame.time.Clock()
        self.func = func
        self.stay = stay
        self.color = color
        self.go = False
        bltext = MAIN_FONT.render(str(round(self.timer, 2)), False, color)
        p = pixel_size
        self.image = pygame.Surface((14 * p, 8 * p))
        self.image.fill((0, 0, 0))
        self.image.fill(color, pygame.Rect(p, p, 12 * p, 6 * p))
        self.image.fill((0, 0, 0), pygame.Rect(p * 2, p * 2, 10 * p, 4 * p))
        self.image.blit(bltext, (p * 2, p * 2))
        self.rect = pygame.Rect(x, y, *self.image.get_size())

    def update(self, *args):
        if self.go:
            time = self.clock.tick()
            self.timer -= time / 1000
            if self.timer <= 0:
                self.go = False
                self.timer = 0
                self.func()
                if not self.stay:
                    self.kill()
        bltext = MAIN_FONT.render(str(round(self.timer, 2)), False, self.color)
        p = pixel_size
        self.image = pygame.Surface((17 * p, 8 * p))
        self.image.fill((0, 0, 0))
        self.image.fill(self.color, pygame.Rect(p, p, 15 * p, 6 * p))
        self.image.fill((0, 0, 0), pygame.Rect(p * 2, p * 2, 13 * p, 4 * p))
        self.image.blit(bltext, (p * 2, p * 1))

    def start(self):
        self.go = True
        self.clock.tick()

    def stop(self):
        self.go = False

    def timeleft(self):
        return self.timer


class Reakcia(GameStage):
    def __init__(self, not_first=False):
        super().__init__()
        for i in range(10):
            for j in range(10):
                self.append(ReakTile(((width - pixel_size * 80) // 2 +
                                      j * 8 * pixel_size,
                                      (height - pixel_size * 80) // 2 +
                                      i * 8 * pixel_size), self.error))
        self.append(Timer(0, 0, 1, stay=True, func=self.time_error))
        self.updatetiles = 0
        self.game_started = False
        self.stop = True
        if not not_first:
            self.append(
                Speech([["Здарова кампудахтор!",
                         "Сейчас ты буишь проходить тест на реакцию!",
                         "Тебе нужно как можно быстрее тыкнуть",
                         "на красный квадрат. Поторопись, у тебя есть",
                         "лишь одна миллисекунда!"],
                        ["Ну все, начинай!"]], func=self.start)
            )
        else:
            self.start()

    def start(self):
        self.elements[100].start()
        self.game_started = True
        self.stop = False
        for i in range(100):
            self.elements[i].change_color()
        self.elements[random.randrange(100)].change_func(self.win)

    def update(self):
        self.updatetiles += 1
        if not self.game_started and self.updatetiles % 20 == 0:
            for i in range(100):
                self.elements[i].change_color()

    def time_error(self):
        phrase = [["Не тормози, это таки на время игра!", "Попробуй еще разок."]]
        self.error(phrase)

    def error(self, phrase=None):
        self.elements[100].stop()
        if not self.stop:
            self.stop = True
            for i in range(100):
                self.elements[i].blacknwhite()
            if phrase is None:
                phrase = [["Прамахнулся! Папробуй еще разок."]]
            self.append(Speech(phrase, func=self.retry))

    def win(self):
        self.elements[100].stop()
        if not self.stop:
            self.stop = True
            self.append(Speech([["Молодчинка!!!!"],
                                ["Хочешь попробовать еще раз?"]],
                               func=self.choice))

    def choice(self):
        btn = load_image("button.png", scale=pixel_size)
        self.append(
            Tile((width / 5, 0, width * 3 / 5, height), pygame.Color(100, 150, 100, 150))
        )
        self.append(
            Button((width - btn.get_width() * 3) / 2, height / 2, btn,
                   "Еще раз", (0, 200, 0), self.retry))
        self.append(
            Button((width + btn.get_width()) / 2, height / 2, btn,
                   "В меню", (0, 200, 0), self.to_menu)
        )

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
            if event.type == pygame.KEYDOWN and pygame.key.get_pressed()[pygame.K_SPACE]:
                stage.toggle_pause()
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
        stage.do_things(mouse_pos, click, pygame.key.get_pressed())
        # screen.blit(load_image("sans.png", scale=pixel_size), (0, 0))
        pygame.display.flip()
        clock.tick(fps)
    pygame.quit()
