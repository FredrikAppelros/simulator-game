#! /usr/bin/env python

from __future__ import division

import numpy
import pygame
import terrain_generator

pygame.init()

FRAMES_PER_SECOND = 60

SCREEN_WIDTH    = 800
SCREEN_HEIGHT   = 800
SCREEN_SIZE     = (SCREEN_WIDTH, SCREEN_HEIGHT)

DEFAULT_SIZE = (800, 800)

WHITE       = numpy.asarray((255, 255, 255))
BLACK       = numpy.asarray((25, 25, 25))
RED         = numpy.asarray((128, 25, 25))
GRAY        = numpy.asarray((128, 128, 128))
BROWN       = numpy.asarray((64, 64, 25))
GREEN       = numpy.asarray((25, 128, 25))
BEIGE       = numpy.asarray((128, 128, 25))
BLUE        = numpy.asarray((25, 25, 128))
DARK_GREEN  = numpy.asarray((25, 68, 25))
DARK_BLUE   = numpy.asarray((25, 25, 64))

fps_on  = False

def init():
    global screen, terrain_data, map_data, map_, font, clock

    scale = 8
    terrain_size = tuple(d // scale for d in SCREEN_SIZE)
    terrain_data = terrain_generator.generate_terrain(terrain_size, scale)
    map_data = generate_map(terrain_data)
    map_ = pygame.Surface(terrain_size)
    pygame.surfarray.blit_array(map_, map_data)
    screen = pygame.display.set_mode(SCREEN_SIZE)
    pygame.display.set_caption('Sim')
    font = pygame.font.Font(pygame.font.get_default_font(), 12)
    clock = pygame.time.Clock()

def generate_map(terrain):
    (width, height) = terrain.shape
    data = numpy.ndarray((width, height, 3), dtype=int)

    # Create colored map from terrain data
    for i in xrange(width):
        for j in xrange(height):
            color = terrain_color(terrain[i,j])
            data[i,j] = color

    return data

def height_color(height):
    if height < 0:
        return lerp(BLUE, BLACK, height + 1)
    else:
        return lerp(BLACK, RED, height)

def terrain_color(height):
    colors  = [DARK_BLUE, BLUE, BEIGE, GREEN, DARK_GREEN, BROWN, GRAY, WHITE]
    heights = [-0.1, 0.0, 0.1, 0.2, 0.4, 0.5, 0.7, 0.8]

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
    global running, fps_on
    if event.type == pygame.QUIT:
        running = False
    elif event.type == pygame.KEYUP:
        if event.key == ord('f'):
            fps_on = not fps_on
        if event.key == ord('s'):
            map_generator.save_map_as_image('map', map_data)
        if event.key == ord('t'):
            map_generator.save_map_as_terrain('map', terrain_data)
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
