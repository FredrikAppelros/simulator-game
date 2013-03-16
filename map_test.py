#! /usr/bin/env python

from __future__ import division

import pygame
import random

from map_generator import Map

pygame.init()

FRAMES_PER_SECOND = 60

SCREEN_WIDTH    = 800
SCREEN_HEIGHT   = 800
SCREEN_SIZE     = (SCREEN_WIDTH, SCREEN_HEIGHT)

BLACK   = pygame.Color(0, 0, 0, 255)
WHITE   = pygame.Color(255, 255, 255, 255)
LAND    = pygame.Color(192, 192, 0, 255)
LAKE    = pygame.Color(64, 64, 255, 255)
OCEAN   = pygame.Color(0, 0, 128, 255)

def init():
    global screen, clock, map_

    screen = pygame.display.set_mode(SCREEN_SIZE)
    clock = pygame.time.Clock()
    seed = random.randint(0, 2**(8 * 4))
    print seed
    map_ = Map(SCREEN_SIZE, 2048, seed)

    pygame.display.set_caption('Map test')

def process_input(event):
    global running
    if event.type == pygame.QUIT or event.type == pygame.KEYUP and event.key == 27:
        running = False

def draw_frame():
    for polygon in map_.polygons:
        if polygon.ocean:
            color = OCEAN
        elif polygon.land:
            color = LAND
        else:
            color = LAKE
        pygame.draw.polygon(screen, color, polygon.points, 0)
    for edge in map_.edges:
        pygame.draw.line(screen, BLACK, edge.v0.point, edge.v1.point, 3)

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

