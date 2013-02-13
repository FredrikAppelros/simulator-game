#! /usr/bin/env python

from __future__ import division

import pygame
import numpy
import noise
import random
import scipy.ndimage

pygame.init()

FRAMES_PER_SECOND = 60

SCREEN_WIDTH    = 800
SCREEN_HEIGHT   = 400
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
    global screen, map_, font, clock
    map_ = generate_map()
    screen = pygame.display.set_mode(SCREEN_SIZE)
    font = pygame.font.Font(pygame.font.get_default_font(), 12)
    clock = pygame.time.Clock()

def generate_map():
    size = (width, height) = (800, 400)
    terrain = generate_terrain(size)
    data = numpy.ndarray((width, height, 3), dtype=int)

    for i in xrange(width):
        for j in xrange(height):
            color = terrain_color(terrain[i,j])
            data[i,j] = color

    map_ = pygame.Surface(size)
    pygame.surfarray.blit_array(map_, data)

    # Output map to file
    scipy.misc.imsave('map.png', data.T)

    return map_

def generate_terrain(size, seed=None):
    if seed:
        random.seed(seed)

    scale = min(size) / min(SCREEN_SIZE)

    threshold_pos_bin   = numpy.vectorize(lambda x: 1 if x > 0.0 else 0.0)
    threshold_pos       = numpy.vectorize(lambda x: x if x > 0.0 else 0.0)
    threshold_neg       = numpy.vectorize(lambda x: x if x < 0.0 else 0.0)

    water_data      = generate_heightmap(size, scale * 64, 8, 0.25)
    hills_data      = generate_heightmap(size, scale * 32, 8, 0.25)
    mountains_data  = generate_heightmap(size, scale * 64, 8, 0.75)

    ground_level = 0.1
    water = threshold_neg(water_data)
    hills = 0.5 * (0.5 + 0.5 * hills_data)
    mountains = 1.0 + abs(mountains_data)

    land_mask = threshold_pos(scipy.ndimage.filters.gaussian_filter(
        threshold_pos_bin(water_data) - ground_level, 4 / scale))
    mountains_mask = threshold_pos(generate_heightmap(size, scale * 64, 8, 0.25))

    terrain = ground_level + water + land_mask * (hills + mountains_mask * mountains)

    return terrain

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
    heights = [-0.1, 0.0, 0.01, 0.2, 0.4, 0.6, 0.7, 0.8]

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
    # Draw map
    pygame.transform.scale(map_, (SCREEN_WIDTH, SCREEN_HEIGHT), screen)

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
