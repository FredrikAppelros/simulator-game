#! /usr/bin/env python

from __future__ import division

import numpy
import scipy
import pygame
import struct
import terrain_generator
import simulator
import entity

pygame.init()

FRAMES_PER_SECOND = 60

WINDOW_WIDTH    = 1024
WINDOW_HEIGHT   = 1024
SCREEN_WIDTH    = 128
SCREEN_HEIGHT   = 128
TERRAIN_WIDTH   = 2048
TERRAIN_HEIGHT  = 2048
VIEWPORT_WIDTH  = SCREEN_WIDTH
VIEWPORT_HEIGHT = int(SCREEN_HEIGHT * 3 / 4)
MINIMAP_WIDTH   = int(SCREEN_WIDTH / 4) - 1
MINIMAP_HEIGHT  = int(SCREEN_HEIGHT / 4) - 1
WINDOW_SIZE     = (WINDOW_WIDTH, WINDOW_HEIGHT)
SCREEN_SIZE     = (SCREEN_WIDTH, SCREEN_HEIGHT)
TERRAIN_SIZE    = (TERRAIN_WIDTH, TERRAIN_HEIGHT)
VIEWPORT_SIZE   = (VIEWPORT_WIDTH, VIEWPORT_HEIGHT)
MINIMAP_SIZE    = (MINIMAP_WIDTH, MINIMAP_HEIGHT)

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

overlay_on = False

viewport = pygame.Rect((0, 0), VIEWPORT_SIZE)

simulator = simulator.Simulator()

def init():
    global window, map_, screen, minimap, terrain_data, map_data, font, clock, minimap_area

    print('Generating terrain...')
    terrain_data = terrain_generator.generate_terrain(TERRAIN_SIZE)
    print('Terrain generation complete')
    print('Coloring terrain...')
    map_data = generate_map(terrain_data)
    print('Terrain coloring complete')

    window = pygame.display.set_mode(WINDOW_SIZE)
    map_ = pygame.Surface(TERRAIN_SIZE)
    screen = pygame.Surface(SCREEN_SIZE)
    minimap = pygame.Surface(MINIMAP_SIZE)

    pygame.surfarray.blit_array(map_, map_data)

    pygame.display.set_caption('Sim')
    font = pygame.font.Font(pygame.font.get_default_font(), 12)
    clock = pygame.time.Clock()
    minimap_area = pygame.Rect((0, 0), MINIMAP_SIZE)

    screen.fill(GRAY)
    pygame.draw.line(screen, BLACK, (0, VIEWPORT_HEIGHT), (SCREEN_WIDTH, VIEWPORT_HEIGHT))

    simulator.start()

def generate_map(terrain):
    (width, height) = terrain.shape
    data = numpy.ndarray((width, height, 3), dtype=int)

    # Create colored map from terrain data
    for i in xrange(width):
        for j in xrange(height):
            color = terrain_color(terrain[i,j])
            data[i,j] = color

    return data

def save_map_as_image(filename, data):
    scipy.misc.imsave(filename + '.png', data.T)

def save_map_as_terrain(filename, data):
    def h(i):
        return struct.pack('h', i)
    h_max = numpy.iinfo(numpy.int16).max
    size = h(min(data.shape) - 1)
    xpts = h(data.shape[0])
    ypts = h(data.shape[1])
    height_scale = h(350)
    base_height = h(10)
    padding = h(0)
    with open(filename + '.ter', 'wb') as f:
        f.write('TERRAGENTERRAIN SIZE')
        f.write(size)
        f.write(padding)
        f.write('XPTS')
        f.write(xpts)
        f.write(padding)
        f.write('YPTS')
        f.write(ypts)
        f.write(padding)
        f.write('ALTW')
        f.write(height_scale)
        f.write(base_height)
        for val in data.flatten():
            f.write(h(val * h_max))
        f.write('EOF')

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
    global overlay_on, viewport

    if event.type == pygame.KEYUP:
        if event.key == ord('o'):
            overlay_on = not overlay_on
        elif event.key == ord('s'):
            save_map_as_image('map', map_data)
        elif event.key == ord('t'):
            save_map_as_terrain('map', terrain_data)
        elif event.key == pygame.K_ESCAPE:
            exit()
    elif (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 or
        # TODO mark here if pressed inside viewport
        event.type == pygame.MOUSEMOTION and pygame.mouse.get_pressed()[0]):
        (x, y) = event.pos
        x = int(x * (SCREEN_WIDTH / WINDOW_WIDTH))
        y = int(y * (SCREEN_HEIGHT / WINDOW_HEIGHT)) - (VIEWPORT_HEIGHT + 1)
        pos = (x, y)
        if minimap_area.contains(pygame.Rect(pos, (1, 1))):
            x = x * (TERRAIN_WIDTH / MINIMAP_WIDTH) - VIEWPORT_WIDTH / 2
            y = y * (TERRAIN_HEIGHT / MINIMAP_HEIGHT) - VIEWPORT_HEIGHT / 2
            (viewport.left, viewport.top) = (x, y)
    elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
        # TODO only place humans if the mouse pressed started inside
        # the viewport
        (x, y) = event.pos
        x = int(x * (SCREEN_WIDTH / WINDOW_WIDTH))
        y = int(y * (SCREEN_HEIGHT / WINDOW_HEIGHT))
        pos = (x, y)
        if pygame.Rect((0, 0), VIEWPORT_SIZE).contains(pos, (1, 1)):
            x = x + viewport.left
            y = y + viewport.top
            pos = (x, y)
            human = entity.Human(pos)
            simulator.add_entity(human)

    elif event.type == pygame.QUIT:
        exit()

def exit():
    global running

    simulator.stop()
    running = False

def process_state():
    global viewport

    (x, y) = (viewport.left, viewport.top)
    pressed = pygame.key.get_pressed()
    if pressed[pygame.K_UP]:
        y -= 2
    if pressed[pygame.K_DOWN]:
        y += 2
    if pressed[pygame.K_LEFT]:
        x -= 2
    if pressed[pygame.K_RIGHT]:
        x += 2

    x = max(x, 0)
    x = min(x, TERRAIN_WIDTH - VIEWPORT_WIDTH)
    y = max(y, 0)
    y = min(y, TERRAIN_HEIGHT - VIEWPORT_HEIGHT)
    (viewport.left, viewport.top) = (x, y)

def draw_frame():
    # Draw map
    screen.blit(map_, (0, 0), viewport)

    # Draw entities
    entities = simulator.get_entities(viewport)
    for entity in entities:
        draw_entity(entity)

    # Draw GUI
    pygame.transform.scale(map_, MINIMAP_SIZE, minimap)
    (x, y) = (viewport.left, viewport.top)
    position = ((x / TERRAIN_WIDTH) * MINIMAP_WIDTH - 1,
        (y / TERRAIN_HEIGHT) * MINIMAP_HEIGHT)
    size = ((VIEWPORT_WIDTH / TERRAIN_WIDTH) * MINIMAP_WIDTH + 2,
        (VIEWPORT_HEIGHT / TERRAIN_HEIGHT) * MINIMAP_HEIGHT + 2)
    rect = pygame.Rect(position, size)
    pygame.draw.rect(minimap, WHITE, rect, 1)
    screen.blit(minimap, (0, VIEWPORT_HEIGHT + 1))

    # Copy screen to window
    pygame.transform.scale(screen, WINDOW_SIZE, window)

    if overlay_on:
        # Display FPS
        fps = font.render('FPS: %d' % clock.get_fps(), True, WHITE)
        window.blit(fps, (10, 10))
        # Display simulator tick
        tick = font.render('Tick: %d' % simulator.tick, True, WHITE)
        window.blit(tick, (10, 26))

def draw_entity(entity):
    (x, y) = entity.pos
    x = x - viewport.left
    y = y - viewport.top
    pos = (x, y)
    screen.blit(entity.image, pos)

def main_loop():
    global running

    running = True
    while running:
        for event in pygame.event.get():
            process_input(event)
        process_state()

        draw_frame()

        pygame.display.flip()

        clock.tick(FRAMES_PER_SECOND)

init()
main_loop()
