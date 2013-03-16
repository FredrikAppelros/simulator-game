from __future__ import division

import noise
import geometry as geo
import numpy as np

from voronoi import voronoi

class Map(object):
    def __init__(self, size, num_points=2048, seed=None):
        self.num_points     = num_points
        self.size           = size
        self.tiles          = []
        self.random_state   = np.random.RandomState(seed)

        self._generate()

    def _generate(self):
        points = _generate_random_points(self.num_points, self.size,
            self.random_state)
        (w, h) = self.size
        bbox = geo.BoundingBox(0, 0, w, h)
        points = _voronoi_relaxation(points, bbox)
        (self.polygons, self.vertices, self.edges) = voronoi(points, bbox)
        self._generate_landmass()
        #self._tileify()

    def _generate_landmass(self):
        offset = np.asarray(self.size) * self.random_state.rand(2)

        def land(p):
            n = (noise.snoise2(p[0] + offset[0], p[1] + offset[1], 8, 0.5) + 1) / 2
            return n > 0.3 * (1 + np.linalg.norm(p) ** 2)

        def fill_ocean(polygon):
            for neighbor in polygon.neighbors:
                if not neighbor.land and not neighbor.ocean:
                    neighbor.ocean = True
                    fill_ocean(neighbor)

        for vertex in self.vertices:
            p = 2 * vertex.point / np.asarray(self.size) - 1
            vertex.land = land(p)

        for polygon in self.polygons:
            if len([v for v in polygon.vertices if v.land]) >= 0.7 * len(polygon.vertices):
                polygon.land = True
            else:
                polygon.land = False

        for polygon in self.polygons:
            if polygon.border:
                polygon.ocean = True
            else:
                polygon.ocean = False

        for polygon in self.polygons:
            if polygon.border:
                fill_ocean(polygon)

def _generate_random_points(num, size, random_state):
    points = random_state.rand(num, 2)
    points[:,0] *= size[0]
    points[:,1] *= size[1]
    return points

def _voronoi_relaxation(points, bbox):
    for i in range(2):
        (polygons, vertices, edges) = voronoi(points, bbox)
        for (i, polygon) in enumerate(polygons):
            p = polygon.vertices[0].point.copy()
            for v in polygon.vertices[1:]:
                p += v.point
            p /= len(polygon.vertices)
            points[i] = p
    return points

