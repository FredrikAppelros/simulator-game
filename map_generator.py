from __future__ import division

import numpy
import noise
import random
import scipy.ndimage

DEFAULT_SIZE = (800, 800)

WHITE       = numpy.asarray((255, 255, 255))
GRAY        = numpy.asarray((128, 128, 128))
BROWN       = numpy.asarray((64, 64, 25))
GREEN       = numpy.asarray((25, 128, 25))
BEIGE       = numpy.asarray((128, 128, 25))
BLUE        = numpy.asarray((25, 25, 128))
DARK_GREEN  = numpy.asarray((25, 68, 25))
DARK_BLUE   = numpy.asarray((25, 25, 64))

def save_map(filename, data):
    scipy.misc.imsave(filename + '.png', data.T)

def generate_map(size):
    (width, height) = size
    terrain = generate_terrain(size)
    data = numpy.ndarray((width, height, 3), dtype=int)

    # Create colored map from terrain data
    for i in xrange(width):
        for j in xrange(height):
            color = terrain_color(terrain[i,j])
            data[i,j] = color

    return data

def generate_terrain(size, seed=None):
    if seed:
        random.seed(seed)

    scale = min(size) / min(DEFAULT_SIZE)

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

