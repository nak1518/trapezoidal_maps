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
        self.edges = []
        
class Edge:
    next_id = 0
    def __init__(self, point_l, point_r):
        self.id = Edge.next_id
        Edge.next_id += 1
        
        self.point_l = point_l
        self.point_r = point_r
        
        # Neighboring trapezoids
        self.traps = []
    
    # Given a point, determines if it is above or below this segment
    def isAbove(self, point):
        if self.point_l.x == self.point_r.x:
            # Vertical segments break can break things so handle it here
            if point.y > self.point_l.y and point.y > self.point_r.y:
                return True
            else:
                return False
        if self.orientation(point) > 0:
            return True
        else:
            return False 
    
    # Finds the orientation of the point with respect to the endpoints
    # >0 means it's above, <0 means it's below
    # Assumes a is to the left of b
    def orientation(self, point):
        a = self.point_l
        b = self.point_r
        return (a.x*b.y-b.x*a.y)-(a.x*point.y-point.x*a.y)+(b.x*point.y-point.x*b.y)
        
        
class Trap:
    next_id = 0
    def __init__(self):
        self.id = Trap.next_id
        Trap.next_id += 1
        
        self.vertices = []
        
        self.edge_top = None
        self.edge_bottom = None
        self.edge_left = None
        self.edge_right = None
    
    # Checks if this trapezoid contains the point
    # Doesn't count points on the edge (should it?)
    # Assumes both side edges are vertical (they should always be vertical)
    def contains(self, point):
        if self.edge_top.point_l.x > point.x or self.edge_top.point_r.x < point.x:
            return False
        elif self.edge_top.orientation(point) > 0 or self.edge_bottom.orientation(point) < 0:
            return False
        else:
            return True
    
    # get the neighboring trapezoid based on the edge between them
    def get_neighbor(self, between_edge):
        edges = [self.edge_top, self.edge_right, self.edge_left, self.edge_bottom]
        for edge in edges:
            # Left or right edges can be none
            if edge == None:
                continue
            if edge.id == between_edge.id:
                traps = edge.traps
                for trap in traps:
                    if trap.id != self.id:
                        return trap
        # If no trapezoid was returned, error I guess
        print("uh oh, trapezoid neighbor returned none")
        return None
