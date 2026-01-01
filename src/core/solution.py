from typing import List, Tuple, Optional, Any
from dataclasses import dataclass, field
from src.core.models import Route, CVRPTWInstance

class Solution:
    """Wrapper for a complete solution (list of routes)."""
    def __init__(self, routes: List[Route], instance: CVRPTWInstance):
        self.routes = routes
        self.instance = instance
        self.total_distance = 0.0
        self.total_wait = 0.0
        self.is_feasible = True
        self.history: List[Tuple[str, int, float]] = [] # (Stage, Step, Cost)
        self._calculate_metrics()
        
    def _calculate_metrics(self):
        self.total_distance = 0.0
        self.total_wait = 0.0
        self.is_feasible = True
        for r in self.routes:
            r.calculate_metrics(self.instance.distance_matrix)
            self.total_distance += r.total_distance
            # Sum waiting times from schedule
            self.total_wait += sum(s[1] for s in r.schedule)
            if not r.is_feasible(self.instance.vehicle_capacity, self.instance.distance_matrix):
                self.is_feasible = False

    def fitness(self) -> float:
        # Minimize distance. Penalize infeasibility heavily.
        if not self.is_feasible:
            return float('inf')
        return self.total_distance
