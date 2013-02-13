#! /usr/bin/env python

from __future__ import division

import pygame
import numpy
import noise
import random

pygame.init()

FRAMES_PER_SECOND = 60

SCREEN_WIDTH    = 800
SCREEN_HEIGHT   = 800
SCREEN_SIZE     = (SCREEN_WIDTH, SCREEN_HEIGHT)

WHITE       = numpy.asarray((255, 255, 255))
BLACK       = numpy.asarray((0, 0, 0))
GRAY        = numpy.asarray((128, 128, 128))
BROWN       = numpy.asarray((64, 64, 25))
GREEN       = numpy.asarray((25, 128, 25))
BEIGE       = numpy.asarray((128, 128, 25))
BLUE        = numpy.asarray((25, 25, 128))
DARK_GREEN  = numpy.asarray((25, 68, 25))
DARK_BLUE   = numpy.asarray((25, 25, 64))

def init():
    global screen, terrain, font, clock
    screen = pygame.display.set_mode(SCREEN_SIZE)
    terrain_size = (400, 400)
    terrain = generate_terrain(terrain_size, seed=2)
    font = pygame.font.Font(pygame.font.get_default_font(), 12)
    clock = pygame.time.Clock()

def generate_terrain(size, seed=0):
    random.seed(seed)
    (width, height) = size
    data = numpy.ndarray((width, height, 3), dtype=int)

    threshold = numpy.vectorize(lambda x: x if x < 0.0 else 0.0)
    ground = 0.1
    water = threshold(generate_heightmap(size, 32, 8, 0.25))
    hills = 0.5 * (0.5 + 0.5 * generate_heightmap(size, 16, 8, 0.25))
    mountains = 0.5 + abs(generate_heightmap(size, 32, 8, 0.75))

    threshold = numpy.vectorize(lambda x: x if x > 0.0 else 0.0)
    hills_mask = 1 - water
    mountains_mask = threshold(generate_heightmap(size, 32, 8, 0.25))

    terrain = mountains_mask

    for i in xrange(width):
        for j in xrange(height):
            #color = terrain_color(terrain[i,j])
            color = terrain[i,j] * WHITE
            data[i,j] = color

    surface = pygame.Surface(size)
    pygame.surfarray.blit_array(surface, data)

    return surface

def generate_heightmap(size, freq=16, octaves=1, persistence=0.5):
    (width, height) = size
    data = numpy.ndarray((width, height))
    freq = freq * octaves
    base = random.randint(0, 512)
    for i in xrange(width):
        for j in xrange(height):
            h = noise.pnoise2(i / freq, j / freq, octaves, persistence, base=base)
            data[i,j] = h
    return data

def terrain_color(height):
    colors  = [DARK_BLUE, BLUE, BEIGE, GREEN, DARK_GREEN, BROWN, GRAY, WHITE]
    heights = [-0.1, 0.0, 0.01, 0.2, 0.4, 0.6, 0.7, 0.9]

    # Check lower bound
    if height < heights[0]:
        return colors[0]

    # Find interpolation positions
    i = 0
    while i < len(heights) - 1 and heights[i+1] < height:
        i += 1

    # Check upper bound
    if i == len(heights) - 1:
        return colors[-1]

    # Interpolate colors
    t = (height - heights[i]) / (heights[i+1] - heights[i])
    color = lerp(colors[i], colors[i+1], t)

    return color

def lerp(a, b, t):
    return (1 - t) * a + t * b

def process_input(event):
    global running
    if event.type == pygame.QUIT:
        running = False

def draw_frame():
    # Draw terrain
    pygame.transform.scale(terrain, (SCREEN_WIDTH, SCREEN_HEIGHT), screen)

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
