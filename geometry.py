from __future__ import division

import numpy as np

class BoundingBox(object):
    """
    Defines a bounding box.

    Parameters
    ----------
    x : numpy.ndarray
        Bottom left x-coordinate of the box
    y : numpy.ndarray
        Bottom left y-coordinate of the box
    w : numpy.ndarray
        Width of the box
    h : numpy.ndarray
        Height of the box

    Attributes
    ----------
    p0 : numpy.ndarray
        The bottom left point of the box
    p1 : numpy.ndarray
        The bottom right point of the box
    p2 : numpy.ndarray
        The top left point of the box
    p3 : numpy.ndarray
        The top right point of the box
    lines : numpy.ndarray
        The four line segments that comprises the bounding box

    """
    def __init__(self, x, y, w, h):
        self.p0 = np.asarray([x, y])
        self.p1 = np.asarray([x + w, y])
        self.p2 = np.asarray([x, y + h])
        self.p3 = np.asarray([x + w, y + h])
        self.lines = [
            [self.p0, self.p1],
            [self.p0, self.p2],
            [self.p2, self.p3],
            [self.p1, self.p3],
        ]

    def intersect(self, a, b):
        """
        Returns a list of intersections between a line segment and the box.

        Parameters
        ----------
        a : numpy.ndarray
            First point on the line
        b : numpy.ndarray
            Second point on the line

        Returns
        -------
        p : numpy.ndarray
            Point of intersection if the line and box intersects, else
            None

        """
        intersections = []
        for line in self.lines:
            (c, d) = line
            p = intersect(c, d, a, b)
            if p is not None:
                intersections.append(p)
        return intersections

    @property
    def center(self):
        return np.mean([self.p0, self.p3], axis=0)

    @property
    def points(self):
        return np.asarray([self.p0, self.p1, self.p2, self.p3])

    def inside(self, p):
        """
        Finds out if a point is located inside the box.

        Parameters
        ----------
        p : numpy.ndarray
            The point

        Returns
        -------
        status : bool
            True if the point is inside the box, False otherwise

        """
        return np.all(p >= self.p0) and np.all(p <= self.p3)

    def __contains__(self, item):
        return self.inside(item)

def intersect(a, b, c, d):
    """
    Calculates the intersection between two line segements.

    Parameters
    ----------
    a : numpy.ndarray
        First point in the first line
    b : numpy.ndarray
        Second point in the first line
    c : numpy.ndarray
        First point in the second line
    d : numpy.ndarray
        Second point in the second line

    Returns
    -------
    p : numpy.ndarray
        Point of intersection if the two segments intersects, else None

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
    k1p = perp(k1)
    k2p = perp(k2)
    # k2p . (m2 - m1) = k2p . k1 * t
    # k1p . (m1 - m2) = k1p . k2 * u
    # thus we get
    # t = (k2p . (m2 - m1)) / (k2p . k1)
    # u = (k1p . (m1 - m2)) / (k1p . k2)
    de_t = np.dot(k2p, k1)
    de_u = np.dot(k1p, k2)
    if de_t is 0.0 or de_u is 0.0:
        # The line segments are parallel
        return None
    t = np.dot(k2p, (m2 - m1)) / de_t
    u = np.dot(k1p, (m1 - m2)) / de_u
    # if t (- [0, 1] and u (- [0, 1] then the segments intersect
    if 0 <= t <= 1 and 0 <= u <= 1:
        # intersection can be found at m1 + k1 * t
        return m1 + k1 * t
    return None

def perp(v):
    """
    Returns a vector that is perpendicular to the supplied vector.

    Parameters
    ----------
    v : array-like
        The supplied vector

    Returns
    -------
    perp : numpy.ndarray
        A vector that is perpendicular to the supplied vector

    """
    return np.asarray([-v[1], v[0]])

