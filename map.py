from __future__ import division

import numpy as np
import scipy.spatial
import matplotlib.pyplot as plt

class Map(object):
    def __init__(self, size, num_points=300, seed=None):
        self.num_points     = num_points
        self.size           = size
        self.tiles          = []
        self.random_state   = np.random.RandomState(seed)

        self._generate()

    def _generate(self):
        points = _generate_random_points(self.num_points, self.size)
        points = _voronoi_relaxation(points)

def _generate_random_points(num, size):
    points = np.random.rand(num, 2)
    points[:,0] *= size[0]
    points[:,1] *= size[1]
    return points

def _voronoi_relaxation(points):
    _voronoi(points)

def _voronoi(points):
    vor = scipy.spatial.Voronoi(points)
    for simplex in vor.ridge_vertices:
        simplex = np.asarray(simplex)
        if np.any(simplex < 0):
            pass

def _intersect(a, b, c, d):
    """
    Calculates the intersection between two line segements.

    Arguments
    ---------
    a   - first point in the first line
    b   - second point in the first line
    c   - first point in the second line
    d   - second point in the second line

    Returns
    -------
    p   - point of intersection if the two segments intersect, else None
    """
    # first line: m1 + k1 * t = a + (b - a) * t
    m1 = a
    k1 = b - a
    # second line: m2 + k2 * u = c + (d - c) * u
    m2 = c
    k2 = d - c
    # intersection: m1 + k1 * t = m2 + k2 * u
    # eliminate parts of this equation by taking the dot product of
    # this and vectors perpendicular to k1 and k2
    k1p = _perp(k1)
    k2p = _perp(k2)
    # k2p . (m2 - m1) = k2p . k1 * t
    # k1p . (m1 - m2) = k1p . k2 * u
    # thus we get
    # t = (k2p . (m2 - m1)) / (k2p . k1)
    # u = (k1p . (m1 - m2)) / (k1p . k2)
    t = np.dot(k2p, (m2 - m1)) / np.dot(k2p, k1)
    u = np.dot(k1p, (m1 - m2)) / np.dot(k1p, k2)
    # if t (- [0, 1] and u (- [0, 1] then the segments intersect
    if 0 <= t <= 1 and 0 <= u <= 1:
        # intersection can be found at m1 + k1 * t
        return m1 + k1 * t
    return None

def _perp(v):
    """
    Returns a vector that is perpendicular to the argument vector
    """
    return np.asarray([-v[1], v[0]])

