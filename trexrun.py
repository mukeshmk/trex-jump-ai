import os
import time
import neat
import random

#pygame version number and welcome message hidden.
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame

# initiallise font
pygame.font.init()

WIN_WIDTH = 1300
WIN_HEIGHT = 500
FLOOR = 350
DINO_BASE = 282.5

WHITE = (255, 255, 255)

dino_imgs = [pygame.transform.scale2x(pygame.image.load(os.path.join("images", "dino-0" + str(x) + ".png"))) for x in range(1, 3)]
bush_imgs = [pygame.transform.scale2x(pygame.image.load(os.path.join("images", "bush-0" + str(x) + ".png"))) for x in range(1, 4)]
base_img = pygame.transform.scale2x(pygame.image.load(os.path.join("images", "base.png")))

STAT_FONT = pygame.font.SysFont("comicsans", 50)

class Dino:
    IMGS = dino_imgs
    ANIMATION_TIME = 5

    def __init__(self, x, y):
        # inital x and y position of the t-rex
        self.x = x
        self.y = y
        # tick_count for time
        self.tick_count = 0
        # inital velocity of the t-rex
        self.vel = 0
        # inital image of the t-rex to be displayed
        self.img_count = 0
        self.img = self.IMGS[0]
        # to check if the t-rex is in jumping motion
        self.is_jump = False

    def move(self):
        # increasing time as move occured every "second" or tick
        self.tick_count += 1

        # s = u * t + 0.5 * a * t^2
        displacement = self.vel * self.tick_count + 0.5 * 1.5 * (self.tick_count**2)
        
        # limits the displacement in the downward direction to a max displacement value
        if displacement >= 16:
            displacement = 16
        
        # limits the displacement in the upward direction to a max displacement value
        if displacement < 0:
            displacement -= 2

        self.y += displacement
        
        if self.y > DINO_BASE:
            self.is_jump = False
            self.y = DINO_BASE
        else:
            self.is_jump = True


    def draw(self, win):
        self.img_count += 1

        # For animation of the trex, loop through three images
        if self.img_count <= self.ANIMATION_TIME:
            self.img = self.IMGS[0]
        elif self.img_count <= self.ANIMATION_TIME*2:
            self.img = self.IMGS[1]
        elif self.img_count == self.ANIMATION_TIME*2 + 1:
            self.img = self.IMGS[0]
            self.img_count = 0
        
        # To stop running animation when jumping
        if self.is_jump:
            self.img = self.IMGS[0]
            self.img_count = 0

        win.blit(self.img, (self.x, self.y))
    
    def jump(self):
        # to avoid double jump when in air
        if self.is_jump:
            return
        # reseting tick_count (time) = 0 to denote the instant at which the jump occured
        self.tick_count = 0
        # the velocity with which the bird moves up when it jumps
        # NOTE vel is negative cause the top left corner of the pygame window is (0, 0)
        self.vel = -9

    def get_mask(self):
        return pygame.mask.from_surface(self.img)

class Base:
    VEL = 10
    WIDTH = base_img.get_width()
    IMG = base_img

    def __init__(self, y):
        self.y = y
        # for cyclic rotation of the background image
        self.x1 = 0
        self.x2 = self.WIDTH
        self.x3 = self.WIDTH*2

    def move(self):
        self.x1 -= self.VEL
        self.x2 -= self.VEL
        self.x3 -= self.VEL

        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x3 + self.WIDTH

        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH
        
        if self.x3 + self.WIDTH < 0:
            self.x3 = self.x2 + self.WIDTH

    def draw(self, win):
        win.fill(WHITE)
        win.blit(self.IMG, (self.x1, self.y))
        win.blit(self.IMG, (self.x2, self.y))
        win.blit(self.IMG, (self.x3, self.y))

class Bush:
    VEL = 10

    def __init__(self, x):
        self.obstacle_size = 0
        self.passed = False

        self.x = [x, x + bush_imgs[0].get_width(), x + bush_imgs[0].get_width() + bush_imgs[1].get_width()]
        self.y = 300

        self.set_width()

    def set_width(self):
        self.obstacle_size = random.randrange(1, 4)

    def move(self):
        for i in range(3):
            self.x[i] -= self.VEL

    def draw(self, win):
        for i in range(self.obstacle_size):
            win.blit(bush_imgs[i], (self.x[i], self.y))
    
    def collide(self, dino):
        dino_mask = dino.get_mask()

        points = []
        for i in range(self.obstacle_size):
            # getting the masks for the images
            mask = pygame.mask.from_surface(bush_imgs[i])
            # calculating the rectangle offset of the images
            offset = (self.x[i] - dino.x, self.y - round(dino.y))
            points.append(dino_mask.overlap(mask, offset))
        
        for point in points:
            if point:
                return True # collision occured
        return False

def draw_window(win, dino, base, bushes, score):
    base.draw(win)
    dino.draw(win)
    for bush in bushes:
        bush.draw(win)
    
    score_label = STAT_FONT.render("Score: " + str(score), 1, (169, 169, 169))
    win.blit(score_label, (WIN_WIDTH - score_label.get_width() - 15, 10))
    
    pygame.display.update()

def main():
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    clock = pygame.time.Clock()

    dino = Dino(200, DINO_BASE)
    base = Base(FLOOR)
    bushes = [Bush(600), Bush(1000), Bush(1400)]
    
    score = 0

    run = True
    while run:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    dino.jump()
        dino.move()
        base.move()

        add_bush = False
        bushes_to_remove = []
        for bush in bushes:
            if bush.collide(dino):
                run = False
            # to check if the bush has left the game window
            if bush.x[bush.obstacle_size - 1] + bush_imgs[bush.obstacle_size - 1].get_width() < 0:
                bushes_to_remove.append(bush)

            if not bush.passed and bush.x[bush.obstacle_size - 1] < dino.x:
                bush.passed = True
                add_bush = True
                score += 1
            
            bush.move()
        
        if add_bush:
            bushes.append(Bush(bushes[len(bushes) - 1].x[bushes[len(bushes) - 1].obstacle_size - 1] + 400))
        for bush in bushes_to_remove:
            bushes.remove(bush)

        draw_window(win, dino, base, bushes, score)

    pygame.quit()
    quit()

main()
