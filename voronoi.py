import scipy.spatial

import geometry as geo
import numpy as np

class Polygon(object):
    def __init__(self, point):
        self.center     = point
        self.points     = []
        self.neighbors  = []
        self.vertices   = set()
        self.edges      = []
        self.border     = False

class Vertex(object):
    def __init__(self, point):
        self.point      = point
        self.neighbors  = []
        self.polygons   = set()
        self.edges      = []

class Edge(object):
    def __init__(self, d0, d1, v0, v1):
        self.d0     = d0
        self.d1     = d1
        self.v0     = v0
        self.v1     = v1

def voronoi(points, bbox):
    vor = scipy.spatial.Voronoi(points)

    polygons    = {}
    vertices    = {}
    edges       = {}

    # create the polygons
    for (i, p) in enumerate(vor.points):
        polygon = Polygon(p)
        polygons[i] = polygon

    # create the vertices
    for (i, v) in enumerate(vor.vertices):
        # only add vertices that are inside the bounding box
        if v in bbox:
            vertex = Vertex(v)
            vertices[i] = vertex

    # store index of next vertex
    next_vertex_index = i + 1

    # create the edges
    for (i, ps, vs) in zip(range(len(vor.ridge_points)),
        vor.ridge_points, vor.ridge_vertices):
        vs = np.asarray(vs)

        if np.any(vs < 0):
            # these edges are infinite
            # index of the existing vertex
            existing_index = vs[vs >= 0][0]
            # the existing vertex
            existing_vertex = vor.vertices[existing_index]
            # skip edge if both vertices are outside the bounding box
            if not existing_vertex in bbox:
                continue

            # calculate a new point on the border of the bounding box
            # and create a new vertex for the new point
            t = vor.points[ps[0]] - vor.points[ps[1]]
            t /= np.linalg.norm(t)
            n = geo.perp(t)
            p_mid = vor.points[ps].mean(axis=0)
            dir_ = np.sign(np.dot(p_mid - bbox.center, n)) * n
            length = bbox.points.ptp(axis=0).max()
            p_far = existing_vertex + length * dir_
            p_new = bbox.intersect(existing_vertex, p_far)[0]
            v_new = Vertex(p_new)
            vertices[next_vertex_index] = v_new

            # store the voronoi components of the edge
            v0 = vertices[existing_index]
            v1 = v_new

            next_vertex_index += 1
        else:
            # these edges are finite
            p0 = vor.vertices[vs[0]]
            p1 = vor.vertices[vs[1]]

            # find the intersections of the edge and the box
            isecs = bbox.intersect(p0, p1)

            # skip edge if it is completely outside the box
            if not p0 in bbox and not p1 in bbox and not isecs:
                continue

            # shorten the edge if needed (if one of the vertices is outside
            # the bounding box)
            if isecs:
                # add the new vertices of the shortened edges
                new_vs = []
                for p in isecs:
                    v_new = Vertex(p)
                    vertices[next_vertex_index] = v_new
                    new_vs.append(v_new)
                    next_vertex_index += 1

                # store the voronoi components of the edge
                if p0 in bbox:
                    v0 = vertices[vs[0]]
                    v1 = new_vs[0]
                elif p1 in bbox:
                    v0 = new_vs[0]
                    v1 = vertices[vs[1]]
                else:
                    v0 = new_vs[0]
                    v1 = new_vs[1]
            else:
                # store the voronoi components of the edge
                v0 = vertices[vs[0]]
                v1 = vertices[vs[1]]

        # store the delaunay components of the edge
        d0 = polygons[ps[0]]
        d1 = polygons[ps[1]]

        edge = Edge(d0, d1, v0, v1)
        edges[i] = edge

        # add connections to the polygons
        d0.neighbors.append(d1)
        d1.neighbors.append(d0)
        d0.vertices.add(v0)
        d0.vertices.add(v1)
        d1.vertices.add(v0)
        d1.vertices.add(v1)
        d0.edges.append(edge)
        d1.edges.append(edge)

        # add connections to the vertices
        v0.neighbors.append(v1)
        v1.neighbors.append(v0)
        v0.polygons.add(d0)
        v0.polygons.add(d1)
        v1.polygons.add(d0)
        v1.polygons.add(d1)
        v0.edges.append(edge)
        v1.edges.append(edge)

    # store index of next edge
    next_edge_index = i + 1

    # find polygons that has vertices with only one edge and create
    # new connecting edges between the vertices and at the same time
    # mark them as border polygons
    for index in polygons:
        polygon = polygons[index]
        unconnected = []
        for vertex in polygon.vertices:
            if len([e for e in vertex.edges if e.d0 is polygon or e.d1 is
                polygon]) == 1:
                unconnected.append(vertex)
        if unconnected:
            polygon.border = True
            while unconnected:
                v0 = unconnected.pop()
                if len(unconnected) == 1:
                    v1 = unconnected.pop()
                else:
                    v1 = (v for v in unconnected if v.point[0] == v0.point[0] or
                        v.point[1] == v0.point[1]).next()
                    unconnected.remove(v1)
                p0 = v0.point
                p1 = v1.point
                if p0[0] == p1[0] or p0[1] == p1[1]:
                    edge = Edge(polygon, None, v0, v1)
                    edges[next_edge_index] = edge
                    polygon.edges.append(edge)
                    v0.neighbors.append(v1)
                    v1.neighbors.append(v0)
                    v0.edges.append(edge)
                    v1.edges.append(edge)

                    next_edge_index += 1
                else:
                    p = (p for p in bbox.points if p0[0] == p[0] and p1[1] == p[1]
                        or p1[0] == p[0] and p0[1] == p[1]).next()
                    v_new = Vertex(p)
                    vertices[next_vertex_index] = v_new
                    polygon.vertices.add(v_new)

                    for v in [v0, v1]:
                        edge = Edge(polygon, None, v, v_new)
                        edges[next_edge_index] = edge
                        polygon.edges.append(edge)
                        v.neighbors.append(v_new)
                        v_new.neighbors.append(v)
                        v_new.polygons.add(polygon)
                        v.edges.append(edge)
                        v_new.edges.append(edge)

                        next_edge_index += 1

                    next_vertex_index += 1

    # create point lists for the polygons in CCW order
    for index in polygons:
        polygon = polygons[index]
        curr_edge = polygon.edges[0]
        p0 = curr_edge.v0.point
        p1 = curr_edge.v1.point
        if p0[0] < p1[0]:
            start_vertex = curr_edge.v0
            curr_vertex = curr_edge.v1
        elif p1[0] < p0[0]:
            start_vertex = curr_edge.v1
            curr_vertex = curr_edge.v0
        elif p0[1] < p1[1]:
            start_vertex = curr_edge.v0
            curr_vertex = curr_edge.v1
        else:
            start_vertex = v1
            curr_vertex = v0
        polygon.points.append(start_vertex.point)
        while curr_vertex is not start_vertex:
            polygon.points.append(curr_vertex.point)
            curr_edge = (e for e in curr_vertex.edges if e is not curr_edge and
                (e.d0 is polygon or e.d1 is polygon)).next()
            curr_vertex = curr_edge.v0 if curr_edge.v0 is not curr_vertex else curr_edge.v1

    # transform the dictionaries and sets into lists
    p_list = []
    v_list = []
    e_list = []
    for index in polygons:
        polygon = polygons[index]
        polygon.vertices = list(polygon.vertices)
        p_list.append(polygon)
    for index in vertices:
        vertex = vertices[index]
        vertex.polygons = list(vertex.polygons)
        v_list.append(vertex)
    for index in edges:
        e_list.append(edges[index])

    return (p_list, v_list, e_list)

