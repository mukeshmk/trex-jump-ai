import os
import time
import neat
import random
import pickle

#pygame version number and welcome message hidden.
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame

# initiallise font
pygame.font.init()

GEN = 0

WIN_WIDTH = 1300
WIN_HEIGHT = 500
FLOOR = 350
DINO_BASE = 282.5

WHITE = (255, 255, 255)

dino_imgs = [pygame.transform.scale2x(pygame.image.load(os.path.join("images", "dino-0" + str(x) + ".png"))) for x in range(1, 3)]
bush_imgs = [pygame.transform.scale2x(pygame.image.load(os.path.join("images", "bush-0" + str(x) + ".png"))) for x in range(1, 4)]
base_img = pygame.transform.scale2x(pygame.image.load(os.path.join("images", "base.png")))

STAT_FONT = pygame.font.SysFont("comicsans", 50)

local_dir = os.path.dirname(__file__)
model_dir = os.path.join(local_dir + 'model')
model_file = 'genome.pkl'

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
        # the velocity with which the t-rex moves up when it jumps
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

def draw_window(win, dinos, base, bushes, score, gen):
    base.draw(win)

    for dino in dinos:
        dino.draw(win)

    for bush in bushes:
        bush.draw(win)
    
    score_label = STAT_FONT.render("Score: " + str(score), 1, (169, 169, 169))
    win.blit(score_label, (WIN_WIDTH - score_label.get_width() - 15, 10))

    if gen > 0:
        # generation count
        gen_label = STAT_FONT.render("Gen: " + str(gen), 1, (169, 169, 169))
        win.blit(gen_label, (10, 10))

        # alive
        alive_label = STAT_FONT.render("Alive: " + str(len(dinos)), 1, (169, 169, 169))
        win.blit(alive_label, (10, 50))
    
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

        draw_window(win, [dino], base, bushes, score, 0)

    pygame.time.wait(2000)
    pygame.quit()
    quit()


def eval_genome(genomes, config):
    global GEN
    GEN += 1

    nets = []
    ge = []
    dinos = []

    for _, g in genomes:
        # creates a neural network for the genome (dinos[i] in one generation)
        # eval_genome function is called multiple times for each generation
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        # creating a dino object to be kept track off
        dinos.append(Dino(200, DINO_BASE))
        # initalizing the fitness value of the dino
        g.fitness = 0
        ge.append(g)

    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    clock = pygame.time.Clock()

    base = Base(FLOOR)
    bushes = [Bush(600), Bush(1000), Bush(1400)]
    
    score = 0

    run = True
    while run:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()

        # determine which bush on the screen for neural network input
        bush_ind = 0
        if len(dinos) > 0 and len(bushes) > 1 :
            for i, dist in enumerate([bush.x[0] - dinos[0].x for bush in bushes]):
                if dist > 0:
                    bush_ind = i
                    break
        else:
            run = False
            break
        
        for x, dino in enumerate(dinos):
            # give each dino a fitness of 0.1 for each frame it stays alive
            ge[x].fitness += 0.1
            dino.move()

            # the input to the neural network is dino location, the bush location which is right infront of it and
            # the length of the bush and using this the network determine whether the dino has to jump or not
            output = nets[x].activate((dino.y, abs(dino.x - bushes[bush_ind].x[0]), bushes[bush_ind].obstacle_size))

            # using a tanh activation function so result will be between -1 and 1. if over 0.5 jump
            # check config file [DefaultGenome] for details
            # output from the nn is always a list of output values, in our case we have only one output so output[0]
            if output[0] > 0.5:
                dino.jump()

        base.move()

        add_bush = False
        bushes_to_remove = []

        for bush in bushes:
            for x, dino in enumerate(dinos):
                if bush.collide(dino):
                    # reduced the fitness of the dino as it has collided
                    ge[x].fitness -= 1
                    # removing the dino, it's nn and it's genome from the list
                    dinos.pop(x)
                    nets.pop(x)
                    ge.pop(x)

                if not bush.passed and bush.x[bush.obstacle_size - 1] < dino.x:
                    bush.passed = True
                    add_bush = True

            # to check if the bush has left the game window
            if bush.x[bush.obstacle_size - 1] + bush_imgs[bush.obstacle_size - 1].get_width() < 0:
                bushes_to_remove.append(bush)
            
            bush.move()
        
        if add_bush:
            score += 1
            # increasing fitness of dino as it passes threw the bushes
            for g in ge:
                g.fitness+=5
            bushes.append(Bush(bushes[len(bushes) - 1].x[bushes[len(bushes) - 1].obstacle_size - 1] + 400))
        for bush in bushes_to_remove:
            bushes.remove(bush)

        draw_window(win, dinos, base, bushes, score, GEN)

        # break if score gets large enough
        if score >= 30:
            break


def run(config_file):
    # loading the config file and it's details with the headings:
    # [DefaultGenome], [DefaultReproduction], [DefaultSpeciesSet], [DefaultStagnation]
    # [NEAT] is not required to be mentioned as it's a mandatory config
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_file)

    # this is used to set the population details from the config file
    p = neat.Population(config)

    # this is used to give the output
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    if os.path.exists(model_dir + '/' + model_file):
        genomes = []
        with open(model_dir + '/' + model_file, 'rb') as f:
            genomes = [(1, pickle.load(f))]
        eval_genome(genomes, config)
    else :
        # represents the no of generations to run the fitness funtion
        generations = 50
        # the "main" function is our fitness function
        # the function has to be modified to run for more than one bird
        # i.e., the entire population in that generation
        # calling it eval_genome and rewriting the function
        winner = p.run(eval_genome, generations)
        if not os.path.exists(model_dir):
            os.makedirs(model_dir)
        with open(model_dir + '/' + model_file, 'wb') as f:
            pickle.dump(p.best_genome, f)

        # show final stats
        print('\nBest genome:\n{!s}'.format(winner))


if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_file = os.path.join(local_dir + 'config-feedforward.txt')
    run(config_file)
