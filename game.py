from os import system, makedirs
from os.path import exists
from sys import exit
from random import randint
from math import sin
PACKAGES = ['pygame']
system('python -m pip install --upgrade pip')
for package in PACKAGES:
    system(f'pip install {package}')

import pygame
pygame.init()
pygame.mixer.init()

#Main Window
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 800
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('The Poilièvre Game')
pygame.display.set_icon(pygame.image.load('assets/Interface/Circle.png'))

highest_score = 0
if exists('data/highest_score.csv'):
    with open('data/highest_score.csv', 'rt') as f:
        highest_score = int(f.read())
        f.close()
score = 0

def get_background():
    background_img = pygame.image.load('assets/Background/Blue.png')
    _, _, width, height = background_img.get_rect()
    tiles = []

    for i in range(SCREEN_WIDTH // width + 1):
        for j in range(SCREEN_HEIGHT // height + 1):
            pos = [i * width, j * height]
            tiles.append(pos)
    return tiles, background_img

def draw_background(surface, background, bg_image):
    for tile in background:
        surface.blit(bg_image, tile)

def sine(speed: float, time: int, how_far: float, overall_y: int) -> int:
    t = pygame.time.get_ticks() / 2 % time
    y = sin(t / speed) * how_far + overall_y
    return int(y)

font = pygame.font.Font('assets/custom-font.ttf', 40)
def draw_score():
    y = sine(200.0, 1280, 10.0, 40)
    show_score = font.render(str(score), True, (0, 0, 0))
    score_rect = show_score.get_rect(center=((SCREEN_WIDTH // 2) - 7.5, y + 30))
    screen.blit(pygame.image.load("assets/scoreboard.png").convert_alpha(), ((SCREEN_WIDTH // 2) - 75, y))
    screen.blit(show_score, score_rect)

def draw_highest_score():
    show_score = font.render(str(highest_score), True, (0, 0, 0))
    rect = show_score.get_rect()
    if highest_score < 10: 
        rect.x = (SCREEN_WIDTH // 2)
    elif highest_score < 100:
        rect.x = (SCREEN_WIDTH // 2) - 15
    else:
        rect.x = (SCREEN_WIDTH // 2) - 25
    rect.y = 75
    screen.blit(show_score, rect)

#CLASSES
class Player(pygame.sprite.Sprite):

    def __init__(self, x):
        pygame.sprite.Sprite.__init__(self)
        self.x = x
        self.image = pygame.image.load('assets/Player/hand.png')
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = 600

    def move(self):
        mouse_pos = pygame.mouse.get_pos()[0]
        if mouse_pos < self.rect.x: self.rect.x -= int(self.rect.x - mouse_pos)
        elif self.rect.x < 500: self.rect.x += int(mouse_pos - self.rect.x)

    def draw(self): screen.blit(self.image, self.rect)
        

class Money(pygame.sprite.Sprite):

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale_by(pygame.image.load('assets/Player/money.png'), 0.15)
        self.rect = self.image.get_rect()
        self.rect.y = 660

    def follow(self, sprite): self.rect.x = sprite.rect.x + 27.5
    def draw(self): screen.blit(self.image, self.rect)
    def tax(self): self.kill()

class Flag(pygame.sprite.Sprite):
    def __init__(self, speed):
        pygame.sprite.Sprite.__init__(self)
        self.speed = speed
        
        self.image = pygame.transform.scale_by(pygame.image.load('assets/Flag.png'), 0.25)
        self.rect = self.image.get_rect()
        self.rect.y = -100
        self.rect.x = randint(0, SCREEN_WIDTH-100)
    
    def glide(self): self.rect.y += self.speed
    def draw(self): screen.blit(self.image, self.rect)
    def check(self, player): 
        if self.rect.colliderect(player.rect): return True



#Main Loop
player = Player(0)
bill = pygame.sprite.Group()
flags = pygame.sprite.Group()
flag_speed = 10

#Menu
menu_ui = pygame.image.load('assets/Interface/Menu/Menu.png')
menu_ui_rect = menu_ui.get_rect()

running = True
menu = True
pygame.mixer.music.load('assets/GrosBonSens.mp3')
pygame.mixer.music.play()
pygame.mixer.music.set_volume(1)
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            break
        if event.type == pygame.KEYDOWN and menu:
            menu = False
            bill.add(Money())
            for i in range(2):
                flags.add(Flag(flag_speed))

    #Draw background
    background, bg_image = get_background()
    draw_background(screen, background, bg_image)

    if menu: 
        screen.blit(menu_ui, menu_ui_rect)
        draw_highest_score()
    else:
        player.move()
        player.draw()
        for money in bill:
            money.follow(player)
            money.draw()
        draw_score()
        #Flags
        for flag in flags:
            flag.glide()
            flag.draw()
            if flag.rect.y > SCREEN_HEIGHT + 100:
                flag.kill()
                flags.add(Flag(flag_speed))
                score += 1
            for argent in bill:
                if flag.check(argent) == True:
                    bill.empty()
                    flags.empty()
                    flags.add(Flag(flag_speed))
                    pygame.mixer.music.load('assets/GrosBonSens.mp3')
                    pygame.mixer.music.play()
                    menu = True
                    if not exists('data'): makedirs('data')
                    if score > highest_score:
                        with open("data/highest_score.csv", 'wt') as hsc:
                            hsc.write(str(score))
                            hsc.close()
                        highest_score = score
                        score = 0
    
    pygame.display.update()
pygame.quit()
exit()