#!/usr/bin/env python3
import pygame
import os
import sys

APP_ROOT = os.path.dirname(os.path.realpath(sys.argv[0]))
APP_NAME = "iBadger"


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


class ImageAction:
    def scale(self, img, to_width, to_height):
        return pygame.transform.smoothscale(img, (to_width, to_height))


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
        allfiles = os.listdir(active_dir)

        for i, x in enumerate(allfiles):
            if not x.endswith((".jpg", ".png", "jpeg")):
                continue
            if x is None or x == "":
                continue
            if self.active_file != "" and self.active_file == x:
                self.index = self.count()

            self.files.append(os.path.join(active_dir, x))

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


class App:
    is_run = True
    is_fullscreen = False
    X = 600
    Y = 800
    img_manager = None
    img = None
    img_path = None
    screen = None
    start_x = 0
    start_y = 0
    max_width = 0
    max_height = 0
    is_change = False

    def __init__(self, active_dir):
        pygame.init()
        self.img_manager = ImageManager(active_dir)
        self.screen = pygame.display.set_mode((self.X, self.Y))
        pygame.display.set_caption(APP_NAME)
        self.fullscreen()
        imageapp = os.path.join(APP_ROOT, "app.png")
        if os.path.isfile(imageapp):
            pygame.display.set_icon(pygame.image.load(imageapp))

    def show_text(self, text, pos1, pos2, center=False):
        font = pygame.font.SysFont(None, 24)
        textimg = font.render(text, True, Color.white)
        img_width = textimg.get_rect()[2]
        sw, sh = self.screen.get_size()
        if center:
            self.screen.blit(textimg, ((sw / 2) - img_width, pos2))
        else:
            self.screen.blit(textimg, (pos1, pos2))

    def show_prev_image(self):
        self.img_manager.prev()
        self.img = pygame.image.load(self.img_manager.current()).convert()
        self.is_change = False
        self.show_image()

    def show_next_image(self):
        self.img_manager.next()
        self.img = pygame.image.load(self.img_manager.current()).convert()
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

        if self.img is None :
            self.img = pygame.image.load(self.img_manager.current()).convert()

        rect = self.img.get_rect()

        img_width = rect[2]
        img_height = rect[3]
        self.max_width = img_width
        self.max_height = img_height

        if sw < img_width:
            self.max_width = sw
            self.max_height = int(img_height * (sw / img_width))

        self.start_x = (sw - self.max_width) / 2
        self.start_y = (sh - self.max_height) / 2

        self.img = pygame.transform.scale(self.img, (self.max_width, self.max_height))
        self.screen.blit(self.img, (self.start_x, self.start_y))
        loc = self.img_manager.get_loc()
        if loc[1] == 0:
            text = "no image found"
        else:
            text = "%s/%s | %s" % (loc[0], loc[1], self.img_manager.current())
        
        self.show_text(text, 20, 30)
        pygame.display.flip()

    def show_status(self, text):
        self.screen.fill(Color.gray)
        self.screen.blit(self.img, (self.start_x, self.start_y))
        self.show_text(text, 20, 30)
        pygame.display.flip()

    def rotate_image_right(self):
        self.is_change = True
        print ("is_change " + str(self.is_change))
        
        self.img = pygame.transform.rotate(self.img, 90)
        self.show_image();

    def rotate_image_left(self):
        self.is_change = True
        print ("is_change " + str(self.is_change))
        self.img = pygame.transform.rotate(self.img, -90)
        self.show_image();
        
    def save_change(self):
        print ("save_change is_change " + str(self.is_change))
        if self.is_change:
            pygame.image.save(self.img, self.img_manager.current())
            self.show_status('save ok ' + self.img_manager.current())
            self.is_change = False
        
    def on_mouse_click(self, event):
        if event.button == Mouse.LEFT:
            self.show_next_image()
        elif event.button == Mouse.RIGHT:
            self.show_prev_image()

    def on_key_press(self, event):
        key_map = {
            pygame.K_SPACE: self.fullscreen,
            pygame.K_ESCAPE: self.quit,
            pygame.K_RIGHT: self.show_next_image,
            pygame.K_LEFT: self.show_prev_image,
            pygame.K_UP: self.rotate_image_right,
            pygame.K_DOWN: self.rotate_image_left,
            pygame.K_s: self.save_change,
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
        pygame.quit()
        sys.exit()

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

        self.quit()


if __name__ == "__main__":
    active_dir = ""
    if len(sys.argv) > 1:
        active_dir = sys.argv[1]
    app = App(active_dir)
    app.run()
    app.quit()
