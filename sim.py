#! /usr/bin/env python

from __future__ import division

import pygame
import map_generator

pygame.init()

FRAMES_PER_SECOND = 60

SCREEN_WIDTH    = 800
SCREEN_HEIGHT   = 800
SCREEN_SIZE     = (SCREEN_WIDTH, SCREEN_HEIGHT)

WHITE   = (255, 255, 255)

fps_on  = False

def init():
    global screen, map_data, map_, font, clock

    map_size = tuple(v // 4 for v in SCREEN_SIZE)
    map_data = map_generator.generate_map(map_size)
    map_ = pygame.Surface(map_size)
    pygame.surfarray.blit_array(map_, map_data)
    screen = pygame.display.set_mode(SCREEN_SIZE)
    pygame.display.set_caption('Sim')
    font = pygame.font.Font(pygame.font.get_default_font(), 12)
    clock = pygame.time.Clock()

def process_input(event):
    global running, fps_on
    if event.type == pygame.QUIT:
        running = False
    elif event.type == pygame.KEYUP:
        if event.key == ord('f'):
            fps_on = not fps_on
        if event.key == ord('s'):
            map_generator.save_map('map', map_data)
        elif event.key == 27:
            running = False

def draw_frame():
    # Draw map
    pygame.transform.scale(map_, (SCREEN_WIDTH, SCREEN_HEIGHT), screen)

    if fps_on:
        # Display FPS
        fps = font.render('FPS: %d' % clock.get_fps(), True, WHITE)
        screen.blit(fps, (10, 10))

def main_loop():
    global running
    running = True
    while running:
        for event in pygame.event.get():
            process_input(event)

        draw_frame()

        pygame.display.flip()

        clock.tick(FRAMES_PER_SECOND)

init()
main_loop()
