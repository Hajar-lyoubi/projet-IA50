from typing import List
import math

def build_distance_matrix(nodes) -> List[List[float]]:
    size = len(nodes)
    dist = [[0.0]*size for _ in range(size)]
    for i in range(size):
        for j in range(size):
            dx = nodes[i].x - nodes[j].x
            dy = nodes[i].y - nodes[j].y
            dist[i][j] = math.hypot(dx, dy)
    return dist
