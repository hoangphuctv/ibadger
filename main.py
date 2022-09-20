import pygame
import os
import sys

APP_ROOT = os.path.dirname(os.path.realpath(__file__))
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
        app_img = os.path.join(APP_ROOT, "app.png")
        if os.path.exists(app_img):
            pygame.display.set_icon(pygame.image.load(app_img))

    def show_text(self, text, pos1, pos2, center=False):
        font = pygame.font.SysFont(None, 24)
        textimg = font.render(text, True, Color.white)
        img_width = textimg.get_rect()[2]
        # img_height = img.get_rect()[3]
        sw, sh = self.screen.get_size()
        if center:
            self.screen.blit(textimg, ((sw/2)-img_width, pos2))
        else:
            self.screen.blit(textimg, (pos1, pos2))

    def show_prev_image(self):
        self.img_manager.prev()
        self.show_image()

    def show_next_image(self):
        self.img_manager.next()
        self.show_image()

    def show_image(self):
        self.screen.fill(Color.gray)
        sw, sh = self.screen.get_size()
        imgpath = self.img_manager.current()
        if imgpath is None:
            self.show_text('No image', 0, sh/2, True)
            pygame.display.flip()
            return

        img = pygame.image.load(self.img_manager.current()).convert()
        rect = img.get_rect()
        
        img_width = rect[2]
        img_height = rect[3]
        max_width = img_width
        max_height = img_height
        
        if sw < img_width:
            max_width = sw
            max_height = int(img_height * (sw/img_width))
        
        start_x = (sw - max_width) / 2
        start_y = (sh - max_height) / 2
        
        img = pygame.transform.scale(img, (max_width, max_height))
        self.screen.blit(img, (start_x, start_y))

        text = (
            str(self.img_manager.get_index() + 1) + "/" + str(self.img_manager.count())
        )
        self.show_text(text, 20, 20)
        pygame.display.flip()

    def on_mouse_click(self, event):
        if event.button == Mouse.LEFT:
                self.show_next_image()
        elif event.button == Mouse.RIGHT:
                self.show_prev_image()

    def quit(self):
        pygame.quit()
        sys.exit()

    def run(self):
        while self.is_run:
            for i in pygame.event.get():
                if i.type == pygame.QUIT:
                    self.is_run = False
                elif i.type == pygame.KEYDOWN:
                    if i.key == pygame.K_SPACE:
                        if self.is_fullscreen:
                            self.screen = pygame.display.set_mode((self.X, self.Y))
                            self.is_fullscreen = False
                            self.show_image()
                        else:
                            self.screen = pygame.display.set_mode(
                                (0, 0), pygame.FULLSCREEN
                            )
                            self.is_fullscreen = True
                    self.show_image()

                    if i.key == pygame.K_ESCAPE:
                        self.quit()
                    elif i.key == pygame.K_RIGHT:
                        self.show_next_image()
                    elif i.key == pygame.K_LEFT:
                        self.show_prev_image()
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
