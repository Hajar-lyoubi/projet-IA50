from typing import List, Tuple
from src.core.models import Node, CVRPTWInstance

def load_solomon_txt(path: str) -> Tuple[List[Node], float]:
    """
    Solomon format (classic):
    - first relevant numeric line for depot then customers:
      CUST NO.  XCOORD  YCOORD  DEMAND  READY TIME  DUE DATE  SERVICE TIME
    Returns (nodes, vehicle_capacity)
    Node id must start at 0 for depot.
    """
    lines = []
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if line:
                lines.append(line)

    # Find the line that starts the table (contains "CUST NO")
    start_idx = None
    for i, line in enumerate(lines):
        if "CUST" in line and "NO" in line and "XCOORD" in line:
            start_idx = i + 1
            break
    if start_idx is None:
        raise ValueError("Could not find customer table header in Solomon file.")

    # Vehicle capacity is usually given in a section above (e.g. "NUMBER     CAPACITY")
    # We'll search for a line with two integers after a header containing "CAPACITY"
    capacity = None
    for i, line in enumerate(lines[:start_idx]):
        if "CAPACITY" in line.upper():
            # next non-empty line often has: <numVehicles> <capacity>
            for j in range(i+1, min(i+6, start_idx)):
                parts = lines[j].split()
                if len(parts) >= 2 and parts[0].isdigit():
                    try:
                        capacity = float(parts[1])
                        break
                    except:
                        pass
        if capacity is not None:
            break
    if capacity is None:
        # fallback if not found
        capacity = 200.0

    nodes: List[Node] = []
    # Parse numeric rows: id x y demand ready due service
    for line in lines[start_idx:]:
        parts = line.split()
        if len(parts) < 7:
            continue
        try:
            cid = int(parts[0])
            x = float(parts[1]); y = float(parts[2])
            demand = float(parts[3])
            ready = float(parts[4]); due = float(parts[5])
            service = float(parts[6])
            nodes.append(Node(cid, x, y, demand, ready, due, service))
        except:
            # ignore non-data lines
            continue

    # Ensure depot id is 0
    # In Solomon, depot is customer 0 already.
    nodes = sorted(nodes, key=lambda n: n.id)
    if nodes[0].id != 0:
        raise ValueError("Solomon file does not contain depot with id 0.")

    return nodes, capacity


def instance_from_solomon(path: str) -> CVRPTWInstance:
    nodes, cap = load_solomon_txt(path)
    inst = CVRPTWInstance(num_customers=len(nodes)-1, vehicle_capacity=cap)
    # override random-generated instance
    inst.nodes = nodes
    size = len(nodes)
    inst.distance_matrix = [[0.0]*size for _ in range(size)]
    for i in range(size):
        for j in range(size):
            inst.distance_matrix[i][j] = nodes[i].distance_to(nodes[j])
    return inst
