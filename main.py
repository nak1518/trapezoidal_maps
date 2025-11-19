# Author: Nick Kocela
# Date: Nov 19 2025

import sys

from Dataclasses import Point, Edge, Trap
from DAG import Type, Node

# Represent trapezoidal map as doubly connected edge list 
# (contains vertices, edges, and faces as separate items with pointers to neighbors). 
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

    
    # Read the input file
    n = 0
    with open(path) as file:
        for i, line in enumerate(file):
            if i == 0:
                 n = int(line)
                 continue
            tokens = line.split()
            if len(tokens) != 4:
                break
            
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
                edge_top = Edge(point_lt, point_rt)
                
                edge_bottom.traps.append(bounding_box)
                edge_left.traps.append(bounding_box)
                edge_right.traps.append(bounding_box)
                edge_top.traps.append(bounding_box)
                
                bounding_box.edge_bottom = edge_bottom
                bounding_box.edge_left = edge_left
                bounding_box.edge_right = edge_right
                bounding_box.edge_top = edge_top
                
                trapezoids.append(bounding_box)
                
                continue
                
            point_l = Point(x1, y1)
            point_r = Point(x2, y2)
            edge = Edge(point_l, point_r)
            
            point_l.edges.append(edge)
            point_r.edges.append(edge)
            edges.append(edge)
    
    # Initialize the DAG for locating points inside trapezoids
    dag = Node(Type.Leaf)
    dag.trap = bounding_box
    
    # Add each edge one at a time
    # The input should already be randomized so no need to worry about that
    for new_edge in edges:
        
        # Find each of the trapezoids that were intersected, left to right
        left_endpoint = new_edge.point_l
        right_endpoint = new_edge.point_r
        
        # Get all the leaf nodes of the trapezoids that were intersected
        intersected_leaf = dag.find(left_endpoint)
        intersected_traps = [intersected_leaf.trap]
        
        # Travel across the trapezoids to the right until you find one that contains the right endpoint
        while(not intersected_traps[-1].contains(right_endpoint)):
            this_trap = intersected_traps[-1]
            new_trap = this_trap.get_neighbor(this_trap.edge_right) # get_neighbor is stubbed
            intersected_traps.append(new_trap)
            
        # For each trapezoid intersected, fix them
        for i, intersected_trap in enumerate(intersected_traps):
            if len(intersected_traps) == 1:
                # Contains both endpoints
                pass
            
            elif i == 0:
                # Contains left endpoint
                pass
            
            elif i == len(intersected_traps) - 1:
                # Contains right endpoint
                pass
            
            else:
                # Contains no endpoints
                pass
            
            
    # After the trapezoidal map is created, let the user input a query point
    # DO INPUT STUFF HERE
    
    # Print out the path it took through the DAG
    
    # Save the entire node structure to a csv file
            
if __name__ == "__main__":
    main(sys.argv)
