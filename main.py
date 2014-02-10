#!usr/bin/env python3
import pygame
from sys import exit
from pygame.locals import *
import random

class Land(pygame.sprite.Sprite):
    def __init__(self,plane_img,land_rect,land_init_pos):
        pygame.sprite.Sprite.__init__(self)
        self.image = plane_img.subsurface(land_rect).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.topleft = land_init_pos
        self.speed = 1

    def move(self):
        self.rect.left -= self.speed

class Bird(pygame.sprite.Sprite):
    def __init__(self,plane_img,bird_rect,bird_init_pos):
        pygame.sprite.Sprite.__init__(self)
        self.image = []
        for i in range(len(bird_rect)):
            self.image.append(plane_img.subsurface(bird_rect[i]).convert_alpha())
        self.rect = bird_rect[0]
        self.rect.topleft = bird_init_pos
        self.img_index = 0
        self.is_hit = False
        self.speed = 3

    def flap(self):
        if self.rect.top <= 0:
            self.rect.top = 0
        else:
            self.rect.top -= self.speed

    def fall(self):
        if self.rect.top >= 364:
            self.rect.top = 364
        else:
            self.rect.bottom += self.speed*2

class Pipe(pygame.sprite.Sprite):
    def __init__(self,plane_img,pipe_rect,pipe_init_pos,is_down):
        pygame.sprite.Sprite.__init__(self)
        self.image = plane_img.subsurface(pipe_rect[is_down]).convert_alpha()
        self.rect = self.image.get_rect()
        if is_down:
            self.rect.topleft = pipe_init_pos
        else:
            self.rect.bottomleft = pipe_init_pos
        self.speed = 1

    def move(self):
        self.rect.left -= self.speed

SCREEN_WIDTH = 288
SCREEN_HEIGHT = 512

#initiate the game
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Flappy Bird')

# load sound effects
die_sound = pygame.mixer.Sound('assets/sounds/sfx_die.ogg')
hit_sound = pygame.mixer.Sound('assets/sounds/sfx_hit.ogg')
point_sound = pygame.mixer.Sound('assets/sounds/sfx_point.ogg')
flap_sound = pygame.mixer.Sound('assets/sounds/sfx_wing.ogg')
swooshing_sound = pygame.mixer.Sound('assets/sounds/sfx_swooshing.ogg')
die_sound.set_volume(0.3)
hit_sound.set_volume(0.3)
point_sound.set_volume(0.3)
flap_sound.set_volume(0.3)
swooshing_sound.set_volume(0.3)

#load images
#background
background = pygame.image.load('assets/gfx/background.png').convert()

plane_img = pygame.image.load('assets/gfx/atlas.png')
#bird
bird_rect = []
bird_rect.append(pygame.Rect(7,978,32,34)) 
bird_rect.append(pygame.Rect(63,978,32,34))
bird_rect.append(pygame.Rect(119,978,32,34))
#land
land_rect = pygame.Rect(584,0,336,112)
#pipe
pipe_rect = []
pipe_rect.append(pygame.Rect(112,646,52,320))
pipe_rect.append(pygame.Rect(168,646,52,320))
#gameover
gameover = pygame.image.load('assets/gfx/gameover.png')

PIPE_FREQUENCY = 192
FLAP_FREQUENCY = 0
MAX_CD = 15
FLAP_CD = MAX_CD
SCORE = 0   

GameIsPlaying = True
bird_init_pos = [96,200]
land0_init_pos = [0,400]
land1_init_pos = [336,400]
pipe_horizontal_pos = [288+i*144 for i in range(2)]

bird = Bird(plane_img,bird_rect,bird_init_pos)
lands = [Land(plane_img,land_rect,land0_init_pos),Land(plane_img,land_rect,land1_init_pos)]
pipes = []
# generate pipes
for H_pos in pipe_horizontal_pos:
    pipe_mid = random.randint(70, 130)
    pipe_up_pos = [H_pos,pipe_mid - 60]
    pipe_down_pos = [H_pos,pipe_mid + 60]
    pipe_up = Pipe(plane_img,pipe_rect,pipe_up_pos,0)
    pipe_down = Pipe(plane_img,pipe_rect,pipe_down_pos,1)
    pipes.append(pipe_up)
    pipes.append(pipe_down)

CLOCK = pygame.time.Clock()
while not bird.is_hit:
    CLOCK.tick(60)  # reset clock to make sure that max fps <= 60
    # update score
    PIPE_FREQUENCY -= 1
    if PIPE_FREQUENCY == 0:
        SCORE += 1
        PIPE_FREQUENCY = 144

    # movement of bird
    key_pressed = pygame.key.get_pressed()
    if FLAP_CD == MAX_CD: 
        if key_pressed[K_SPACE]:
            bird.flap()
            flap_sound.play()
            FLAP_CD -= 1
        else:bird.fall()
    else:
        bird.flap()
        if FLAP_CD == 0:FLAP_CD = MAX_CD
        else:FLAP_CD -= 1

    # move pipe back to the tail of the queue if out of window 
    pipe_mid = random.randint(70, 130)
    pipe_up_pos = [288,pipe_mid - 60]
    pipe_down_pos = [288,pipe_mid + 60]
    for i in range(4):
        pipes[i].move()
        if pygame.sprite.collide_rect(pipes[i],bird):
            bird.is_hit = True
            hit_sound.play()
            break
        if pipes[i].rect.right < 0:
            if i%2 == 0: pipes[i].rect.bottomleft = pipe_up_pos
            else: pipes[i].rect.topleft = pipe_down_pos

    # movement of land
    for land in lands:
        if pygame.sprite.collide_rect(land,bird):
            bird.is_hit = True
            hit_sound.play()
        if land.rect.right <= 0:
            land.rect.topleft = [336,400] 
        land.move()
    
    #draw background
    screen.fill(0)
    screen.blit(background, (0, 0))

    #draw bird,pipes and land
    screen.blit(bird.image[bird.img_index], bird.rect)
    if FLAP_FREQUENCY % 14 == 0: 
        bird.img_index += 1
        if bird.img_index == 3:bird.img_index = 0
    FLAP_FREQUENCY += 1
    if FLAP_FREQUENCY > 336:
        FLAP_FREQUENCY = 0
    for pipe in pipes:
        screen.blit(pipe.image,pipe.rect)
    for land in lands:
        screen.blit(land.image,land.rect)

    #draw score
    score_font = pygame.font.Font(None, 36)
    score_text = score_font.render(str(SCORE), True, (128, 128, 128))
    text_rect = score_text.get_rect()
    text_rect.topleft = [10, 10]
    screen.blit(score_text, text_rect)
    
    #update screen
    pygame.display.update()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

font = pygame.font.Font(None, 48)
text = font.render('Score: '+ str(SCORE), True, (255, 0, 0))
text_rect = text.get_rect()
text_rect.centerx = screen.get_rect().centerx
text_rect.centery = screen.get_rect().centery + 24
screen.blit(gameover, (0, 0))
screen.blit(text, text_rect)


while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
    pygame.display.update()
