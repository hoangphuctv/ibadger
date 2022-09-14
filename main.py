from operator import truediv
from os import stat
from turtle import back
import pygame
import os


pygame.init()
white = 255, 255, 255
black = 0, 0, 0
X = 600
Y = 800

screen = pygame.display.set_mode()
sw, sh = screen.get_size()
pygame.display.set_caption("img")

is_run = True
while is_run:
    for i in pygame.event.get():
        if i.type == pygame.QUIT:
            is_run = False

    if is_run:
        screen.fill(black)

pygame.quit()
