import random
from typing import List, Tuple
from src.core.models import CVRPTWInstance, Route
from src.core.solution import Solution
from src.interfaces import SolverStrategy
from src.config import TabuConfig
from src.utils.logger import logger

class TabuSolver(SolverStrategy):
    """
    Stage 3: Tabu Search
    Local search refinement.
    """
    def __init__(self, instance: CVRPTWInstance, config: TabuConfig):
        self.instance = instance
        self.config = config
        self.tabu_list = []
        logger.debug(f"Initialized TabuSolver with max_steps={config.max_steps}")

    def solve(self, initial_solution: Solution) -> Tuple[Solution, List[float]]:
        current_sol = initial_solution
        best_sol = initial_solution
        history = [best_sol.fitness()]
        
        for step in range(self.config.max_steps):
            neighborhood = self._get_neighborhood(current_sol)
            
            best_neighbor = None
            best_move = None
            
            candidates = []
            for neighbor, move in neighborhood:
                is_tabu = move in self.tabu_list
                if neighbor.fitness() < best_sol.fitness():
                    is_tabu = False
                
                if not is_tabu:
                    candidates.append((neighbor, move))
            
            if not candidates:
                history.append(best_sol.fitness())
                continue
                
            best_neighbor, best_move = min(candidates, key=lambda x: x[0].fitness())
            
            current_sol = best_neighbor
            self.tabu_list.append(best_move)
            if len(self.tabu_list) > self.config.tabu_tenure:
                self.tabu_list.pop(0)
                
            if current_sol.fitness() < best_sol.fitness():
                best_sol = current_sol
            
            history.append(best_sol.fitness())
            if step % 10 == 0:
                logger.debug(f"Tabu Step {step}: Best Cost {best_sol.fitness():.2f}")
                
        return best_sol, history

    def _get_neighborhood(self, solution: Solution) -> List[Tuple[Solution, Tuple]]:
        neighbors = []
        attempts = 0
        max_attempts = self.config.neighborhood_size
        
        routes = solution.routes
        if len(routes) < 1:
            return []

        while attempts < max_attempts:
            move_type = random.choice(['relocate', 'swap'])
            
            if move_type == 'relocate':
                r_idx1 = random.randint(0, len(routes)-1)
                r_idx2 = random.randint(0, len(routes)-1)
                
                r1 = routes[r_idx1]
                if len(r1.nodes) <= 2: 
                    attempts += 1
                    continue
                
                c_idx = random.randint(1, len(r1.nodes)-2)
                customer = r1.nodes[c_idx]
                
                new_r1_nodes = r1.nodes[:c_idx] + r1.nodes[c_idx+1:]
                
                r2 = routes[r_idx2]
                insert_pos = random.randint(1, len(r2.nodes)-1)
                new_r2_nodes = r2.nodes[:insert_pos] + [customer] + r2.nodes[insert_pos:]
                
                new_routes = [r for i, r in enumerate(routes) if i not in [r_idx1, r_idx2]]
                new_routes.append(Route(nodes=new_r1_nodes))
                new_routes.append(Route(nodes=new_r2_nodes))
                
                neighbor = Solution(new_routes, self.instance)
                if neighbor.is_feasible:
                    move = ('relocate', customer.id, r_idx1, r_idx2)
                    neighbors.append((neighbor, move))

            else: # Swap
                r_idx1 = random.randint(0, len(routes)-1)
                r_idx2 = random.randint(0, len(routes)-1)
                
                r1 = routes[r_idx1]
                r2 = routes[r_idx2]
                
                if len(r1.nodes) <= 2 or len(r2.nodes) <= 2:
                    attempts += 1
                    continue
                    
                c_idx1 = random.randint(1, len(r1.nodes)-2)
                c_idx2 = random.randint(1, len(r2.nodes)-2)
                
                cust1 = r1.nodes[c_idx1]
                cust2 = r2.nodes[c_idx2]
                
                if r_idx1 == r_idx2:
                    new_nodes = r1.nodes[:]
                    new_nodes[c_idx1], new_nodes[c_idx2] = new_nodes[c_idx2], new_nodes[c_idx1]
                    new_routes = [r for i, r in enumerate(routes) if i != r_idx1]
                    new_routes.append(Route(nodes=new_nodes))
                else:
                    new_r1_nodes = r1.nodes[:]
                    new_r1_nodes[c_idx1] = cust2
                    new_r2_nodes = r2.nodes[:]
                    new_r2_nodes[c_idx2] = cust1
                    
                    new_routes = [r for i, r in enumerate(routes) if i not in [r_idx1, r_idx2]]
                    new_routes.append(Route(nodes=new_r1_nodes))
                    new_routes.append(Route(nodes=new_r2_nodes))
                
                neighbor = Solution(new_routes, self.instance)
                if neighbor.is_feasible:
                    move = ('swap', cust1.id, cust2.id)
                    neighbors.append((neighbor, move))
            
            attempts += 1
            
        return neighbors
