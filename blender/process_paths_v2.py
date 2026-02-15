"""
Network Topology Parser for OBJ Files

This script reads an OBJ file containing a network mesh, analyzes its topology,
and exports the network structure to CSV files.

FEATURES:
- Classifies vertices as nodes (endpoints/intersections) or inline vertices
- Builds edges between nodes with inline vertex sequences
- Validates all connections against original OBJ data
- Exports to CSV: nodes, edges, vertices, and summary
- Optional coordinate transformation (x,y,z) -> (x,z,-y)
- Optional offset application

USAGE:
    python process_network_topology.py
    
Or configure and run from within your IDE/script.
"""

import csv
import os
from collections import defaultdict
from typing import List, Tuple, Dict, Set, Optional
from dataclasses import dataclass, field


@dataclass
class Vector3:
    """3D vector/point"""
    x: float
    y: float
    z: float
    
    def __iter__(self):
        return iter((self.x, self.y, self.z))
    
    def __repr__(self):
        return f"({self.x:.3f}, {self.y:.3f}, {self.z:.3f})"


@dataclass
class Node:
    """Network node (endpoint or intersection)"""
    id: str
    index: int  # Original OBJ vertex index
    position: Vector3
    node_type: str  # 'ENDPOINT' or 'INTERSECTION'
    connection_count: int
    
    def to_csv_row(self):
        return [
            self.id,
            f'{self.position.x:.6f}',
            f'{self.position.y:.6f}',
            f'{self.position.z:.6f}',
            self.node_type,
            self.connection_count
        ]


@dataclass
class Edge:
    """Network edge connecting two nodes"""
    id: str
    start_node_id: str
    end_node_id: str
    start_node_index: int
    end_node_index: int
    inline_vertex_indices: List[int] = field(default_factory=list)
    bidirectional: bool = True
    
    def vertex_count(self):
        return len(self.inline_vertex_indices)
    
    def to_csv_row(self, vertices_dict):
        """Convert to CSV row with calculated length"""
        # Calculate edge length if we have vertices
        length = 0.0
        if self.inline_vertex_indices:
            # Simple approach: sum distances between consecutive points
            pass  # Will calculate in exporter
        
        return [
            self.id,
            self.start_node_id,
            self.end_node_id,
            self.start_node_index,
            self.end_node_index,
            len(self.inline_vertex_indices),
            self.bidirectional
        ]


@dataclass
class Vertex:
    """Inline vertex along an edge"""
    id: str
    edge_id: str
    edge_index: int  # Position within edge (0-based)
    index: int  # Original OBJ vertex index
    position: Vector3
    
    def to_csv_row(self):
        return [
            self.id,
            self.edge_id,
            self.edge_index,
            self.index,
            f'{self.position.x:.6f}',
            f'{self.position.y:.6f}',
            f'{self.position.z:.6f}'
        ]


@dataclass
class Line:
    """Line segment from OBJ file"""
    start_index: int
    end_index: int
    
    def __repr__(self):
        return f"Line({self.start_index} -> {self.end_index})"


class NetworkTopology:
    """Main network topology structure"""
    
    def __init__(self):
        self.nodes: List[Node] = []
        self.edges: List[Edge] = []
        self.vertices: List[Vertex] = []
        
        self.node_map: Dict[str, Node] = {}
        self.edge_map: Dict[str, Edge] = {}
        
        # Topology data
        self.obj_vertices: List[Vector3] = []
        self.obj_lines: List[Line] = []
        self.node_indices: Set[int] = set()
        self.inline_vertex_indices: Set[int] = set()
        self.vertex_connections: Dict[int, List[int]] = defaultdict(list)
        
    def get_stats(self):
        """Get topology statistics"""
        endpoint_count = sum(1 for n in self.nodes if n.node_type == 'ENDPOINT')
        intersection_count = sum(1 for n in self.nodes if n.node_type == 'INTERSECTION')
        
        return {
            'total_nodes': len(self.nodes),
            'endpoint_nodes': endpoint_count,
            'intersection_nodes': intersection_count,
            'total_edges': len(self.edges),
            'total_inline_vertices': len(self.vertices),
            'total_obj_vertices': len(self.obj_vertices),
            'total_obj_lines': len(self.obj_lines)
        }


def parse_obj_file(filepath: str, offset: Tuple[float, float, float] = (0, 0, 0),
                   apply_transform: bool = False) -> Tuple[List[Vector3], List[Line]]:
    """
    Parse OBJ file and extract vertices and lines.
    
    Args:
        filepath: Path to OBJ file
        offset: (x, y, z) offset to apply to all vertices
        apply_transform: If True, apply coordinate transform (x,y,z) -> (x,z,-y)
    
    Returns:
        Tuple of (vertices, lines)
    """
    vertices = []
    lines = []
    
    print(f"Parsing OBJ file: {filepath}")
    print(f"  Offset: {offset}")
    print(f"  Apply transform (x,y,z) -> (x,z,-y): {apply_transform}")
    
    with open(filepath, 'r') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            
            if line.startswith('v '):
                # Parse vertex: v x y z
                parts = line.split()
                if len(parts) >= 4:
                    x, y, z = float(parts[1]), float(parts[2]), float(parts[3])
                    
                    # Apply coordinate transformation if requested
                    if apply_transform:
                        x_new = x
                        y_new = z
                        z_new = -y
                        x, y, z = x_new, y_new, z_new
                    
                    # Apply offset
                    x += offset[0]
                    y += offset[1]
                    z += offset[2]
                    
                    vertices.append(Vector3(x, y, z))
                    
            elif line.startswith('l '):
                # Parse line: l v1 v2 (1-indexed in OBJ format)
                parts = line.split()
                if len(parts) >= 3:
                    try:
                        v1 = int(parts[1]) - 1  # Convert to 0-indexed
                        v2 = int(parts[2]) - 1
                        lines.append(Line(v1, v2))
                    except ValueError as e:
                        print(f"Warning: Could not parse line {line_num}: {line}")
    
    print(f"Loaded {len(vertices)} vertices and {len(lines)} lines")
    return vertices, lines


def analyze_topology(vertices: List[Vector3], lines: List[Line]) -> NetworkTopology:
    """
    Analyze network topology to classify vertices and build connectivity.
    
    Args:
        vertices: List of 3D vertices
        lines: List of line segments
    
    Returns:
        NetworkTopology object with classified vertices
    """
    topology = NetworkTopology()
    topology.obj_vertices = vertices
    topology.obj_lines = lines
    
    print("\nAnalyzing topology...")
    
    # Count connections for each vertex
    connection_counts = defaultdict(int)
    
    # Initialize all vertices
    for i in range(len(vertices)):
        topology.vertex_connections[i] = []
    
    # Count connections from lines
    for line_idx, line in enumerate(lines):
        connection_counts[line.start_index] += 1
        connection_counts[line.end_index] += 1
        
        topology.vertex_connections[line.start_index].append(line_idx)
        topology.vertex_connections[line.end_index].append(line_idx)
    
    # Classify vertices based on connection count
    for i in range(len(vertices)):
        connections = connection_counts[i]
        
        if connections == 1 or connections >= 3:
            # Node: endpoint (1 connection) or intersection (3+ connections)
            topology.node_indices.add(i)
        elif connections == 2:
            # Inline vertex: exactly 2 connections
            topology.inline_vertex_indices.add(i)
        # Ignore vertices with 0 connections
    
    print(f"  Nodes: {len(topology.node_indices)}")
    print(f"    Endpoints: {sum(1 for i in topology.node_indices if connection_counts[i] == 1)}")
    print(f"    Intersections: {sum(1 for i in topology.node_indices if connection_counts[i] >= 3)}")
    print(f"  Inline vertices: {len(topology.inline_vertex_indices)}")
    
    return topology


def find_edges(topology: NetworkTopology) -> None:
    """
    Find all edges in the network by connecting nodes through inline vertices.
    Explores all line connections from each node, including inline vertex chains.
    Handles multiple edges between the same pair of nodes.
    
    Args:
        topology: NetworkTopology object to populate with edges
    """
    print("\nFinding edges between nodes...")
    
    edge_list = []  # List of (start_node, end_node, inline_vertices)
    processed_paths = set()  # Track processed inline vertex sets (frozenset for set comparison)
    
    # For each node, explore ALL its line connections
    for start_node_idx in topology.node_indices:
        # Get all lines connected to this node
        for line_idx in topology.vertex_connections[start_node_idx]:
            line = topology.obj_lines[line_idx]
            
            # Get the vertex on the other end of this line
            next_vertex = line.end_index if line.start_index == start_node_idx else line.start_index
            
            # If it's another node, create direct edge
            if next_vertex in topology.node_indices:
                # Use canonical form for comparison
                edge_nodes = frozenset([start_node_idx, next_vertex])
                edge_inline = frozenset()  # No inline vertices
                
                path_signature = (edge_nodes, edge_inline)
                
                if path_signature not in processed_paths:
                    edge_list.append((start_node_idx, next_vertex, []))
                    processed_paths.add(path_signature)
            
            # If it's an inline vertex, follow it to find the end node
            elif next_vertex in topology.inline_vertex_indices:
                # Trace through inline vertices to find end node
                path = trace_inline_path(start_node_idx, next_vertex, topology)
                
                if path and len(path) >= 2:
                    end_node_idx = path[-1]
                    
                    # Verify end is a node
                    if end_node_idx in topology.node_indices:
                        # Create path signature to detect duplicates
                        # Use frozenset of inline vertices to detect same path in reverse
                        inline_vertices = path[1:-1] if len(path) > 2 else []
                        edge_nodes = frozenset([start_node_idx, end_node_idx])
                        edge_inline = frozenset(inline_vertices)
                        
                        path_signature = (edge_nodes, edge_inline)
                        
                        if path_signature not in processed_paths:
                            edge_list.append((start_node_idx, end_node_idx, inline_vertices))
                            processed_paths.add(path_signature)
    
    print(f"  Found {len(edge_list)} unique edges")
    
    # Convert edge list to edge compositions dict with unique keys
    edge_compositions = {}
    for i, (start_node, end_node, inline_verts) in enumerate(edge_list):
        # Create unique key for each edge
        edge_key = f"{min(start_node, end_node)}_{max(start_node, end_node)}_{i}"
        
        # Normalize inline vertex order based on edge direction
        if start_node > end_node:
            # Reverse if needed to match canonical form (smaller index first)
            inline_verts = list(reversed(inline_verts))
        
        edge_compositions[edge_key] = {
            'start': min(start_node, end_node),
            'end': max(start_node, end_node),
            'inline': inline_verts
        }
    
    # Store in topology for later use
    topology.edge_compositions = edge_compositions


def trace_inline_path(start_node_idx: int, first_inline_idx: int, topology: NetworkTopology) -> Optional[List[int]]:
    """
    Trace a path from a start node through inline vertices to an end node.
    
    Args:
        start_node_idx: Starting node index
        first_inline_idx: First inline vertex in the path
        topology: NetworkTopology object
    
    Returns:
        Complete path including start node, inline vertices, and end node
    """
    path = [start_node_idx, first_inline_idx]
    visited = {start_node_idx, first_inline_idx}
    current = first_inline_idx
    
    # Follow inline vertices until we hit a node
    while True:
        # Find next vertex
        next_vertex = None
        for line_idx in topology.vertex_connections[current]:
            line = topology.obj_lines[line_idx]
            neighbor = line.end_index if line.start_index == current else line.start_index
            
            if neighbor not in visited:
                next_vertex = neighbor
                break
        
        if next_vertex is None:
            # Dead end, shouldn't happen in a closed network
            return None
        
        path.append(next_vertex)
        visited.add(next_vertex)
        
        # If we hit a node, we're done
        if next_vertex in topology.node_indices:
            return path
        
        # If it's inline, continue
        if next_vertex in topology.inline_vertex_indices:
            current = next_vertex
        else:
            # Hit something that's not a node or inline vertex
            return None
    
    return None


def find_reachable_nodes(start_node_idx: int, topology: NetworkTopology) -> Set[int]:
    """
    Find all nodes reachable from a starting node using BFS.
    
    Args:
        start_node_idx: Starting node index
        topology: NetworkTopology object
    
    Returns:
        Set of reachable node indices
    """
    reachable = set()
    visited = {start_node_idx}
    queue = [start_node_idx]
    
    while queue:
        current = queue.pop(0)
        
        # Check all lines connected to current vertex
        for line_idx in topology.vertex_connections[current]:
            line = topology.obj_lines[line_idx]
            next_vertex = line.end_index if line.start_index == current else line.start_index
            
            if next_vertex not in visited:
                visited.add(next_vertex)
                
                if next_vertex in topology.node_indices:
                    reachable.add(next_vertex)
                
                queue.append(next_vertex)
    
    return reachable


def find_path_between_nodes(start_idx: int, end_idx: int, topology: NetworkTopology) -> Optional[List[int]]:
    """
    Find path between two nodes using DFS.
    
    Args:
        start_idx: Starting node index
        end_idx: Ending node index
        topology: NetworkTopology object
    
    Returns:
        List of vertex indices forming the path, or None if no path found
    """
    visited = {start_idx}
    path = [start_idx]
    
    if dfs_find_path(start_idx, end_idx, topology, visited, path):
        return path
    return None


def dfs_find_path(current: int, target: int, topology: NetworkTopology,
                  visited: Set[int], path: List[int]) -> bool:
    """
    Recursive DFS to find path between nodes.
    
    Args:
        current: Current vertex index
        target: Target vertex index
        topology: NetworkTopology object
        visited: Set of visited vertices
        path: Current path being built
    
    Returns:
        True if path found, False otherwise
    """
    if current == target:
        return True
    
    # Try all connected vertices
    for line_idx in topology.vertex_connections[current]:
        line = topology.obj_lines[line_idx]
        next_vertex = line.end_index if line.start_index == current else line.start_index
        
        if next_vertex in visited:
            continue
        
        # Don't traverse through other nodes (except target)
        if next_vertex in topology.node_indices and next_vertex != target:
            continue
        
        visited.add(next_vertex)
        path.append(next_vertex)
        
        if dfs_find_path(next_vertex, target, topology, visited, path):
            return True
        
        # Backtrack
        path.pop()
        visited.remove(next_vertex)
    
    return False


def create_edge_key(node1: int, node2: int) -> str:
    """Create consistent edge key with smaller index first"""
    return f"{min(node1, node2)}_{max(node1, node2)}"


def build_network_structure(topology: NetworkTopology) -> None:
    """
    Build the final network structure with nodes, edges, and vertices.
    
    Args:
        topology: NetworkTopology object to populate
    """
    print("\nBuilding network structure...")
    
    # Create nodes
    vertex_to_node_id = {}
    connection_counts = defaultdict(int)
    
    # Count connections for type classification
    for line in topology.obj_lines:
        connection_counts[line.start_index] += 1
        connection_counts[line.end_index] += 1
    
    for node_idx, vertex_idx in enumerate(sorted(topology.node_indices)):
        node_id = f"node_{node_idx}"
        position = topology.obj_vertices[vertex_idx]
        connections = connection_counts[vertex_idx]
        
        node_type = 'ENDPOINT' if connections == 1 else 'INTERSECTION'
        
        node = Node(
            id=node_id,
            index=vertex_idx,
            position=position,
            node_type=node_type,
            connection_count=connections
        )
        
        topology.nodes.append(node)
        topology.node_map[node_id] = node
        vertex_to_node_id[vertex_idx] = node_id
    
    print(f"  Created {len(topology.nodes)} nodes")
    
    # Create edges
    edge_key_to_id = {}
    
    for edge_idx, (edge_key, edge_data) in enumerate(sorted(topology.edge_compositions.items())):
        # Extract data from new format
        start_node_idx = edge_data['start']
        end_node_idx = edge_data['end']
        inline_indices = edge_data['inline']
        
        start_node_id = vertex_to_node_id.get(start_node_idx)
        end_node_id = vertex_to_node_id.get(end_node_idx)
        
        if not start_node_id or not end_node_id:
            print(f"  Warning: Skipping edge {edge_key} - node mapping not found")
            continue
        
        edge_id = f"edge_{edge_idx}"
        
        edge = Edge(
            id=edge_id,
            start_node_id=start_node_id,
            end_node_id=end_node_id,
            start_node_index=start_node_idx,
            end_node_index=end_node_idx,
            inline_vertex_indices=inline_indices,
            bidirectional=True
        )
        
        topology.edges.append(edge)
        topology.edge_map[edge_id] = edge
        edge_key_to_id[edge_key] = edge_id
    
    print(f"  Created {len(topology.edges)} edges")
    
    # Create inline vertices
    vertex_count = 0
    
    for edge in topology.edges:
        for edge_vertex_idx, obj_vertex_idx in enumerate(edge.inline_vertex_indices):
            vertex_id = f"vertex_{vertex_count}"
            position = topology.obj_vertices[obj_vertex_idx]
            
            vertex = Vertex(
                id=vertex_id,
                edge_id=edge.id,
                edge_index=edge_vertex_idx,
                index=obj_vertex_idx,
                position=position
            )
            
            topology.vertices.append(vertex)
            vertex_count += 1
    
    print(f"  Created {len(topology.vertices)} inline vertices")


def validate_network(topology: NetworkTopology) -> bool:
    """
    Validate the network structure.
    
    Args:
        topology: NetworkTopology object to validate
    
    Returns:
        True if valid, False otherwise
    """
    print("\nValidating network structure...")
    
    valid = True
    
    # Check that all inline vertices are assigned
    assigned_vertices = set()
    for edge in topology.edges:
        assigned_vertices.update(edge.inline_vertex_indices)
    
    unassigned = topology.inline_vertex_indices - assigned_vertices
    if unassigned:
        print(f"  Warning: {len(unassigned)} inline vertices not assigned to any edge")
        
        # Analyze unassigned vertices
        connection_counts = defaultdict(int)
        for line in topology.obj_lines:
            connection_counts[line.start_index] += 1
            connection_counts[line.end_index] += 1
        
        # Sample a few unassigned vertices for debugging
        sample_size = min(5, len(unassigned))
        print(f"  Sample of unassigned vertices (showing {sample_size}):")
        for i, v_idx in enumerate(sorted(unassigned)[:sample_size]):
            conn_count = connection_counts[v_idx]
            neighbors = []
            for line_idx in topology.vertex_connections[v_idx]:
                line = topology.obj_lines[line_idx]
                neighbor = line.end_index if line.start_index == v_idx else line.start_index
                neighbors.append(neighbor)
            print(f"    Vertex {v_idx}: {conn_count} connections, neighbors: {neighbors}")
        
        valid = False
    
    # Check for duplicate assignments
    all_assigned = []
    for edge in topology.edges:
        all_assigned.extend(edge.inline_vertex_indices)
    
    if len(all_assigned) != len(set(all_assigned)):
        duplicates = len(all_assigned) - len(set(all_assigned))
        print(f"  Warning: {duplicates} vertices assigned to multiple edges")
        valid = False
    
    # Validate edge connections
    invalid_edges = 0
    for edge in topology.edges:
        if not validate_edge_path(edge, topology):
            invalid_edges += 1
            valid = False
    
    if invalid_edges > 0:
        print(f"  Error: {invalid_edges} edges have invalid vertex ordering")
    
    if valid:
        print("  ✓ Network structure is valid")
    else:
        print("  ✗ Network structure has issues (see warnings above)")
    
    return valid


def validate_edge_path(edge: Edge, topology: NetworkTopology) -> bool:
    """
    Validate that an edge's path follows actual line connections.
    
    Args:
        edge: Edge to validate
        topology: NetworkTopology object
    
    Returns:
        True if valid, False otherwise
    """
    # Build complete path: start node + inline vertices + end node
    path = [edge.start_node_index] + edge.inline_vertex_indices + [edge.end_node_index]
    
    if len(path) < 2:
        return False
    
    # Check each consecutive pair
    for i in range(len(path) - 1):
        v1, v2 = path[i], path[i + 1]
        if not are_vertices_connected(v1, v2, topology):
            print(f"  Error in {edge.id}: vertices {v1} -> {v2} not connected in OBJ")
            return False
    
    return True


def are_vertices_connected(v1: int, v2: int, topology: NetworkTopology) -> bool:
    """
    Check if two vertices are directly connected by a line in the OBJ data.
    
    Args:
        v1: First vertex index
        v2: Second vertex index
        topology: NetworkTopology object
    
    Returns:
        True if connected, False otherwise
    """
    for line in topology.obj_lines:
        if (line.start_index == v1 and line.end_index == v2) or \
           (line.start_index == v2 and line.end_index == v1):
            return True
    return False


def export_to_csv(topology: NetworkTopology, obj_filepath: str, output_dir: Optional[str] = None) -> List[str]:
    """
    Export network topology to CSV files.
    
    Args:
        topology: NetworkTopology object to export
        obj_filepath: Original OBJ file path (for naming)
        output_dir: Output directory (default: same as OBJ file)
    
    Returns:
        List of created CSV file paths
    """
    print("\nExporting to CSV files...")
    
    # Determine output directory
    if output_dir is None:
        output_dir = os.path.dirname(obj_filepath)
    if not output_dir:
        output_dir = "."
    
    # Get base name
    obj_basename = os.path.splitext(os.path.basename(obj_filepath))[0]
    
    created_files = []
    
    # Export nodes
    nodes_file = os.path.join(output_dir, f"{obj_basename}_nodes.csv")
    with open(nodes_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['# Network Nodes'])
        writer.writerow(['# Source:', os.path.basename(obj_filepath)])
        writer.writerow([])
        writer.writerow(['NodeId', 'X', 'Y', 'Z', 'NodeType', 'ConnectionCount'])
        
        for node in topology.nodes:
            writer.writerow(node.to_csv_row())
    
    created_files.append(nodes_file)
    print(f"  ✓ {os.path.basename(nodes_file)} ({len(topology.nodes)} nodes)")
    
    # Export edges
    edges_file = os.path.join(output_dir, f"{obj_basename}_edges.csv")
    with open(edges_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['# Network Edges'])
        writer.writerow(['# Source:', os.path.basename(obj_filepath)])
        writer.writerow([])
        writer.writerow(['EdgeId', 'StartNodeId', 'EndNodeId', 'StartNodeIndex', 
                        'EndNodeIndex', 'InlineVertexCount', 'Bidirectional'])
        
        for edge in topology.edges:
            writer.writerow(edge.to_csv_row(None))
    
    created_files.append(edges_file)
    print(f"  ✓ {os.path.basename(edges_file)} ({len(topology.edges)} edges)")
    
    # Export vertices
    vertices_file = os.path.join(output_dir, f"{obj_basename}_vertices.csv")
    with open(vertices_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['# Network Inline Vertices'])
        writer.writerow(['# Source:', os.path.basename(obj_filepath)])
        writer.writerow([])
        writer.writerow(['VertexId', 'EdgeId', 'EdgeIndex', 'ObjVertexIndex', 'X', 'Y', 'Z'])
        
        for vertex in topology.vertices:
            writer.writerow(vertex.to_csv_row())
    
    created_files.append(vertices_file)
    print(f"  ✓ {os.path.basename(vertices_file)} ({len(topology.vertices)} vertices)")
    
    # Export summary
    summary_file = os.path.join(output_dir, f"{obj_basename}_summary.csv")
    stats = topology.get_stats()
    
    with open(summary_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['# Network Topology Summary'])
        writer.writerow(['# Source:', os.path.basename(obj_filepath)])
        writer.writerow([])
        writer.writerow(['Property', 'Value'])
        writer.writerow(['TotalNodes', stats['total_nodes']])
        writer.writerow(['EndpointNodes', stats['endpoint_nodes']])
        writer.writerow(['IntersectionNodes', stats['intersection_nodes']])
        writer.writerow(['TotalEdges', stats['total_edges']])
        writer.writerow(['TotalInlineVertices', stats['total_inline_vertices']])
        writer.writerow(['TotalObjVertices', stats['total_obj_vertices']])
        writer.writerow(['TotalObjLines', stats['total_obj_lines']])
    
    created_files.append(summary_file)
    print(f"  ✓ {os.path.basename(summary_file)}")
    
    return created_files


def process_obj_file(obj_filepath: str,
                     offset: Tuple[float, float, float] = (0, 0, 0),
                     apply_transform: bool = False,
                     output_dir: Optional[str] = None) -> NetworkTopology:
    """
    Main processing function - parse OBJ and create network topology.
    
    Args:
        obj_filepath: Path to OBJ file
        offset: (x, y, z) offset to apply
        apply_transform: Whether to apply coordinate transform
        output_dir: Output directory for CSV files
    
    Returns:
        NetworkTopology object
    """
    print("=" * 70)
    print("NETWORK TOPOLOGY PARSER")
    print("=" * 70)
    
    # Parse OBJ file
    vertices, lines = parse_obj_file(obj_filepath, offset, apply_transform)
    
    # Analyze topology
    topology = analyze_topology(vertices, lines)
    
    # Find edges
    find_edges(topology)
    
    # Build network structure
    build_network_structure(topology)
    
    # Validate
    validate_network(topology)
    
    # Export to CSV
    csv_files = export_to_csv(topology, obj_filepath, output_dir)
    
    # Print summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    stats = topology.get_stats()
    print(f"Nodes:            {stats['total_nodes']}")
    print(f"  Endpoints:      {stats['endpoint_nodes']}")
    print(f"  Intersections:  {stats['intersection_nodes']}")
    print(f"Edges:            {stats['total_edges']}")
    print(f"Inline Vertices:  {stats['total_inline_vertices']}")
    print(f"\nExported {len(csv_files)} CSV files to: {output_dir or os.path.dirname(obj_filepath)}")
    print("=" * 70)
    
    return topology

import bpy

if __name__ == "__main__":
    # Configuration
    obj_file = bpy.path.abspath("//Mesh.obj")  # Relative to .blend file
    
    # Transformation settings
    offset = (0.0, 0.0, 0.0)
    apply_transform = False  # Set to True for (x,y,z) -> (x,z,-y) transform
    
    # Output directory (None = same as OBJ file)
    output_dir = None
    
    # Process the file
    topology = process_obj_file(
        obj_file,
        offset=offset,
        apply_transform=apply_transform,
        output_dir=output_dir
    )
    
    print("\n✓ Processing complete!")


print("Network Topology Parser - Functions defined successfully")
