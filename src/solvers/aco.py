import random
from typing import List, Tuple
from src.core.models import CVRPTWInstance, Route, Node
from src.core.solution import Solution
from src.interfaces import SolverStrategy
from src.config import ACOConfig
from src.utils.logger import logger

class ACOSolver(SolverStrategy):
    """
    Stage 1: Ant Colony Optimization
    Constructs solutions probabilisticly based on pheromones and heuristic info.
    """
    def __init__(self, instance: CVRPTWInstance, config: ACOConfig):
        self.instance = instance
        self.config = config
        
        size = len(instance.nodes)
        self.pheromones = [[1.0 for _ in range(size)] for _ in range(size)]
        logger.debug(f"Initialized ACOSolver with {config.n_ants} ants")

    def solve(self) -> Tuple[List[Solution], List[float]]:
        best_solutions = []
        history = []
        
        global_best_cost = float('inf')
        
        for i in range(self.config.iterations):
            solutions = []
            for _ in range(self.config.n_ants):
                sol = self._construct_solution()
                if sol.is_feasible:
                    solutions.append(sol)
            
            # Evaporation
            for r in range(len(self.pheromones)):
                for c in range(len(self.pheromones)):
                    self.pheromones[r][c] *= (1 - self.config.rho)
            
            # Reinforcement
            current_best = None
            for sol in solutions:
                contribution = 1.0 / (sol.total_distance + 1e-6)
                for r in sol.routes:
                    for k in range(len(r.nodes) - 1):
                        u, v = r.nodes[k].id, r.nodes[k+1].id
                        self.pheromones[u][v] += contribution
                
                if current_best is None or sol.fitness() < current_best.fitness():
                    current_best = sol
            
            if solutions:
                best_solutions.extend(solutions)
                
            # Track history
            if current_best:
                if current_best.fitness() < global_best_cost:
                    global_best_cost = current_best.fitness()
            
            # If no feasible solution found yet, append inf or last best
            cost = global_best_cost if global_best_cost != float('inf') else 0
            history.append(cost)
            logger.debug(f"ACO Iteration {i+1}/{self.config.iterations}: Best Cost {cost:.2f}")
                
        return best_solutions, history

    def _construct_solution(self) -> Solution:
        unvisited = set(self.instance.get_customers())
        routes = []
        
        while unvisited:
            route_nodes = [self.instance.get_depot()]
            current_load = 0.0
            current_time = 0.0
            
            while True:
                curr_node = route_nodes[-1]
                feasible_next = []
                
                # Find feasible candidates
                for cand in unvisited:
                    # Check Capacity
                    if current_load + cand.demand > self.instance.vehicle_capacity:
                        continue
                    
                    # Check Time Window
                    dist = self.instance.distance_matrix[curr_node.id][cand.id]
                    arrival = current_time + dist
                    wait = max(0.0, cand.ready_time - arrival)
                    start = arrival + wait
                    
                    if start <= cand.due_date:
                        feasible_next.append(cand)
                
                if not feasible_next:
                    break
                
                # Select next node
                next_node = self._select_next_node(curr_node, feasible_next)
                route_nodes.append(next_node)
                unvisited.remove(next_node)
                
                # Update state
                current_load += next_node.demand
                dist = self.instance.distance_matrix[curr_node.id][next_node.id]
                arrival = current_time + dist
                wait = max(0.0, next_node.ready_time - arrival)
                current_time = arrival + wait + next_node.service_time
            
            route_nodes.append(self.instance.get_depot())
            routes.append(Route(nodes=route_nodes))
            
        return Solution(routes, self.instance)

    def _select_next_node(self, curr: Node, candidates: List[Node]) -> Node:
        # Probabilistic selection
        probs = []
        for cand in candidates:
            tau = self.pheromones[curr.id][cand.id]
            dist = self.instance.distance_matrix[curr.id][cand.id]
            eta = 1.0 / (dist + 1e-6)
            probs.append((tau ** self.config.alpha) * (eta ** self.config.beta))
            
        total = sum(probs)
        if total == 0:
            return random.choice(candidates)
        
        probs = [p/total for p in probs]
        return random.choices(candidates, weights=probs, k=1)[0]
