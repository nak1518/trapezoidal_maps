# Author: Nick Kocela
# Date: Nov 19 2025

import sys

from Dataclasses import Point, Edge, Trap
from DAG import Node

# Represent trapezoidal map as doubly connected edge list 
# (contains vertices, edges, and faces as seperate items with pointers to neighbors). 
# Also give everything an ID to make it easy to compare them?

def main(argv):
    path = "nick.txt"
    if len(argv) > 1:
        path = argv[1]
    
    lines = []
    trapezoids = []
    edges = []
    points = []
    dag = None
    
    print("here")
    
    # Read the input file
    n = 0
    with open(path) as file:
        for i, line in enumerate(file):
            if i == 0:
                 n = int(line)
                 continue
            tokens = line.split()
            if len(tokens) != 4:
                print("Error reading input. Terminating")
                return 1
            x1 = int(tokens[0])
            y1 = int(tokens[1])
            x2 = int(tokens[2])
            y2 = int(tokens[3])
            
            # Defining the bounding box
            if i == 1:
                point_lb = Point(x1, y1)
                point_rb = Point(x2, y1)
                point_lt = Point(x1, y2)
                point_rt = Point(x2, y2)
                
                bounding_box = Trap()
                
                edge_bottom = Edge(point_lb, point_rb)
                edge_left = Edge(point_lb, point_lt)
                edge_right = Edge(point_rb, point_rt)
                edge_top = Edge(point_lt, point_lt)
                
                edge_bottom.traps.append(edge_bottom)
                
                
                
                bounding_box.edge_bottom = edge_bottom
                bounding_box.edge_left = edge_left
                bounding_box.edge_right = edge_right
                bounding_box.edge_top = edge_top
            
            if x1 == x2:
                print("Error, vertical line in input. Terminating")
                return 1
            
if __name__ == "__main__":
    main(sys.argv)