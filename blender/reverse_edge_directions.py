#!/usr/bin/env python3
"""
Script to reverse the direction of specific edges in a network mesh.
This involves:
1. Swapping start/end nodes in the edges file
2. Physically reordering vertex rows AND reversing EdgeIndex for those edges in the vertices file

No external dependencies required - uses only Python standard library.
"""

import csv
import os
import bpy

# List of edges to reverse
EDGES_TO_REVERSE = [
    'edge_46',
    'edge_5',
    'edge_49',
    'edge_27',
    'edge_31',
    'edge_30',
    'edge_55',
    'edge_18',
    'edge_21',
    'edge_23',
    'edge_25',
    'edge_36',
    'edge_37',
    'edge_15',
]

def read_csv_with_comments(filepath):
    """
    Read a CSV file, separating comments from data.
    
    Returns:
        tuple: (comments_list, header_row, data_rows)
    """
    comments = []
    data_rows = []
    header = None
    
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            # Skip empty rows
            if not row or not any(row):
                continue
                
            # Check if this is a comment line (first cell starts with #)
            if row[0].startswith('#'):
                comments.append(','.join(row) + '\n')
            elif header is None:
                # First non-comment line is the header - strip whitespace
                header = [col.strip() for col in row]
            else:
                # Data rows - strip whitespace from each cell
                data_rows.append([cell.strip() for cell in row])
    
    return comments, header, data_rows

def write_csv_with_comments(filepath, comments, header, data_rows):
    """
    Write a CSV file with comments preserved.
    """
    # Create directory if it doesn't exist
    directory = os.path.dirname(filepath)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)
        print(f"Created directory: {directory}")
    
    with open(filepath, 'w', encoding='utf-8', newline='') as f:
        # Write comments
        for comment in comments:
            f.write(comment)
        
        # Write blank line if there were comments
        if comments and not comments[-1].endswith('\n\n'):
            f.write('\n')
        
        # Write header
        writer = csv.writer(f)
        writer.writerow(header)
        
        # Write data
        writer.writerows(data_rows)

def reverse_edges(edges_file, vertices_file, output_edges_file, output_vertices_file):
    """
    Reverse the direction of specified edges.
    
    Args:
        edges_file: Path to the edges CSV file
        vertices_file: Path to the vertices CSV file
        output_edges_file: Path to save modified edges CSV
        output_vertices_file: Path to save modified vertices CSV
    """
    
    # Read edges file
    print("Reading edges file...")
    edges_comments, edges_header, edges_data = read_csv_with_comments(edges_file)
    
    # Create a dictionary mapping header names to column indices
    edges_col_idx = {col: idx for idx, col in enumerate(edges_header)}
    print(f"Edges columns found: {list(edges_col_idx.keys())}")
    
    # Verify required columns exist
    required_edges_cols = ['EdgeId', 'StartNodeId', 'EndNodeId', 'StartNodeIndex', 'EndNodeIndex']
    missing_cols = [col for col in required_edges_cols if col not in edges_col_idx]
    if missing_cols:
        raise ValueError(f"Missing required columns in edges file: {missing_cols}")
    
    # Read vertices file
    print("Reading vertices file...")
    vertices_comments, vertices_header, vertices_data = read_csv_with_comments(vertices_file)
    
    # Create a dictionary mapping header names to column indices
    vertices_col_idx = {col: idx for idx, col in enumerate(vertices_header)}
    print(f"Vertices columns found: {list(vertices_col_idx.keys())}")
    
    # Verify required columns exist
    required_vertices_cols = ['EdgeId', 'EdgeIndex']
    missing_cols = [col for col in required_vertices_cols if col not in vertices_col_idx]
    if missing_cols:
        raise ValueError(f"Missing required columns in vertices file: {missing_cols}")
    
    print(f"\nReversing direction for {len(EDGES_TO_REVERSE)} edges...")
    
    # Process edges - swap start/end nodes
    edges_reversed = 0
    for i, row in enumerate(edges_data):
        edge_id = row[edges_col_idx['EdgeId']]
        
        if edge_id in EDGES_TO_REVERSE:
            # Swap StartNodeId and EndNodeId
            start_node_idx = edges_col_idx['StartNodeId']
            end_node_idx = edges_col_idx['EndNodeId']
            start_node = row[start_node_idx]
            end_node = row[end_node_idx]
            row[start_node_idx] = end_node
            row[end_node_idx] = start_node
            
            # Swap StartNodeIndex and EndNodeIndex
            start_idx_col = edges_col_idx['StartNodeIndex']
            end_idx_col = edges_col_idx['EndNodeIndex']
            start_index = row[start_idx_col]
            end_index = row[end_idx_col]
            row[start_idx_col] = end_index
            row[end_idx_col] = start_index
            
            edges_reversed += 1
            print(f"  ✓ Reversed {edge_id}: {start_node} ↔ {end_node}")
    
    if edges_reversed < len(EDGES_TO_REVERSE):
        print(f"  ⚠ Warning: Only found {edges_reversed} of {len(EDGES_TO_REVERSE)} edges to reverse")
    
    print(f"\nReversing vertex order for edges...")
    
    # Group all vertices by edge
    vertices_by_edge = {}
    for i, row in enumerate(vertices_data):
        edge_id = row[vertices_col_idx['EdgeId']]
        if edge_id not in vertices_by_edge:
            vertices_by_edge[edge_id] = []
        vertices_by_edge[edge_id].append((i, row))
    
    # Build a new vertices data list with reversed edges in reverse order
    new_vertices_data = []
    processed_indices = set()
    
    # Go through original vertices data in order
    for i, row in enumerate(vertices_data):
        if i in processed_indices:
            continue
            
        edge_id = row[vertices_col_idx['EdgeId']]
        
        # If this edge should be reversed and we haven't processed it yet
        if edge_id in EDGES_TO_REVERSE and edge_id in vertices_by_edge:
            # Get all vertices for this edge
            edge_vertices = vertices_by_edge[edge_id]
            
            # Sort by current EdgeIndex to ensure proper order
            edge_index_col = vertices_col_idx['EdgeIndex']
            edge_vertices_sorted = sorted(edge_vertices, key=lambda x: int(x[1][edge_index_col]))
            
            # Reverse the order
            edge_vertices_reversed = list(reversed(edge_vertices_sorted))
            
            # Calculate max index for reversing EdgeIndex values
            max_index = max(int(v[1][edge_index_col]) for v in edge_vertices_sorted)
            
            # Add reversed vertices with reversed EdgeIndex
            for orig_idx, vertex_row in edge_vertices_reversed:
                # Create a copy of the row
                new_row = vertex_row.copy()
                # Reverse the EdgeIndex value
                old_edge_index = int(vertex_row[edge_index_col])
                new_edge_index = max_index - old_edge_index
                new_row[edge_index_col] = str(new_edge_index)
                new_vertices_data.append(new_row)
                processed_indices.add(orig_idx)
            
            print(f"  ✓ Reversed {len(edge_vertices)} vertices for {edge_id}")
            
            # Mark this edge as processed
            del vertices_by_edge[edge_id]
        else:
            # Edge not reversed, keep original
            new_vertices_data.append(row)
            processed_indices.add(i)
    
    print(f"\nSummary:")
    print(f"  - Edges reversed: {edges_reversed}")
    print(f"  - Vertices reordered: {len([v for v in vertices_data if v[vertices_col_idx['EdgeId']] in EDGES_TO_REVERSE])}")
    
    # Write the modified data back to files
    print(f"\nWriting modified files...")
    
    write_csv_with_comments(output_edges_file, edges_comments, edges_header, edges_data)
    write_csv_with_comments(output_vertices_file, vertices_comments, vertices_header, new_vertices_data)
    
    print(f"  ✓ Edges saved to: {output_edges_file}")
    print(f"  ✓ Vertices saved to: {output_vertices_file}")
    print("\nDone!")

if __name__ == "__main__":
    # Input files
    edges_input = bpy.path.abspath("//Mesh_edges.csv")  # Relative to .blend file
    vertices_input = bpy.path.abspath("//Mesh_vertices.csv")  # Relative to .blend file
    
    # Output files
    edges_output = bpy.path.abspath("//outputs//Mesh_edges.csv")  # Relative to .blend file
    vertices_output = bpy.path.abspath("//outputs//Mesh_vertices.csv")  # Relative to .blend file
    
    # Run the reversal
    reverse_edges(edges_input, vertices_input, edges_output, vertices_output)