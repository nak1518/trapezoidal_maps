# Author: Nick Kocela
# Date: Nov 19 2025

class Node:
    next_id = 0
    def __init__(self, type, child_1=None, child_2=None, trap=None):
        self.id = Node.next_id
        Node.next_id += 1
        
        self.type = type
        self.child_1 = child_1
        self.child_2 = child_2
        self.trap = trap
        
        