# Author: Nick Kocela
# Date: Nov 19 2025

from enum import Enum

class Type(Enum):
    X_Node = 1
    Y_Node = 2
    Leaf = 3

class Node:
    next_id = 0
    def __init__(self, type, child_1=None, child_2=None, trap=None):
        self.id = Node.next_id
        Node.next_id += 1
        
        self.type = type
        
        # Used if it's an x-node or y-node respectively
        self.point = None
        self.edge = None
        
        # Is the left or above child
        self.child_1 = child_1
        # Is the right or below child
        self.child_2 = child_2
        
        self.trap = trap
    
    # Finds the 
    def find(self, point):
        if self.type == Type.X_Node:
            if point.x < self.point.x:
                return self.child_1.find(point)
            else:
                return self.child_2.find(point)
        elif self.type == Type.Y_Node:
            if self.edge.isAbove(point):
                return self.child_1.find(point)
            else:
                return self.child_2.find(point)
        else:
            # Must be a Leaf node
            return self
