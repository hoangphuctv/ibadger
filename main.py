from asyncio import events
from operator import truediv
from os import stat
from turtle import back
import pygame
import os
import sys

APP_ROOT = os.path.dirname(os.path.realpath(__file__))
APP_NAME = "iBadger"


class ImageManager:
    index = 0
    files = []
    active_dir = ""
    active_file = ""

    def __init__(self, active_dir=""):
        
        if active_dir == "" or active_dir == ".":
            active_dir = os.getcwd()
        elif not os.path.exists(active_dir):
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
        print(self.files)

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

        # print("Len ", self.count())
        # print("Access ", self.index)
        return self.files[self.index]

    def next(self):
        self.index = self.index + 1
        return self.current()

    def prev(self):
        self.index = self.index - 1
        return self.current()

    def get_index(self):
        return self.index


class Color:
    white = 255, 255, 255
    black = 0, 0, 0


class App:
    is_run = True
    is_fullscreen = False
    X = 600
    Y = 800
    img_manager = None
    screen = None

    def __init__(self, active_dir):
        pygame.init()
        self.img_manager = ImageManager(active_dir)
        self.screen = pygame.display.set_mode((self.X, self.Y))
        pygame.display.set_caption(APP_NAME)
        self.show_image()
        pygame.display.set_icon(pygame.image.load(os.path.join(APP_ROOT, "app.png")))

    def show_text(self, text, pos1, pos2):
        font = pygame.font.SysFont(None, 24)
        img = font.render(text, True, Color.white)
        self.screen.blit(img, (pos1, pos2))

    def show_prev_image(self):
        self.img_manager.prev()
        self.show_image()

    def show_next_image(self):
        self.img_manager.next()
        self.show_image()

    def show_image(self):
        imgpath = self.img_manager.current()
        if imgpath is None:
            return
        img = pygame.image.load(self.img_manager.current()).convert()
        rect = img.get_rect()
        sw, sh = self.screen.get_size()

        start_x = (sw - rect[2]) / 2
        start_y = (sh - rect[3]) / 2
        self.screen.blit(img, (start_x, start_y))

        text = (
            str(self.img_manager.get_index() + 1) + "/" + str(self.img_manager.count())
        )
        self.show_text(text, 20, 20)
        pygame.display.flip()

    def quit(self):
        pygame.quit()

    def run(self):
        while self.is_run:
            for i in pygame.event.get():
                if i.type == pygame.QUIT:
                    self.is_run = False
                elif i.type == pygame.KEYDOWN:
                    if i.key == pygame.K_SPACE:
                        self.screen.fill(Color.black)

                        if self.is_fullscreen:
                            self.screen = pygame.display.set_mode((self.X, self.Y))
                            self.is_fullscreen = False
                        else:
                            self.screen = pygame.display.set_mode(
                                (0, 0), pygame.FULLSCREEN
                            )
                            self.is_fullscreen = True

                        self.show_image()

                    if i.key == pygame.K_ESCAPE:
                        pygame.quit()
                    elif i.key == pygame.K_RIGHT:
                        self.show_next_image()
                    elif i.key == pygame.K_LEFT:
                        self.show_prev_image()
                elif i.type == pygame.MOUSEBUTTONUP:
                    if i.button == 1:
                        self.show_next_image()
                    elif i.button == 3:
                        self.show_prev_image()

            if self.is_run:
                self.screen.fill(Color.black)
        
        self.quit()


if __name__ == "__main__":
    print(sys.argv)
    active_dir = ""
    if len(sys.argv) > 2:
        active_dir = sys.argv[1]

    app = App(active_dir)
    app.run()
    app.quit()


# 1 - left click
# 2 - middle click
# 3 - right click
# 4 - scroll up
# 5 - scroll down
