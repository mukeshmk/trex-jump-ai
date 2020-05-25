import os
import time
import neat
import random

#pygame version number and welcome message hidden.
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame

WIN_WIDTH = 750
WIN_HEIGHT = 400

WHITE = (255, 255, 255)

dino_imgs = [pygame.transform.scale2x(pygame.image.load(os.path.join("images", "dino-0" + str(x) + ".png"))) for x in range(1, 3)]
bush_imgs = [pygame.transform.scale2x(pygame.image.load(os.path.join("images", "bush-0" + str(x) + ".png"))) for x in range(1, 4)]
base_img = pygame.transform.scale2x(pygame.image.load(os.path.join("images", "base.png")))

def draw_window(win, dino):
    win.fill(WHITE)
    win.blit(base_img, (0, 350))
    win.blit(dino, (200, 200))
    win.blit(bush_imgs[0], (400, 300))
    pygame.display.update()

def main():
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))

    run = True
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
        draw_window(win, dino_imgs[0])

main()