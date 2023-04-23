#!/usr/bin/env python3
import os
import sys
import threading
from datetime import datetime

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"
import pygame

APP_ROOT = os.path.dirname(os.path.realpath(sys.argv[0]))
APP_NAME = "iBadger"
SUPPORTED_EXT = (".jpg",".jpeg", ".png", "jpeg", ".bmp")
DEBUG = True


def debug(txt):
    if not DEBUG:
        return
    now = datetime.now()
    dt_string = now.strftime("%Y-%m-%d %H:%M:%S")
    print(dt_string, txt)


def scale_img_size(w, h, maxw, maxh, ratio=1):
    if w > maxw:
        w, h = maxw, h * maxw / w

    if h > maxh:
        w, h = w * maxh / h, maxh
    return w * ratio, h * ratio


class Color:
    white = 255, 255, 255
    black = 0, 0, 0
    gray = 100, 100, 100


class Mouse:
    LEFT = 1
    MIDDLE = 2
    RIGHT = 3
    SCROLL_UP = 4
    SCROLL_DOWN = 5


class ImageManager:
    index = 0
    files = []
    active_dir = ""
    active_file = ""

    def __init__(self, active_dir=""):
        if active_dir == "" or active_dir == ".":
            active_dir = os.getcwd()
        elif not os.path.exists(active_dir):
            print("path not found ", active_dir)
            active_dir = os.getcwd()
        else:
            active_dir = os.path.realpath(active_dir)

        if os.path.isfile(active_dir):
            self.active_file = os.path.basename(active_dir)
            active_dir = os.path.dirname(active_dir)

        self.active_dir = active_dir
        debug("Active dir: " + active_dir)


    def scanfile(self):
        cwd = self.active_dir
        for f in os.listdir(cwd):
            if os.path.isfile(os.path.join(cwd, f)) and f.lower().endswith(SUPPORTED_EXT):
                self.files.append(os.path.join(cwd, f))
                if len(self.files) == 1:
                    app.show_image()

        app.show_image()

    def count(self):
        return len(self.files)

    def append(self, img_path):
        self.files.append(img_path)

    def current(self):
        if self.count() <= 0:
            return None
        if self.index >= self.count():
            self.index = 0
        elif self.index < 0:
            self.index = self.count() - 1

        return self.files[self.index]

    def next(self):
        self.index = self.index + 1
        return self.current()

    def prev(self):
        self.index = self.index - 1
        return self.current()

    def get_index(self):
        return self.index

    def get_loc(self):
        return (self.get_index() + 1, self.count())

    def remove_path(self, path):
        n = self.count()
        i = 0
        for f in self.files:
            if f == path:
                return self.files.pop(i)

            i = i + 1

        return None                


class App:
    is_run = True
    is_fullscreen = False
    X = 600
    Y = 800
    img_manager = None
    img = None
    img_org = None
    img_path = None
    screen = None
    start_x = 0
    start_y = 0
    max_width = 0
    max_height = 0
    is_change = False
    zoom_level = 1

    def __init__(self, active_dir):
        pygame.init()
        self.img_manager = ImageManager(active_dir)
        self.screen = pygame.display.set_mode((self.X, self.Y))
        pygame.display.set_caption(APP_NAME)
        self.show_image()
        imageapp = os.path.join(APP_ROOT, "app.png")
        if os.path.isfile(imageapp):
            pygame.display.set_icon(pygame.image.load(imageapp))

    def load_img(self, path="", retry=1):
        if path == "":
            path = self.img_manager.current()

        if path is None:
            return None
        if retry > 3:
            return None
        try:
            debug("load_img " + path)
            return pygame.image.load(path).convert_alpha()
        except:
            self.img_manager.remove_path(path)
            path = self.img_manager.current()
            self.load_img(self.img_manager.current(), retry + 1)

    def zoom_level_reset(self):
        self.zoom_level = 1
        debug("zoom_level " + str(self.zoom_level))
        self.show_image()

    def zoom_level_increase(self):
        if self.zoom_level > 2:
            return
        self.zoom_level += 0.05
        debug("zoom_level " + str(self.zoom_level))
        self.show_image()

    def zoom_level_decrease(self):
        if self.zoom_level < 0.8:
            return
        self.zoom_level -= 0.05
        debug("zoom_level " + str(self.zoom_level))
        self.show_image()

    def show_text(self, text, xleft, xtop, center=False):
        font = pygame.font.SysFont("Arial", 12)
        textimg = font.render(text, True, Color.white)
        img_width = textimg.get_rect()[2]
        sw, sh = self.screen.get_size()
        if center:
            self.screen.blit(textimg, ((sw / 2) - img_width, xtop))
        else:
            self.screen.blit(textimg, (xleft, xtop))

    def show_prev_image(self):
        self.img_manager.prev()
        self.img_org = self.load_img()
        self.is_change = False
        self.show_image()

    def show_next_image(self):
        self.img_manager.next()
        self.img_org = self.load_img()
        self.is_change = False
        self.show_image()

    def show_image(self):
        self.screen.fill(Color.gray)
        sw, sh = self.screen.get_size()
        imgpath = self.img_manager.current()
        if imgpath is None:
            self.show_text("No image", 0, sh / 2, True)
            pygame.display.flip()
            return

        if self.img_org is None:
            self.img_org = self.load_img()

        self.img = self.img_org

        if self.img is None:
            return

        rect = self.img.get_rect()

        img_width = rect[2]
        img_height = rect[3]
        self.max_width, self.max_height = scale_img_size(
            img_width, img_height, sw, sh, self.zoom_level
        )

        self.start_x = (sw - self.max_width) / 2
        self.start_y = (sh - self.max_height) / 2

        self.img = pygame.transform.smoothscale(
            self.img, (self.max_width, self.max_height)
        )
        self.screen.blit(self.img, (self.start_x, self.start_y))
        loc = self.img_manager.get_loc()
        if loc[1] == 0:
            text = "no image found"
        else:
            text = "%s/%s | %s" % (
                loc[0],
                loc[1],
                os.path.basename(self.img_manager.current()),
            )

        self.show_text(text, 20, 20)
        pygame.display.flip()

    def show_status(self, text):
        self.screen.fill(Color.gray)
        self.screen.blit(self.img, (self.start_x, self.start_y))
        self.show_text(text, 20, 20)
        pygame.display.flip()

    def rotate_image_right(self):
        self.is_change = True

        self.img_org = pygame.transform.rotate(self.img_org, 90)
        self.show_image()

    def rotate_image_left(self):
        self.is_change = True
        self.img_org = pygame.transform.rotate(self.img_org, -90)
        self.show_image()

    def save_change(self):
        if self.is_change:
            pygame.image.save(self.img_org, self.img_manager.current())
            self.show_status("save ok " + self.img_manager.current())
            self.is_change = False

    def on_mouse_click(self, event):
        if event.button == Mouse.LEFT:
            self.show_next_image()
        elif event.button == Mouse.RIGHT:
            self.show_prev_image()
        elif event.button == Mouse.MIDDLE:
            self.zoom_level_reset()

    def on_key_press(self, event):
        debug("on_key_press = " + str(event.key))
        key_map = {
            pygame.K_SPACE: self.fullscreen,
            pygame.K_ESCAPE: self.quit,
            pygame.K_RIGHT: self.show_next_image,
            pygame.K_LEFT: self.show_prev_image,
            pygame.K_r: self.rotate_image_right,
            pygame.K_l: self.rotate_image_left,
            pygame.K_s: self.save_change,
            pygame.K_q: self.quit,
            pygame.K_0: self.zoom_level_reset,
        }
        do_action = key_map.get(event.key, None)
        if do_action:
            do_action()

    def fullscreen(self):
        if self.is_fullscreen:
            self.screen = pygame.display.set_mode((self.X, self.Y))
            self.is_fullscreen = False
            self.show_image()
        else:
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            self.is_fullscreen = True
        self.show_image()

    def quit(self):
        sys.exit()
        pygame.quit()

    def check_exit(self):
        if self.is_run is False:
            self.quit()

    def run(self):
        while self.is_run:
            for i in pygame.event.get():
                if i.type == pygame.QUIT:
                    self.is_run = False
                    break
                elif i.type == pygame.KEYDOWN:
                    self.on_key_press(i)
                elif i.type == pygame.MOUSEBUTTONUP:
                    self.on_mouse_click(i)
                elif i.type == pygame.MOUSEBUTTONDOWN:
                    if i.button == 4:
                        self.zoom_level_increase()
                    elif i.button == 5:
                        self.zoom_level_decrease()

        self.quit()


if __name__ == "__main__":
    active_dir = ""
    if len(sys.argv) > 1:
        active_dir = sys.argv[1]
    app = App(active_dir)

    # th_scanfile = threading.Thread(target=app.img_manager.scanfile, args=())
    # th_scanfile.start()

    app.img_manager.scanfile()
    app.run()
