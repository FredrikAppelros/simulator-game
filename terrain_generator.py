from __future__ import division

import numpy
import noise
import random
import scipy.ndimage

def generate_terrain(size, scale=1.0, seed=None):
    if seed:
        random.seed(seed)

    threshold_pos_bin   = numpy.vectorize(lambda x: 1 if x > 0.0 else 0.0)
    threshold_pos       = numpy.vectorize(lambda x: x if x > 0.0 else 0.0)
    threshold_neg       = numpy.vectorize(lambda x: x if x < 0.0 else 0.0)

    water_data      = generate_heightmap(size, scale * 1, 8, 0.25)
    hills_data      = generate_heightmap(size, scale * 2, 6, 0.25)
    mountains_data  = generate_heightmap(size, scale * 16, 4, 0.75)

    ground_level = 0.1
    water = threshold_neg(water_data)
    hills = 0.25 + 0.25 * hills_data
    mountains = 0.6 + abs(mountains_data)

    land_mask = threshold_pos(scipy.ndimage.filters.gaussian_filter(
        threshold_pos_bin(water_data) - ground_level, 8 / scale))
    mountains_mask = 2 * threshold_pos(generate_heightmap(size, scale * 1, 8, 0.25) - 0.4)

    terrain = ground_level + water + land_mask * (hills + mountains_mask * mountains)

    return terrain

def generate_heightmap(size, freq=16, octaves=1, persistence=0.5):
    (width, height) = size
    data = numpy.ndarray((width, height))
    freq = freq * octaves
    offset_x = random.randint(0, 4096)
    offset_y = random.randint(0, 4096)
    for i in xrange(width):
        for j in xrange(height):
            h = noise.snoise2(offset_x + freq * i / 4096, offset_y + freq * j
                / 4096, octaves, persistence)
            data[i,j] = h
    return data

