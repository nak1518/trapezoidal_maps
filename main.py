# Author: Nick Kocela, Anjan Maharjan
# Date: Nov 19 2025

import sys

from Dataclasses import Point, Edge, Trap
from DAG import Type, Node

# Global lists for labeling
all_points = []  # All points in order (left endpoints first, then right endpoints)
all_left_points = []  # Left endpoints (P1..Pk)
all_right_points = []  # Right endpoints (Q1..Qk)
all_edges = []   # All edges in order
all_trapezoids = []  # All trapezoids
all_nodes = []   # All DAG nodes

def find_leaf_nodes(node, leaves):
    """Recursively find all leaf nodes in the DAG"""
    if node is None:
        return
    if node.type == Type.Leaf:
        leaves.append(node)
    else:
        if node.child_1:
            find_leaf_nodes(node.child_1, leaves)
        if node.child_2:
            find_leaf_nodes(node.child_2, leaves)

def get_all_nodes(node, nodes_set):
    """Recursively collect all nodes in the DAG"""
    if node is None:
        return
    nodes_set.add(node)
    if node.child_1:
        get_all_nodes(node.child_1, nodes_set)
    if node.child_2:
        get_all_nodes(node.child_2, nodes_set)

def find_path_to_leaf(node, point, path):
    """Find the traversal path from root to leaf containing the point"""
    global all_left_points, all_right_points
    if node is None:
        return None
    if node.type == Type.X_Node:
        if node.point in all_left_points:
            point_idx = all_left_points.index(node.point) + 1
            path.append(f"P{point_idx}")
        elif node.point in all_right_points:
            point_idx = all_right_points.index(node.point) + 1
            path.append(f"Q{point_idx}")
        else:
            path.append(f"P?")  # Fallback
        if point.x < node.point.x:
            return find_path_to_leaf(node.child_1, point, path)
        else:
            return find_path_to_leaf(node.child_2, point, path)
    elif node.type == Type.Y_Node:
        edge_idx = all_edges.index(node.edge) + 1
        path.append(f"S{edge_idx}")
        if node.edge.isAbove(point):
            return find_path_to_leaf(node.child_1, point, path)
        else:
            return find_path_to_leaf(node.child_2, point, path)
    else:  # Leaf
        if node.trap and node.trap in all_trapezoids:
            trap_idx = all_trapezoids.index(node.trap) + 1
            path.append(f"T{trap_idx}")
        return node

def find_all_references_to_node(root, target_node, parent_refs):
    """Find all parent nodes that reference target_node"""
    if root is None:
        return
    if root.child_1 == target_node:
        parent_refs.append((root, 1))
    if root.child_2 == target_node:
        parent_refs.append((root, 2))
    if root.child_1:
        find_all_references_to_node(root.child_1, target_node, parent_refs)
    if root.child_2:
        find_all_references_to_node(root.child_2, target_node, parent_refs)

def replace_node_references(root, old_node, new_node):
    """Replace all references to old_node with new_node in the DAG"""
    parent_refs = []
    find_all_references_to_node(root, old_node, parent_refs)
    for parent, child_num in parent_refs:
        if child_num == 1:
            parent.child_1 = new_node
        else:
            parent.child_2 = new_node
    return len(parent_refs) > 0

def get_all_leaves(root):
    """Get all leaf nodes from the DAG"""
    leaves = []
    find_leaf_nodes(root, leaves)
    return leaves

def find_intersected_trapezoids(dag_root, new_edge):
    """Find all trapezoids intersected by the new edge"""
    left_point = new_edge.point_l
    right_point = new_edge.point_r
    
    # Find starting trapezoid
    start_leaf = dag_root.find(left_point)
    intersected_leaves = [start_leaf]
    
    # Follow the edge to find all intersected trapezoids
    current_trap = start_leaf.trap
    visited = set([current_trap.id])
    
    while not current_trap.contains(right_point):
        # Try to move right
        if current_trap.edge_right is None:
            break
        right_neighbor = current_trap.get_neighbor(current_trap.edge_right)
        if right_neighbor is None or right_neighbor.id in visited:
            break
        
        # Find the leaf containing this trapezoid
        found = False
        for leaf in get_all_leaves(dag_root):
            if leaf.trap == right_neighbor:
                intersected_leaves.append(leaf)
                current_trap = right_neighbor
                visited.add(current_trap.id)
                found = True
                break
        if not found:
            break
    
    return intersected_leaves

def create_trapezoid(edge_top, edge_bottom, edge_left, edge_right):
    """Create a new trapezoid with given edges"""
    trap = Trap()
    trap.edge_top = edge_top
    trap.edge_bottom = edge_bottom
    trap.edge_left = edge_left
    trap.edge_right = edge_right
    
    # Update edge references
    if edge_top:
        edge_top.traps.append(trap)
    if edge_bottom:
        edge_bottom.traps.append(trap)
    if edge_left:
        edge_left.traps.append(trap)
    if edge_right:
        edge_right.traps.append(trap)
    
    all_trapezoids.append(trap)
    return trap

def get_intersection_y(edge, x):
    """Get the y-coordinate where a vertical line at x intersects the edge"""
    if edge.point_l.x == edge.point_r.x:
        # Vertical edge
        return None
    # Linear interpolation
    if edge.point_l.x == edge.point_r.x:
        return None
    t = (x - edge.point_l.x) / (edge.point_r.x - edge.point_l.x)
    y = edge.point_l.y + t * (edge.point_r.y - edge.point_l.y)
    return y

def create_vertical_edge(x, y_bottom, y_top):
    """Create a vertical edge at x from y_bottom to y_top"""
    bottom_point = Point(x, y_bottom)
    top_point = Point(x, y_top)
    return Edge(bottom_point, top_point)

def split_trapezoid_by_point(trap, point, is_left):
    """Split a trapezoid by a vertical line through a point"""
    # Create vertical edge at the point
    # Find y coordinates where vertical line intersects top and bottom edges
    y_top = get_intersection_y(trap.edge_top, point.x) if trap.edge_top else point.y
    y_bottom = get_intersection_y(trap.edge_bottom, point.x) if trap.edge_bottom else point.y
    
    # If we can't get intersection, use point's y and extend
    if y_top is None:
        y_top = point.y + 1000  # Extend upward
    if y_bottom is None:
        y_bottom = point.y - 1000  # Extend downward
    
    vertical_edge = create_vertical_edge(point.x, y_bottom, y_top)
    
    # Create new trapezoids on left and right
    trap_left = create_trapezoid(trap.edge_top, trap.edge_bottom, trap.edge_left, vertical_edge)
    trap_right = create_trapezoid(trap.edge_top, trap.edge_bottom, vertical_edge, trap.edge_right)
    
    # Create point node
    point_node = Node(Type.X_Node)
    point_node.point = point
    
    leaf_left = Node(Type.Leaf)
    leaf_left.trap = trap_left
    leaf_right = Node(Type.Leaf)
    leaf_right.trap = trap_right
    
    point_node.child_1 = leaf_left
    point_node.child_2 = leaf_right
    
    all_trapezoids.remove(trap)
    return point_node, [leaf_left, leaf_right]

def split_trapezoid_by_edge(trap, edge):
    """Split a trapezoid by an edge (above and below), with proper wall trimming"""
    # Determine the x-range of this trapezoid
    trap_left_x = trap.edge_left.point_l.x if trap.edge_left else edge.point_l.x
    trap_right_x = trap.edge_right.point_l.x if trap.edge_right else edge.point_r.x
    
    # Find where the edge enters and exits this trapezoid (trimming points)
    entry_x = max(trap_left_x, edge.point_l.x)
    exit_x = min(trap_right_x, edge.point_r.x)
    
    # Create vertical edges at entry and exit points for trimming
    left_vert_edge = None
    right_vert_edge = None
    
    # If edge enters this trapezoid (not at left boundary), create vertical edge at entry
    if entry_x > trap_left_x:
        # Get y coordinates where vertical line at entry_x intersects top and bottom
        y_top_entry = get_intersection_y(trap.edge_top, entry_x) if trap.edge_top else None
        y_bottom_entry = get_intersection_y(trap.edge_bottom, entry_x) if trap.edge_bottom else None
        y_edge_entry = get_intersection_y(edge, entry_x)
        
        if y_top_entry is None:
            # Extend upward - use a large value
            y_top_entry = y_edge_entry + 1000 if y_edge_entry else 1000
        if y_bottom_entry is None:
            # Extend downward
            y_bottom_entry = y_edge_entry - 1000 if y_edge_entry else -1000
        
        left_vert_edge = create_vertical_edge(entry_x, y_bottom_entry, y_top_entry)
    
    # If edge exits this trapezoid (not at right boundary), create vertical edge at exit
    if exit_x < trap_right_x:
        # Get y coordinates where vertical line at exit_x intersects top and bottom
        y_top_exit = get_intersection_y(trap.edge_top, exit_x) if trap.edge_top else None
        y_bottom_exit = get_intersection_y(trap.edge_bottom, exit_x) if trap.edge_bottom else None
        y_edge_exit = get_intersection_y(edge, exit_x)
        
        if y_top_exit is None:
            y_top_exit = y_edge_exit + 1000 if y_edge_exit else 1000
        if y_bottom_exit is None:
            y_bottom_exit = y_edge_exit - 1000 if y_edge_exit else -1000
        
        right_vert_edge = create_vertical_edge(exit_x, y_bottom_exit, y_top_exit)
    
    # Determine left and right edges for resulting trapezoids
    # Use trimmed edges if created, otherwise use original boundaries
    left_edge_above = left_vert_edge if left_vert_edge else trap.edge_left
    left_edge_below = left_vert_edge if left_vert_edge else trap.edge_left
    right_edge_above = right_vert_edge if right_vert_edge else trap.edge_right
    right_edge_below = right_vert_edge if right_vert_edge else trap.edge_right
    
    # Create trapezoids above and below the edge
    trap_above = create_trapezoid(trap.edge_top, edge, left_edge_above, right_edge_above)
    trap_below = create_trapezoid(edge, trap.edge_bottom, left_edge_below, right_edge_below)
    
    seg_node = Node(Type.Y_Node)
    seg_node.edge = edge
    
    leaf_above = Node(Type.Leaf)
    leaf_above.trap = trap_above
    leaf_below = Node(Type.Leaf)
    leaf_below.trap = trap_below
    
    seg_node.child_1 = leaf_above
    seg_node.child_2 = leaf_below
    
    all_trapezoids.remove(trap)
    return seg_node, [leaf_above, leaf_below]

def add_edge_to_map(dag_root, new_edge):
    """Add a new edge to the trapezoidal map using incremental algorithm"""
    left_point = new_edge.point_l
    right_point = new_edge.point_r
    
    # Find all intersected trapezoids
    intersected_leaves = find_intersected_trapezoids(dag_root, new_edge)
    
    if not intersected_leaves:
        return dag_root
    
    # First, add point nodes for endpoints if they don't exist
    # For left point
    left_leaf = dag_root.find(left_point)
    if left_leaf.trap.contains(left_point):
        # Split by left point first
        point_node, new_leaves = split_trapezoid_by_point(left_leaf.trap, left_point, True)
        if dag_root == left_leaf:
            dag_root = point_node
        else:
            replace_node_references(dag_root, left_leaf, point_node)
        # Update intersected_leaves
        intersected_leaves = find_intersected_trapezoids(dag_root, new_edge)
    
    # For right point
    right_leaf = dag_root.find(right_point)
    if right_leaf.trap.contains(right_point):
        # Split by right point
        point_node, new_leaves = split_trapezoid_by_point(right_leaf.trap, right_point, False)
        if dag_root == right_leaf:
            dag_root = point_node
        else:
            replace_node_references(dag_root, right_leaf, point_node)
        # Update intersected_leaves
        intersected_leaves = find_intersected_trapezoids(dag_root, new_edge)
    
    # Now split all intersected trapezoids by the edge with proper trimming
    for i, leaf in enumerate(intersected_leaves):
        trap = leaf.trap
        is_first = (i == 0)
        is_last = (i == len(intersected_leaves) - 1)
        
        # Check if this trapezoid actually needs to be split by the edge
        # (it should be between or contain the endpoints)
        trap_left_x = trap.edge_left.point_l.x if trap.edge_left else float('-inf')
        trap_right_x = trap.edge_right.point_l.x if trap.edge_right else float('inf')
        
        # Skip if trapezoid is completely outside the edge range
        if trap_right_x < left_point.x or trap_left_x > right_point.x:
            continue
        
        # Split by edge (this will handle trimming)
        seg_node, new_leaves = split_trapezoid_by_edge(trap, new_edge)
        if dag_root == leaf:
            dag_root = seg_node
        else:
            replace_node_references(dag_root, leaf, seg_node)
    
    return dag_root

def build_adjacency_matrix(dag_root):
    """Build adjacency matrix from DAG structure"""
    nodes_set = set()
    get_all_nodes(dag_root, nodes_set)
    nodes_list = sorted(list(nodes_set), key=lambda n: n.id)
    
    n = len(nodes_list)
    matrix = [[0] * n for _ in range(n)]
    
    # Build the matrix (child -> parent)
    for i, node in enumerate(nodes_list):
        if node.child_1:
            child_idx = nodes_list.index(node.child_1)
            matrix[child_idx][i] = 1
        if node.child_2:
            child_idx = nodes_list.index(node.child_2)
            matrix[child_idx][i] = 1
    
    return matrix, nodes_list

def get_node_label(node):
    """Get the label for a node"""
    global all_left_points, all_right_points
    if node.type == Type.X_Node:
        if node.point in all_left_points:
            return f"P{all_left_points.index(node.point) + 1}"
        elif node.point in all_right_points:
            return f"Q{all_right_points.index(node.point) + 1}"
    elif node.type == Type.Y_Node:
        if node.edge in all_edges:
            return f"S{all_edges.index(node.edge) + 1}"
    else:  # Leaf
        if node.trap and node.trap in all_trapezoids:
            return f"T{all_trapezoids.index(node.trap) + 1}"
    return f"N{node.id}"

def print_adjacency_matrix(matrix, nodes_list, output_file):
    """Print the adjacency matrix in the required format to a file"""
    n = len(nodes_list)
    
    # Print header
    output_file.write("   ")
    for i in range(n):
        label = get_node_label(nodes_list[i])
        output_file.write(f"{label:>4}")
    output_file.write(" Sum\n")
    
    # Print rows
    for i in range(n):
        row_sum = sum(matrix[i])
        col_sum = sum(matrix[j][i] for j in range(n))
        
        label = get_node_label(nodes_list[i])
        output_file.write(f"{label:>3}")
        for j in range(n):
            output_file.write(f"{matrix[i][j]:4}")
        output_file.write(f" {row_sum:3}\n")

def main(argv):
    path = "nick.txt"
    if len(argv) > 1:
        path = argv[1]
    
    global all_points, all_edges, all_trapezoids, all_nodes, all_left_points, all_right_points
    
    # Reset global counters
    Point.next_id = 0
    Edge.next_id = 0
    Trap.next_id = 0
    Node.next_id = 0
    
    trapezoids = []
    edges = []
    points = []
    dag = None
    
    # Read the input file
    n = 0
    with open(path) as file:
        for i, line in enumerate(file):
            line = line.strip()
            if not line:
                continue
            if i == 0:
                 n = int(line)
                 continue
            tokens = line.split()
            if len(tokens) != 4:
                continue
            
            x1 = float(tokens[0])
            y1 = float(tokens[1])
            x2 = float(tokens[2])
            y2 = float(tokens[3])
            
            # Defining the bounding box (line 2)
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
                all_trapezoids.append(bounding_box)
                continue
                
            # Process line segments
            # Ensure left point has smaller x (or smaller y if x is equal)
            if x1 < x2 or (x1 == x2 and y1 < y2):
                point_l = Point(x1, y1)
                point_r = Point(x2, y2)
            else:
                point_l = Point(x2, y2)
                point_r = Point(x1, y1)
            
            edge = Edge(point_l, point_r)
            
            points.append(point_l)
            points.append(point_r)
            point_l.edges.append(edge)
            point_r.edges.append(edge)
            edges.append(edge)
    
    # Organize points: left endpoints first (P1..Pk), then right endpoints (Q1..Qk)
    left_points = []
    right_points = []
    for edge in edges:
        left_points.append(edge.point_l)
        right_points.append(edge.point_r)
    
    # Store separately for labeling
    all_left_points = left_points
    all_right_points = right_points
    all_points = left_points + right_points  # Keep for compatibility
    all_edges = edges
    
    # Initialize the DAG for locating points inside trapezoids
    dag = Node(Type.Leaf)
    dag.trap = bounding_box
    
    # Add each edge one at a time using incremental algorithm
    for new_edge in edges:
        dag = add_edge_to_map(dag, new_edge)
    
    # Build and print adjacency matrix to output file
    matrix, nodes_list = build_adjacency_matrix(dag)
    
    # Determine output filename (based on input filename)
    output_filename = path.rsplit('.', 1)[0] + "_output.txt" if '.' in path else path + "_output.txt"
    
    with open(output_filename, 'w') as output_file:
        print_adjacency_matrix(matrix, nodes_list, output_file)
    
    # Check if query point is provided
    if len(argv) < 4:
        print(f"Error: Query point not provided. Usage: python3 main.py <input_file> <x> <y>")
        sys.exit(1)
    
    # Query point provided as command line arguments
    x = float(argv[2])
    y = float(argv[3])
    query_point = Point(x, y)
    path = []
    find_path_to_leaf(dag, query_point, path)
    print(" ".join(path))
            
if __name__ == "__main__":
    main(sys.argv)
