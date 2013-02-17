from __future__ import division

import numpy
import noise
import random
import struct
import scipy.ndimage

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
    hills = 0.5 * (0.5 + 0.5 * hills_data)
    mountains = 0.3 + abs(mountains_data)

    land_mask = threshold_pos(scipy.ndimage.filters.gaussian_filter(
        threshold_pos_bin(water_data) - ground_level, 8 / scale))
    mountains_mask = threshold_pos(generate_heightmap(size, scale * 1, 8, 0.25) - 0.2)

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

