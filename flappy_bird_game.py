import pygame
from pygame.locals import *
import random
import sys

pygame.mixer.pre_init()
pygame.init()
font = pygame.font.Font('04B_19.ttf', 35)
font_smaller = pygame.font.Font('04B_19.ttf', 25)

# screen set up
screen_width = 432
screen_height = 768
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Flappy Bird')


# functions used in game
def score_check():
    global score
    global can_score
    if pipe_list:
        for pipe in pipe_list:
            if 120 < pipe.centerx < 130 and can_score:
                score += 1
                can_score = False
                sound_point.play()


def create_pipe():
    pipe_pos = random.randint(250, 600)
    bottom_pipe = pipe_surface.get_rect(midtop=(500, pipe_pos))
    top_pipe = pipe_down_surface.get_rect(midbottom=(500, pipe_pos - 160))
    return [bottom_pipe, top_pipe]


def rotate_bird(bird):
    new_bird = pygame.transform.rotozoom(bird, bird_fall_speed*-5, 1)
    return new_bird


def display_score(game_over, is_first):
    if game_over and is_first:
        high_score_surface = font.render(f'High Score: {high_score}', False, (255, 255, 255))
        high_score_rect = high_score_surface.get_rect(center=(216, 610))
        screen.blit(high_score_surface, high_score_rect)
    elif game_over:
        score_surface = font.render(f'Score: {score}', False, (255, 255, 255))
        score_rect = score_surface.get_rect(center=(216, 75))
        screen.blit(score_surface, score_rect)
        high_score_surface = font.render(f'High Score: {high_score}', False, (255, 255, 255))
        high_score_rect = high_score_surface.get_rect(center=(216, 610))
        screen.blit(high_score_surface, high_score_rect)
        restart_text = font_smaller.render(f'Click anywhere to restart', False, (255, 255, 255))
        screen.blit(restart_text, (50, 400))
    else:
        score_surface = font.render(str(score), False, (255, 255, 255))
        score_rect = score_surface.get_rect(center=(216, 75))
        screen.blit(score_surface, score_rect)


FPS = pygame.time.Clock()

# game variables
gravity = 0.25
bird_fall_speed = 0
active = False
score = 0
can_score = True
first_game = True
with open('high_score.txt', 'r') as f:
    high_score = int(f.read())

# images and objects
bg = pygame.transform.scale_by(pygame.image.load('sprites/background-day.png').convert(), 1.5)

start_screen = pygame.transform.scale_by(pygame.image.load('sprites/message.png').convert_alpha(), 1.5)
game_over_screen = pygame.transform.scale_by(pygame.image.load('sprites/gameover.png').convert_alpha(), 1.5)

pipe_surface = pygame.transform.scale_by(pygame.image.load('sprites/pipe-green.png').convert(), 1.5)
pipe_down_surface = pygame.transform.rotate(pipe_surface, 180)
pipe_list = []
SPAWNPIPE = pygame.USEREVENT + 1
pygame.time.set_timer(SPAWNPIPE, 2000)

floor = pygame.transform.scale_by(pygame.image.load('sprites/base.png').convert(), 1.5)
floor_x_pos = 0

# bird animation
bird_up = pygame.transform.scale_by(pygame.image.load('sprites/yellowbird-upflap.png').convert_alpha(), 1.5)
bird_mid = pygame.transform.scale_by(pygame.image.load('sprites/yellowbird-midflap.png').convert_alpha(), 1.5)
bird_down = pygame.transform.scale_by(pygame.image.load('sprites/yellowbird-downflap.png').convert_alpha(), 1.5)
bird_animation = [bird_down, bird_mid, bird_up]
bird_frame = 0
bird_surface = bird_animation[bird_frame]
bird_rect = bird_surface.get_rect(center=(125, 400))
BIRDFLAP = pygame.USEREVENT
pygame.time.set_timer(BIRDFLAP, 120)

# sounds
sound_flap = pygame.mixer.Sound('audio/wing.wav')
sound_flap.set_volume(0.1)
sound_hit = pygame.mixer.Sound('audio/hit.wav')
sound_hit.set_volume(0.5)
sound_point = pygame.mixer.Sound('audio/point.wav')
sound_point.set_volume(0.5)

while True:
    screen.blit(bg, (0, 0))
    # event handler
    for event in pygame.event.get():
        if event.type == QUIT:
            with open('high_score.txt', 'w') as f:
                f.write(str(high_score))
            pygame.quit()
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN and active:
            bird_fall_speed = 0
            bird_fall_speed -= 7
            sound_flap.play()
        if event.type == pygame.MOUSEBUTTONDOWN and not active:
            pipe_list.clear()
            bird_rect.center = (125, 384)
            bird_fall_speed = 0
            first_game = False
            active = True
            score = 0
            can_score = True
        if event.type == SPAWNPIPE:
            pipe_list.extend(create_pipe())
            can_score = True
        if event.type == BIRDFLAP:
            bird_frame = bird_frame + 1 if bird_frame < 2 else 0
    if active:
        # draws and moves bird
        bird_surface = bird_animation[bird_frame]
        bird_rect = bird_surface.get_rect(center=(125, bird_rect.centery))
        bird_fall_speed += gravity
        rotated_bird = rotate_bird(bird_surface)
        bird_rect.centery += bird_fall_speed
        if bird_rect.bottom >= 650 or bird_rect.bottom <= -100:
            active = False
            sound_hit.play()
        screen.blit(rotated_bird, bird_rect)

        # draws and moves pipes
        for index, pipe in enumerate(pipe_list):
            screen.blit(pipe_surface, pipe) if index % 2 == 0 else screen.blit(pipe_down_surface, pipe)
            pipe.centerx -= 3
            pipe_list = [pipe for pipe in pipe_list if pipe.right > -25]
            if bird_rect.colliderect(pipe):
                active = False
                sound_hit.play()

        score_check()
        display_score(False, first_game)
    else:
        if score > high_score:
            high_score = score
        display_score(True, first_game)
        screen.blit(start_screen, (78, 130)) if first_game else screen.blit(game_over_screen, (78, 300))

    # draws each element

    # draws and moves floor
    screen.blit(floor, (floor_x_pos, 655))
    screen.blit(floor, (floor_x_pos + 432, 655))
    if floor_x_pos <= -432:
        floor_x_pos = 0
    floor_x_pos -= 3
    pygame.display.update()
    FPS.tick(60)
