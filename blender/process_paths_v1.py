"""
Blender Script: Process Two Parallel Paths from OBJ File

This script reads an OBJ file containing two unconnected parallel paths,
identifies the highest endpoint (vertex with only 1 connection and max Z) in each path,
and returns ordered vertex lists starting from those highest endpoints.

FEATURES:
- Offset all vertices by (x, y, z)
- Apply coordinate transformation (x,y,z) -> (x,-z,y) for coordinate system conversion
- Start paths from highest endpoint (vertex with 1 connection and max Z)
- Output ordered vertex lists and create Blender curve objects
- Export paths to CSV files

USAGE IN BLENDER:
1. Open Blender's Text Editor
2. Create a new text file and paste this script
3. Update the obj_file path to point to your OBJ file (line ~145)
4. Configure offset and transformation settings (lines ~150-160)
5. Run the script (Alt+P or click "Run Script")
6. Check the System Console (Window > Toggle System Console) for results

The script will:
- Apply transformations (offset and coordinate system conversion)
- Print the ordered vertex lists to the console
- Create two new curve objects in your scene showing the ordered paths
- Export paths to CSV files in the same directory as the OBJ file
- Return path1_verts and path2_verts variables you can access in the script
"""

import bpy
from collections import defaultdict
import csv
import os


def parse_obj_and_order_paths(obj_filepath, offset_x=0.0, offset_y=0.0, offset_z=0.0, apply_transform=True):
    """
    Parse an OBJ file containing two unconnected parallel paths.
    Returns two lists of vertices ordered from the highest endpoint.
    
    An endpoint is a vertex with only 1 edge connection. The script finds
    the endpoint with the maximum Z coordinate and traverses from there.
    
    Args:
        obj_filepath: Path to the OBJ file
        offset_x: X offset to apply to all vertices (default: 0.0)
        offset_y: Y offset to apply to all vertices (default: 0.0)
        offset_z: Z offset to apply to all vertices (default: 0.0)
        apply_transform: If True, applies coordinate transform (x,y,z) -> (x,-z,y) (default: True)
        
    Returns:
        list of lists: Each inner list contains (x, y, z) tuples for one path,
                      ordered from the highest endpoint to the lowest endpoint
    """
    
    # Parse OBJ file
    vertices = []
    edges = []
    
    print(f"Parsing OBJ file: {obj_filepath}")
    print(f"  Offset: ({offset_x}, {offset_y}, {offset_z})")
    print(f"  Apply transform (x,y,z) -> (x,-z,y): {apply_transform}")
    
    with open(obj_filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith('v '):
                # Parse vertex: v x y z
                parts = line.split()
                x, y, z = float(parts[1]), float(parts[2]), float(parts[3])
                
                # Apply coordinate transformation if requested
                # Transform: (x, y, z) -> (x, -z, y)
                if apply_transform:
                    x_new = x
                    y_new = -z
                    z_new = y
                    x, y, z = x_new, y_new, z_new
                
                # Apply offset
                x += offset_x
                y += offset_y
                z += offset_z
                
                vertices.append((x, y, z))
            elif line.startswith('l '):
                # Parse line: l v1 v2 (1-indexed in OBJ format)
                parts = line.split()
                v1, v2 = int(parts[1]) - 1, int(parts[2]) - 1  # Convert to 0-indexed
                edges.append((v1, v2))
    
    print(f"Loaded {len(vertices)} vertices and {len(edges)} edges")
    
    # Build adjacency graph
    graph = defaultdict(list)
    for v1, v2 in edges:
        graph[v1].append(v2)
        graph[v2].append(v1)
    
    # Find connected components (the two separate paths)
    visited = set()
    components = []
    
    def dfs(start, component):
        """Depth-first search to find connected vertices"""
        stack = [start]
        while stack:
            v = stack.pop()
            if v in visited:
                continue
            visited.add(v)
            component.append(v)
            for neighbor in graph[v]:
                if neighbor not in visited:
                    stack.append(neighbor)
    
    # Find all connected components
    for i in range(len(vertices)):
        if i not in visited and i in graph:  # Only consider vertices with edges
            component = []
            dfs(i, component)
            if component:
                components.append(component)
    
    print(f"Found {len(components)} separate paths")
    
    # For each component, find the highest endpoint and order the path
    ordered_paths = []
    
    for comp_idx, component in enumerate(components):
        # Find endpoints (vertices with only 1 connection)
        endpoints = [v for v in component if len(graph[v]) == 1]
        
        if len(endpoints) != 2:
            print(f"Warning: Path {comp_idx + 1} has {len(endpoints)} endpoints (expected 2)")
            # Fallback: use vertex with max Z if endpoints aren't clear
            start_idx = max(component, key=lambda idx: vertices[idx][2])
        else:
            # Find the endpoint with the highest Z coordinate
            start_idx = max(endpoints, key=lambda idx: vertices[idx][2])
        
        start_z_value = vertices[start_idx][2]
        print(f"Path {comp_idx + 1}: Starting from endpoint vertex {start_idx} with Z={start_z_value:.3f}")
        
        # Traverse the path from the highest endpoint
        ordered = []
        current = start_idx
        visited_path = set()
        
        # Traverse along the path
        while current is not None:
            visited_path.add(current)
            ordered.append(vertices[current])
            
            # Find next unvisited neighbor
            next_vertex = None
            for neighbor in graph[current]:
                if neighbor not in visited_path:
                    next_vertex = neighbor
                    break
            
            current = next_vertex
        
        ordered_paths.append(ordered)
        print(f"Path {comp_idx + 1}: {len(ordered)} vertices ordered from highest endpoint")
    
    return ordered_paths


def export_paths_to_csv(paths, obj_filepath, output_dir=None, offset_x=0.0, offset_y=0.0, offset_z=0.0, apply_transform=True):
    """
    Export ordered paths to CSV files.
    
    Args:
        paths: List of paths (each path is a list of (x, y, z) tuples)
        obj_filepath: Original OBJ file path (used for naming)
        output_dir: Directory to save CSV files (default: same as OBJ file)
        offset_x, offset_y, offset_z: The offsets that were applied
        apply_transform: Whether transformation was applied
        
    Returns:
        list: List of CSV file paths that were created
    """
    
    # Get the base name from the OBJ file path
    obj_basename = os.path.splitext(os.path.basename(obj_filepath))[0]
    
    # Determine output directory
    if output_dir is None:
        output_dir = os.path.dirname(obj_filepath)
    
    # If no directory specified, use current directory
    if not output_dir:
        output_dir = "."
    
    csv_files = []
    
    for i, path in enumerate(paths):
        # Create filename
        csv_filename = f"{obj_basename}_path{i+1}_ordered.csv"
        csv_filepath = os.path.join(output_dir, csv_filename)
        
        # Write CSV
        with open(csv_filepath, 'w', newline='') as f:
            writer = csv.writer(f)
            
            # Write header with metadata
            writer.writerow(['# Ordered Path Vertices'])
            writer.writerow([f'# Source: {os.path.basename(obj_filepath)}'])
            writer.writerow([f'# Path: {i+1}'])
            writer.writerow([f'# Vertices: {len(path)}'])
            writer.writerow([f'# Offset: ({offset_x}, {offset_y}, {offset_z})'])
            writer.writerow([f'# Transform Applied: {apply_transform}'])
            if apply_transform:
                writer.writerow(['# Transform: (x,y,z) -> (x,-z,y)'])
            writer.writerow(['# Starting from highest endpoint (max Z)'])
            writer.writerow([])
            
            # Write column headers
            writer.writerow(['Index', 'X', 'Y', 'Z'])
            
            # Write vertices
            for j, (x, y, z) in enumerate(path):
                writer.writerow([j, f'{x:.6f}', f'{y:.6f}', f'{z:.6f}'])
        
        csv_files.append(csv_filepath)
        print(f"✓ Exported: {csv_filename} ({len(path)} vertices)")
    
    return csv_files


# =============================================================================
# MAIN EXECUTION
# =============================================================================

if __name__ == "__main__":
    # *** UPDATE THIS PATH TO YOUR OBJ FILE ***
    # obj_file = "C:\path\to\your\obj.txt"  # Change this!
    
    # Alternative: Use bpy.path to select file through Blender's file browser
    obj_file = bpy.path.abspath("//OpenPitPaths.obj.txt")  # Relative to .blend file
    
    # *** TRANSFORMATION SETTINGS ***
    # Offset to apply to all vertices (default: 0, 0, 0)
    offset_x = 0.0
    offset_y = 0.0
    offset_z = 0.0
    
    # Whether to apply coordinate transformation (x,y,z) -> (x,-z,y)
    # This is useful when converting between different 3D software coordinate systems
    # Set to False to keep original coordinates
    apply_transform = False
    
    # *** CSV OUTPUT SETTINGS ***
    # Directory to save CSV files (default: None = same directory as OBJ file)
    # Examples:
    #   output_dir = None  # Save to same directory as OBJ
    #   output_dir = "/path/to/output/folder"  # Specify custom directory
    #   output_dir = bpy.path.abspath("//")  # Save to .blend file directory
    output_dir = None
    
    # Process the paths with transformations
    paths = parse_obj_and_order_paths(
        obj_file, 
        offset_x=offset_x, 
        offset_y=offset_y, 
        offset_z=offset_z,
        apply_transform=apply_transform
    )
    
    # Store results in variables you can access
    path1_verts = paths[0] if len(paths) > 0 else []
    path2_verts = paths[1] if len(paths) > 1 else []
    
    # Display results
    print("\n" + "="*70)
    print("ORDERED VERTEX LISTS (Starting from Highest Endpoint)")
    print("="*70)
    
    for i, path in enumerate(paths):
        print(f"\nPath {i + 1}:")
        print(f"  Total vertices: {len(path)}")
        print(f"  Starting point (highest endpoint): {path[0]}")
        print(f"  Ending point (lowest endpoint): {path[-1]}")
        print(f"\n  First 10 vertices:")
        for j, vert in enumerate(path[:10]):
            print(f"    [{j:3d}] ({vert[0]:10.3f}, {vert[1]:10.3f}, {vert[2]:10.3f})")
    
    # Export to CSV
    print("\n" + "="*70)
    print("Exporting to CSV files...")
    print("="*70)
    
    csv_files = export_paths_to_csv(
        paths, 
        obj_file,
        output_dir=output_dir,
        offset_x=offset_x,
        offset_y=offset_y,
        offset_z=offset_z,
        apply_transform=apply_transform
    )
    
    csv_output_location = output_dir if output_dir else (os.path.dirname(obj_file) or 'current directory')
    print(f"\nCSV files saved to: {csv_output_location}")
    
    # Create curve objects in Blender from these paths
    print("\n" + "="*70)
    print("Creating Blender curve objects...")
    print("="*70)
    
    for i, path in enumerate(paths):
        # Create a new curve
        curve_data = bpy.data.curves.new(name=f"OrderedPath_{i+1}", type='CURVE')
        curve_data.dimensions = '3D'
        
        # Create a new spline in the curve
        spline = curve_data.splines.new(type='POLY')
        spline.points.add(len(path) - 1)  # Already has 1 point by default
        
        # Set the coordinates
        for j, (x, y, z) in enumerate(path):
            spline.points[j].co = (x, y, z, 1.0)  # 4th coordinate is weight
        
        # Create object and link to scene
        curve_obj = bpy.data.objects.new(f"OrderedPath_{i+1}", curve_data)
        bpy.context.collection.objects.link(curve_obj)
        
        print(f"✓ Created curve object: OrderedPath_{i+1} with {len(path)} points")
    
    print("\n" + "="*70)
    print("COMPLETE!")
    print("="*70)
    print("\nVariables available in this script:")
    print("  - path1_verts: List of (x,y,z) tuples for path 1")
    print("  - path2_verts: List of (x,y,z) tuples for path 2")
    print("  - paths: List containing both path lists")
    print("  - csv_files: List of CSV file paths created")
    print("\nOutputs created:")
    print("  - Two curve objects added to your Blender scene")
    print(f"  - {len(csv_files)} CSV files exported")
    print("\nCheck the System Console for the full vertex lists and file locations.")
    print("="*70)
