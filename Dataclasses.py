# Author: Nick Kocela
# Date: Nov 19 2025

class Point:
    next_id = 0
    def __init__(self, x, y):
        self.id = Point.next_id
        Point.next_id += 1
        
        self.x = x
        self.y = y
        
        # Points to incident edges
        edges = []
        
class Edge:
    next_id = 0
    def __init__(self, point_l, point_r):
        self.id = Edge.next_id
        Edge.next_id += 1
        
        self.point_l = point_l
        self.point_r = point_r
        
        # Neighboring trapezoids
        self.traps = []
        
class Trap:
    next_id = 0
    def __init__(self):
        self.id = Trap.next_id
        Trap.next_id += 1
        
        vertices = []
        
        edge_top = None
        edge_bot = None
        edge_left = None
        edge_right = None