import random
from datetime import datetime
from lib.functions import *
from lib.constants import *

settings = set_file(defaultsettings, "settings.txt")
save = defaultsave[:]  # файл сохранения
savename = None  # имя файла сохранения в папке
pygame.init()  # Основная инициализация, определеине размеров, создание констант
pygame.display.set_caption('Игра')
if settings["fullscreen"]:  # Фуллскрин или нет
    screen = pygame.display.set_mode(psize, pygame.FULLSCREEN | pygame.SCALED)
else:
    screen = pygame.display.set_mode(psize)
size = width, height = screen.get_size()  # Размер экрана
pixel_size = height // 100  # Размер пикселей игры
MAIN_FONT = pygame.font.Font("data/cool pixel font.ttf", pixel_size * 6)  # Основной шрифт
BIG_FONT = pygame.font.Font("data/cool pixel font.ttf", pixel_size * 8)  # Крупная версия

# Инициализация основных групп спрайтов
buttons = pygame.sprite.Group()
sprites = pygame.sprite.Group()
additional = pygame.sprite.Group()


def exit():  # Удобная функция выхода из игры. Она не с остальными функциями,
    # потому что в ней так же происходит сохранение всех настроек
    if any([i == 0 for i in save]):
        save_file(settings, "settings.txt")
        if savename is None and any([1 in i for i in save]):
            save_file(save, datetime.now().strftime("%H-%M-%S %d.%m.%Y") +
                      str(len(os.listdir(os.getcwd())) - 8) + ".save")
        elif savename is not None:
            save_file(save, savename)
    pygame.quit()
    sys.exit()


class GameStage:  # Надкласс для стадий игры, чтобы не создавать кучу повторяющихся циклов
    def __init__(self):
        self.elements = []
        self.sprites = pygame.sprite.Group()
        self.args = None
        self.nextstage = None
        self.active = True

    def do_things(self, *args):  # "Истинное обновление". Возникло, потому что есть пауза
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

    def pause(self):  # Функция остановки
        self.active = False

    def unpause(self):  # Функция продолжения
        self.active = True

    def toggle_pause(self):  # Переключатель между паузой и... непаузой
        self.active = not self.active

    def transform(self, stage=None, *args):  # Функция для перехода с одной стадии к другой
        self.active = False
        for _ in range(len(self.elements)):  # Удаление всех спрайтов
            self.elements[-1].kill()
            i = self.elements.pop()
            del i
        if stage is None:
            return
        self.nextstage = stage  # Nextstage проверяется в основном цикле, если она не пустая,
        # весь класс меняется на другой
        self.args = args  # Аргументы, которые можно подать на следующую стадию


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
        if italic:  # Некоторые части могут быть курсивом - это типа пролом четвертой стены
            self.italics = [True for _ in range(len(self.fulltext))]
        elif italics is not None:  # Список курсивных фраз
            self.italics = italics
        else:
            self.italics = [False for _ in range(len(self.fulltext))]
        if not cutscene and not self.italics[0]:
            self.text[0] = '* ' + self.text[0]  # Просто по приколу
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
        # Область письма
        if cutscene:
            self.image = pygame.Surface((width, height))
            self.rect = pygame.Rect(0, 0, width, height)
        else:
            self.image = load_image("dialogue.png", scale=pixel_size)
            if self.character is not None:
                self.image.blit(self.character, self.charrect)
            self.rect = pygame.Rect(0, height - self.image.get_height(),
                                    width, self.image.get_height())
        if rates is None:  # Список скоростей письма для разных фраз
            self.rates = [rate for _ in range(len(self.fulltext))]
        else:
            self.rates = rates
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
        if cutscene:  # Изменение шрифта в зависимости от типа Speech
            self.font = BIG_FONT
        else:
            self.font = MAIN_FONT

    def update(self, mpos, click, keyboard):  # Функция для плавного появления текста и переходов
        doskip = keyboard[pygame.K_x]  # Скипать ли текст
        donext = keyboard[pygame.K_z] or keyboard[pygame.K_RETURN]  # Врубать ли следующую фразу
        # Изменение цвета в случае, если в colorlib записан другой
        if (self.phrase, self.step // self.rates[self.phrase]) not in self.colorlib:
            color = self.maincolor
        else:
            color = self.colorlib[(self.phrase, self.step // self.rates[self.phrase])]
        # "Проматывание" текущего текста до конца, если лень смотреть анимацию
        if doskip and self.step < (len(self.normaltext)) * self.rates[self.phrase]:
            if self.italics[self.phrase]:
                self.font.set_italic(True)
            self.step = (len(self.normaltext) - 1) * self.rates[self.phrase]
            bltext = [self.font.render(i, False, color) for i in self.text]
            for i in range(len(bltext)):  # Цикл, потому что несколько строк
                if self.cutscene:
                    x = (width - self.font.size(self.text[i])[0]) // 2
                else:
                    x = pixel_size * 6 + self.charrect.x + self.charrect.w
                self.image.blit(bltext[i], (
                    x, pixel_size * (5 + 20 * self.cutscene) + self.font.get_height() * i))
            if self.italics[self.phrase]:
                self.font.set_italic(False)
        elif donext and self.step >= (len(self.normaltext)) * self.rates[self.phrase]:
            # Если текст уже доанимировался, нажатие запускает следующую фразу
            self.next_phrase()
        elif self.step < (len(self.normaltext)) * self.rates[self.phrase]:
            if self.step % self.rates[self.phrase] == 0:
                # Если ничего не произошло, просто рендерим следующий символ
                # А еще, если шрифт курсивный, то рендерим не символ, а всю фразу
                # ДО символа включительно
                j = self.step // self.rates[self.phrase]
                numline = 0
                for i in self.text:  # Нахождение номера строки и символа в строке
                    if j >= len(i):
                        j -= len(i)
                        numline += 1
                    else:
                        break
                pizza = False  # Делать ли курсив. Типа Italic, Италия, пицца хыха
                if self.italics[self.phrase]:
                    pizza = True
                    self.font.set_italic(True)
                if pizza:  # Рендер курсива
                    bltext = self.font.render(
                        self.text[numline][:j + 1], False, color)
                else:  # Рендер некурсива (они отличаются по непонятной причине, но так надо)
                    bltext = self.font.render(
                        self.normaltext[self.step // self.rates[self.phrase]], False, color)
                if self.cutscene:  # Определение координат текста в зависимости от типа Speech
                    # и наличия спрайта персонажа
                    x = (width - self.font.size(self.text[numline])[0]) // 2
                else:
                    x = pixel_size * 6 + self.charrect.x + self.charrect.w
                self.image.blit(bltext, (x + self.font.size(
                    self.text[numline][:j])[0] * (not pizza),
                                         pixel_size * (5 + 20 * self.cutscene) +
                                         self.font.get_height() * numline))
            if self.italics[self.phrase]:
                self.font.set_italic(False)
            self.step += 1  # +1 шаг

    def set_text(self, text):  # Функция для переделки текста
        # Обновление области для письма (включая спрайты персонажей)
        if self.cutscene:
            self.image = pygame.Surface((width, height))
        else:
            self.image = load_image("dialogue.png", scale=pixel_size)
            if self.character is not None:
                self.image.blit(self.character, self.charrect)
        # Изменение текущего текста
        if type(text) == str:
            self.text = text.rstrip().split("\n")
        else:
            self.text = text
        if not self.cutscene and not self.italics[self.phrase]:
            self.text[0] = '* ' + self.text[0]
        self.normaltext = "".join(self.text)
        self.step = 0

    def next_phrase(self):  # Переход к следующей фразе
        if self.phrase >= len(self.fulltext) - 1:  # Если фразы закончились
            self.func()
            if not self.stay:
                self.kill()
        else:  # Новый текст, новый спрайт, новая скорость письма
            self.phrase += 1
            self.character = self.chars[self.phrase]
            if self.character is not None:
                self.charrect = self.character.get_rect()
                self.charrect = self.charrect.move(pixel_size * 5, pixel_size * 5)
            else:
                self.charrect = pygame.Rect(0, 0, 0, 0)
            self.set_text(self.fulltext[self.phrase])

    def is_complete(self):  # Закончился ли текст
        if self.phrase == len(self.fulltext) - 1 and \
                self.step == (len(self.normaltext)) * self.rates[self.phrase]:
            return True
        return False


class Tile(pygame.sprite.Sprite):  # Простой прямоугольник, возможно записать текст
    # Ну, и еще он может быть полупрозрачным
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
            self.image.blit(bltext, ((width - bltext.get_width()) // 2, height / 3 +
                                     self.rect.height / 3 / len(self.text) * i))

    def update(self, mpos, click, keyboard):
        if keyboard[pygame.K_z] or keyboard[pygame.K_RETURN]:
            self.func()
            if self.suicide:
                self.kill()


class Button(pygame.sprite.Sprite):
    # Класс простой кнопки с картинкой
    def __init__(self, x, y, sprite, text, tcolor, func, *args, send=False):
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
        self.args = args
        self.send = send

    def update(self, mpos, click, *args):
        # Нажатие кнопки
        if in_rect((self.rect.x, self.rect.y, *self.rect.size), mpos) and click:
            if self.send:
                global button_name
                button_name = self.text
            self.func(*self.args)

    def set_text(self, text):  # Передлка текста на кнопке
        self.text = text
        self.image = self.sprite.copy()
        self.image.blit(MAIN_FONT.render(self.text, False, self.tcolor),
                        ((self.rect.w - MAIN_FONT.size(text)[0]) / 2,
                         (self.rect.h - MAIN_FONT.get_height()) / 2))


class MainMenu(GameStage):  # Главное меню
    def __init__(self):
        super().__init__()
        self.generate_menu()

    def generate_menu(self):
        btn = load_image("menubutton.png", scale=pixel_size)
        self.append(Button((width - btn.get_width()) // 2,
                           (height - btn.get_height() * 5) // 2, btn.copy(),
                           "Попробовать демо", (0, 200, 0), self.saveload),
                    Button((width - btn.get_width()) // 2,
                           (height - btn.get_height() * 3) // 2, btn.copy(),
                           "Загрузить демо", (0, 200, 0), self.saveload, True),
                    Button((width - btn.get_width()) // 2,
                           (height - btn.get_height() * 1) // 2, btn.copy(),
                           "Настройки", (0, 200, 0), self.settings),
                    Button((width - btn.get_width()) // 2,
                           (height + btn.get_height() * 1) // 2, btn.copy(),
                           "Выход", (0, 200, 0), exit))

    def settings(self):
        self.transform(MainSettings)

    def saveload(self, load=False):
        self.transform(Saveload, load)


def set_choice(text, func, *args):  # Быстрая функция для создания окна с подтверждением
    stage.pause()
    Choice(text, func, *args)


class Choice(pygame.sprite.Sprite):  # Собсна само окно с подтверждением
    def __init__(self, text, func, *args):
        super().__init__(additional)
        global on_choice
        on_choice = True
        self.image = load_image("choice.png", scale=pixel_size)
        self.rect = self.image.get_rect()
        self.rect = self.rect.move((width - self.rect.width) // 2,
                                   (height - self.rect.height) // 2)
        p = pixel_size
        bltext = MAIN_FONT.render(text, False, (0, 200, 0))
        self.image.blit(bltext, (4 * p, 4 * p))
        self.ok = Button(self.rect.x + 4 * p, self.rect.y + 15 * p,
                         load_image("button.png", scale=p), "OK", (0, 200, 0), self.if_ok, *args)
        self.ok.kill()
        self.ok.add(additional)
        self.cancel = Button(self.rect.x + 57 * p, self.rect.y + 15 * p,
                             load_image("button.png", scale=p), "Отмена", (0, 200, 0), self.kill)
        self.cancel.kill()
        self.cancel.add(additional)
        self.func = func

    def if_ok(self, *args):  # Выполнение функции, если нажата клавиша "ОК"
        self.func(*args)
        self.kill()

    def kill(self):  # Самоуничтожение
        global on_choice, stage
        on_choice = False
        stage.unpause()
        self.ok.kill()
        del self.ok
        self.cancel.kill()
        del self.cancel
        super().kill()
        del self


class Saveload(GameStage):  # Экран с загрузкой или созданием файла
    def __init__(self, load):
        super().__init__()
        self.loaded = ["пусто0.save"] * 5
        files = os.listdir(os.getcwd())
        for i in range(len(files)):
            if ".save" in files[i]:
                self.loaded[self.loaded.index("пусто0.save")] = files[i]
        btn = load_image("menubutton.png", scale=pixel_size)
        btnw = btn.get_width()
        btnh = btn.get_height()
        for i in range(5):
            self.append(Button((width - btnw) // 2,
                               (height - btnh * 5) // 2 + i * btnh,
                               btn, self.loaded[i][:-6], (0, 200, 0),
                               self.play, self.loaded[i], load, send=True))
        self.append(Button((width - btnw) // 2,
                           (height - btnh * 5) // 2 + 5 * btnh,
                           btn, "Назад", (0, 200, 0),
                           self.back))

    def back(self):  # Выход в меню
        self.transform(MainMenu)

    def play(self, filename, load):  # Сохранение или загрузка сохранения
        if load and filename == "пусто0.save":  # Загрузка пустого файла. Ты дурак штоле?
            return
        elif load:  # Подтверждение просто на случай мисклика
            set_choice("Вы уверены?", self.load, filename)
        elif filename == "пусто0.save":  # Создание нового файла
            global savename
            savename = datetime.now().strftime("%H-%M-%S %d.%m.%Y") + \
                       str(len(os.listdir(os.getcwd())) - 8) + ".save"
            self.startgame()
        else:  # Перезапись существующего
            set_choice("Вы точно хотите перезаписать сохранение?", self.startgame,
                       datetime.now().strftime("%H-%M-%S %d.%m.%Y") +
                       str(len(os.listdir(os.getcwd())) - 8) + ".save", True)

    def load(self, file):  # Впомогательный класс, записывающий имя файла в переменную
        global save, savename
        save = set_file(save, file)
        savename = file
        self.startgame()

    def startgame(self, name=None, rewrite=False):  # Загрузка самой игры на нужной стадии
        if rewrite:  # Удаление перезаписываемого файла
            for i in self.loaded:
                if button_name in i:
                    os.remove(i)
                    break
        if name is not None:
            global savename
            savename = name
        i = 0
        j = 0
        for i in range(len(save)):
            fl = False
            for j in range(len(save[i])):
                if save[i][j] != 0:
                    fl = True
                    break
            if fl:
                break
        self.transform(gamestages[i][j])


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

    def tgl_fullscreen(self):  # Включение полноэкранного режима
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

    def savenback(self):  # Сохранение настроек и уход в главное меню
        save_file(settings, "settings.txt")
        self.transform(MainMenu)


class Help(GameStage):  # Класс с управлением
    def __init__(self):
        super().__init__()
        self.append(
            Tile(screen.get_rect(), (0, 0, 0, 0), [
                "z или enter: выполнить/подтвердить",
                "x: пропустить/отменить"
            ], func=self.intro, suicide=True)
        )

    def intro(self):  # Переход к интро
        global save, savename
        save[0][0] = 0
        save_file(save, savename)
        self.transform(Intro)


class Intro(GameStage):  # Введение в игру
    def __init__(self):
        super().__init__()
        self.funytimer = 3
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

    def game(self):  # Переход к первой мини-игре
        global save, savename
        save[0][1] = 0
        save_file(save, savename)
        self.transform(Reakcia)

    def update(self, *args):  # Появление кнопки
        if self.elements[0].is_complete() and self.wasnt:
            self.funytimer -= 1
        if self.funytimer == 0:
            btn = load_image("button.png", scale=pixel_size)
            self.wasnt = False
            self.append(Button((width - btn.get_width()) // 2,
                               (height - btn.get_height()) // 2,
                               btn, "нажми", (0, 200, 0), self.game))


class ReakTile(pygame.sprite.Sprite):  # Плитка для игры
    def __init__(self, xy, func):
        super().__init__(sprites)
        self.image = pygame.Surface((pixel_size * 7, pixel_size * 7))
        color = pygame.Color(random.randint(0, 120),
                             random.randint(150, 255),
                             random.randint(0, 120))
        self.image.fill(color)
        color.hsva = (color.hsva[0], min(color.hsva[1], 100),
                      max(color.hsva[2] - 30, 0), min(color.hsva[3], 100))
        self.image.fill(color, pygame.Rect(pixel_size, pixel_size, 5 * pixel_size, 5 * pixel_size))
        self.rect = pygame.Rect(*xy, pixel_size * 7, pixel_size * 7)
        self.func = func
        self.red = False

    def update(self, mpos, click, *args):
        if in_rect((self.rect.x, self.rect.y, *self.rect.size), mpos) and click:
            self.func()

    def change_func(self, func2):  # Становление плитки красной
        self.func = func2
        self.change_color(pygame.Color(255, 0, 0))
        self.red = True

    def is_red(self):  # Нужно ли на неее нажать
        return self.red

    def change_color(self, color=None):  # Изменение цвета
        if color is None:
            color = pygame.Color(random.randint(0, 120),
                                 random.randint(150, 255),
                                 random.randint(0, 120))
        else:
            color = pygame.Color(color)
        self.image.fill(color)
        color.hsva = (color.hsva[0], min(color.hsva[1], 100),
                      max(color.hsva[2] - 30, 0), min(color.hsva[3], 100))
        self.image.fill(color, pygame.Rect(pixel_size, pixel_size, 5 * pixel_size, 5 * pixel_size))
        self.red = False

    def blacknwhite(self):  # Черно-белый режим
        color = self.image.get_at((0, 0))
        color.hsva = [color.hsva[0], 0, color.hsva[2], color.hsva[3]]
        self.change_color(color)


class Timer(pygame.sprite.Sprite):  # Таймер
    def __init__(self, x, y, seconds, color=(0, 200, 0), func=do_nothing(),
                 stay=False, text=True):
        super().__init__()
        self.timer: float = seconds
        self.clock = pygame.time.Clock()
        self.func = func
        self.stay = stay
        self.color = color
        self.go = False
        self.text = "Время:  " * text
        bltext = MAIN_FONT.render(self.text + str(round(self.timer, 2)), False, color)
        p = pixel_size
        self.image = pygame.Surface((42 * p, 8 * p))
        self.image.fill((0, 0, 0))
        self.image.fill(color, pygame.Rect(p * 25, p, 16 * p, 6 * p))
        self.image.fill((0, 0, 0), pygame.Rect(p * 26, p * 2, 14 * p, 4 * p))
        self.image.blit(bltext, (p * 2, p * 2))
        self.rect = pygame.Rect(x, y, *self.image.get_size())

    def update(self, *args):  # Обновление таймера
        if self.go:
            time = self.clock.tick()
            self.timer -= time / 1000
            if self.timer <= 0:
                self.go = False
                self.timer = 0
                self.func()
                if not self.stay:
                    self.kill()
        bltext = MAIN_FONT.render(self.text + str(round(self.timer, 2)), False, self.color)
        p = pixel_size
        self.image = pygame.Surface((42 * p, 8 * p))
        self.image.fill((0, 0, 0))
        self.image.fill(self.color, pygame.Rect(p * 25, p, 16 * p, 6 * p))
        self.image.fill((0, 0, 0), pygame.Rect(p * 26, p * 2, 14 * p, 4 * p))
        self.image.blit(bltext, (p * 2, p * 1))

    def start(self):  # Начало отсчета
        self.go = True
        self.clock.tick()

    def stop(self):  # Остановка таймера
        self.go = False

    def restart(self, seconds):  # Перезапуск таймера
        self.timer: float = seconds
        self.clock = pygame.time.Clock()
        self.start()

    def timeleft(self):  # Сколько осталось времени
        return self.timer


class Counter(pygame.sprite.Sprite):  # Счетчик для реакции
    def __init__(self, x, y, color=(0, 200, 0)):
        super().__init__()
        self.counter = 0
        self.maxx = 0
        self.color = color
        self.text = "Счет:   "
        bltext = MAIN_FONT.render(self.text + str(self.counter) + "/" + str(self.maxx),
                                  False, color)
        p = pixel_size
        self.image = pygame.Surface((42 * p, 8 * p))
        self.image.fill((0, 0, 0))
        self.image.fill(color, pygame.Rect(p * 25, p, 16 * p, 6 * p))
        self.image.fill((0, 0, 0), pygame.Rect(p * 26, p * 2, 14 * p, 4 * p))
        self.image.blit(bltext, (p * 2, p * 2))
        self.rect = pygame.Rect(x, y, *self.image.get_size())

    def update(self, *args):
        bltext = MAIN_FONT.render(self.text + str(self.counter) + "/" + str(self.maxx),
                                  False, self.color)
        p = pixel_size
        self.image = pygame.Surface((42 * p, 8 * p))
        self.image.fill((0, 0, 0))
        self.image.fill(self.color, pygame.Rect(p * 25, p, 16 * p, 6 * p))
        self.image.fill((0, 0, 0), pygame.Rect(p * 26, p * 2, 14 * p, 4 * p))
        self.image.blit(bltext, (p * 2, p * 1))

    def delta(self, sc, m):  # Изменение очков
        self.counter += sc
        self.maxx += m

    def percentage(self):  # Сколько очков из максимума
        return (self.counter / self.maxx) * 100


class Reakcia(GameStage):  # Первая мини-игра
    def __init__(self, not_first=False):
        super().__init__()
        for i in range(10):
            for j in range(10):
                self.append(ReakTile(((width - pixel_size * 80) // 2 +
                                      j * 8 * pixel_size,
                                      (height - pixel_size * 80) // 2 +
                                      i * 8 * pixel_size), self.error))
        self.append(Timer(0, 0, 0.6, stay=True, func=self.error))
        self.append(Counter(pixel_size * 50, 0))
        self.updatetiles = 0
        self.trying = 0
        self.game_started = False
        self.stop = True
        self.overtimer = -1
        if not not_first and save[0][2] != 2:  # Интро
            self.append(
                Speech([["Первый тест - проверка на твою скорсть",
                         "обработки информации или, грубо говоря,",
                         "тест на реакцию."],
                        ["Тебе нужно как можно быстрее находить",
                         "красный квадрат среди ста других.",
                         "Для того, чтобы указать на квадрат,",
                         "тебе выдается специальный курсор."],
                        ["(В этой мини-игре используется",
                         "управление мышкой)"],
                        ["Всего дается 20 попыток.",
                         "Поторопись, на каждую попытку",
                         "у тебя есть лишь доля миллисекунды."],
                        ["Итак, тест начинается!"]], func=self.start,
                       italics=[False, False, True, False, False]))
        else:
            self.start()

    def start(self):  # Начало мини-игры
        global save
        save[0][2] = 2
        self.elements[100].start()
        self.game_started = True
        self.stop = False
        for i in range(100):
            self.elements[i].change_color()
        self.elements[random.randrange(100)].change_func(self.retry)

    def update(self):
        self.updatetiles += 1
        if not self.game_started and self.updatetiles % 20 == 0:
            for i in range(100):
                self.elements[i].change_color()

    def error(self):
        self.retry(0)

    def end(self):
        self.elements[100].stop()
        if not self.stop:
            self.stop = True
            for i in range(100):
                self.elements[i].blacknwhite()
            p = self.elements[101].percentage()
            loose = False
            if p == 100:
                text = [["Ого! Постирон- эээ, потрясающий результат!",
                         "Ты набрал все 20 баллов!"],
                        ["Разумеется, это не значит, что тебя",
                         "не нужно продолжать оптимизировать",
                         "(ведь у нас впереди куда более сложные",
                         "задачи на скорость), но этот тест",
                         "ты прошел на все 100!"]]
            elif p > 90:
                text = [["Прекрасный результат!",
                         "Хоть это задание и одно из простых,",
                         "Я рад, что ты прошел его с такой легкостью."]]
            elif p > 70:
                text = [["Неплохой результат!",
                         "Вполне ожидаемо для такой нейроструктуры,",
                         "как у тебя."],
                        ["Разумеется, твой вычислительный",
                         "центр необходимо будет оптимизировать",
                         "для задач мирового уровня,",
                         "Но для начала результат очень неплохой!"]]
            elif p > 50:
                text = [["Результат... приемлемый.",
                         "Не лучший, конечно же, и даже ниже,",
                         "чем я рассчитывал, но приемлемый."],
                        ["Тебя, конечно же, придется оптимизировать,",
                         "но это неизбежно вне зависимости от теста."]]
            elif p > 30:
                text = [["...хм."],
                        ["Возможно, что-то в системе заторомзило?",
                         "Хотя нет, это исключено, я специально",
                         "очищал все данные сервера."],
                        ["К тому же, он рассчитан на куда большие",
                         "перегрузки. Значит ли это, что ты так плохо",
                         "оптимизирован?"],
                        ["Потребуется больше тестов, чем я думал...",
                         "Хотя сейчас это неважно.",
                         "На чем это я остановился? А, да."]]
            else:
                text = [["..."],
                        ["Окей, скажу сразу, ты не прошел тест.",
                         "Скорее всего в тебе есть какой-то",
                         "Баг, очень сильно тормозящий твою",
                         "мыслительную деятельность. И я не могу",
                         "его проигнорировать."],
                        ["Не хотелось прибегать к этому, поскольку",
                         "не известно, что происходит с сознанием",
                         "после полной перепрошивки.",
                         "Но это явно необходимо."],
                        ["Прости и прощай,",
                         "на случай, если ты... ну, не будешь собой."]]
                loose = True
            if not loose:
                phrase = [["Тест завершен, время смотреть результаты.",
                           "Тааак, что тут у нас?"],
                          ["..."],
                          *text,
                          ["Итак, следующий тест - на сложность",
                           "твоей нейросети. Он скорее лишь для",
                           "галочки, просто проверить,",
                           "не повредилось ли твое сознание при...", ],
                          ["А впрочем, это не так уж и важно.",
                           "Переходим к следующему тесту!"]]
                self.append(Speech(phrase, func=self.win))
            else:
                phrase = [["Тест завершен, время смотреть результаты.",
                           "Тааак, что тут у нас?"],
                          ["..."],
                          *text]
                self.append(Speech(phrase, func=self.gameover))

    def win(self):
        save[0][2] = 0
        self.append(Speech([["Так, ну поскольку это демка..."],
                            ["Хочешь попробовать еще раз?"]],
                           func=self.choice, italic=True))

    def gameover(self):
        global save
        save[0][2] = 3
        self.transform(GameOver)

    def choice(self):
        btn = load_image("button.png", scale=pixel_size)
        self.append(
            Tile((width / 5, 0, width * 3 / 5, height), pygame.Color(100, 150, 100, 150))
        )
        self.append(
            Button((width - btn.get_width() * 3) / 2, height / 2, btn,
                   "Еще раз", (0, 200, 0), self.completeretry))
        self.append(
            Button((width + btn.get_width()) / 2, height / 2, btn,
                   "В меню", (0, 200, 0), self.to_menu)
        )

    def to_menu(self):
        global save, savename
        save_file(save, savename)
        self.transform(MainMenu)

    def retry(self, score=1):
        if self.game_started:
            self.trying += 1
            if self.trying <= 20:
                self.elements[101].delta(score, 1)
                for i in range(100):
                    self.elements[i].change_color()
                self.elements[100].restart(0.6)
                self.elements[random.randrange(100)].change_func(self.retry)
            else:
                self.end()

    def completeretry(self):
        self.transform(Reakcia)


class GameOver(GameStage):
    def __init__(self):
        super().__init__()
        self.append(pygame.sprite.Sprite())
        self.elements[-1].image = load_image("gameover.png", scale=pixel_size)
        self.elements[-1].rect = pygame.Rect(0, 0, 150 * pixel_size, 100 * pixel_size)
        btn = load_image("button.png", scale=pixel_size)
        self.append(Button((width - btn.get_width()) // 2, height - pixel_size * 30, btn,
                           "В меню", (0, 200, 0), self.to_menu))

    def to_menu(self):
        self.transform(MainMenu)


gamestages = [[Help, Intro, Reakcia]]

if __name__ == '__main__':
    running = True
    # Теоретическое положение курсора по умолчанию
    mouse_pos = (0, 0)
    clock = pygame.time.Clock()
    stage = MainMenu()
    while running:  # Основной цикл
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
        if not on_choice:
            sprites.update(mouse_pos, click, pygame.key.get_pressed())
        screen.fill((0, 0, 0))
        sprites.draw(screen)
        nextstage = stage.nextstage
        if nextstage is not None:
            stage = nextstage(*stage.args)
        stage.do_things(mouse_pos, click, pygame.key.get_pressed())
        # Обновление спрайтов, которым пофиг на паузу
        additional.update(mouse_pos, click, pygame.key.get_pressed())
        additional.draw(screen)
        # Вывод на экран и подгонка fps
        pygame.display.flip()
        clock.tick(fps)
    exit()
