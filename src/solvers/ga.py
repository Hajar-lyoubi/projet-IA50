import random
from typing import List, Tuple
from src.core.models import CVRPTWInstance, Route, Node
from src.core.solution import Solution
from src.interfaces import SolverStrategy
from src.config import GAConfig
from src.utils.logger import logger

class GASolver(SolverStrategy):
    """
    Stage 2: Genetic Algorithm
    Evolves population using Order Crossover and Mutation.
    """
    def __init__(self, instance: CVRPTWInstance, config: GAConfig):
        self.instance = instance
        self.config = config
        logger.debug(f"Initialized GASolver with pop_size={config.population_size}")

    def solve(self, initial_solutions: List[Solution]) -> Tuple[Solution, List[float]]:
        history = []
        
        # Initialize population
        population = initial_solutions[:self.config.population_size]
        # Fill if needed
        while len(population) < self.config.population_size:
            population.append(self._generate_random_solution())
            
        best_overall = min(population, key=lambda x: x.fitness())
        history.append(best_overall.fitness())
        
        for gen in range(self.config.generations):
            new_pop = []
            
            # Elitism
            new_pop.append(best_overall)
            
            while len(new_pop) < self.config.population_size:
                p1 = self._tournament_selection(population)
                p2 = self._tournament_selection(population)
                
                # Crossover
                child_routes = self._ordered_crossover(p1, p2)
                
                # Mutation
                if random.random() < self.config.mutation_rate:
                    child_routes = self._mutate(child_routes)
                
                child = Solution(child_routes, self.instance)
                new_pop.append(child)
            
            population = new_pop
            current_best = min(population, key=lambda x: x.fitness())
            if current_best.fitness() < best_overall.fitness():
                best_overall = current_best
            
            history.append(best_overall.fitness())
            if gen % 10 == 0:
                logger.debug(f"GA Gen {gen}: Best Cost {best_overall.fitness():.2f}")
                
        return best_overall, history

    def _generate_random_solution(self) -> Solution:
        customers = self.instance.get_customers()
        random.shuffle(customers)
        return self._split_into_routes(customers)

    def _split_into_routes(self, customers: List[Node]) -> Solution:
        routes = []
        route_nodes = [self.instance.get_depot()]
        load = 0
        time = 0
        
        for c in customers:
            dist = self.instance.distance_matrix[route_nodes[-1].id][c.id]
            arrival = time + dist
            wait = max(0, c.ready_time - arrival)
            start = arrival + wait
            
            if (load + c.demand <= self.instance.vehicle_capacity and 
                start <= c.due_date):
                route_nodes.append(c)
                load += c.demand
                time = start + c.service_time
            else:
                route_nodes.append(self.instance.get_depot())
                routes.append(Route(nodes=route_nodes))
                
                route_nodes = [self.instance.get_depot(), c]
                load = c.demand
                dist = self.instance.distance_matrix[0][c.id]
                arrival = dist
                wait = max(0, c.ready_time - arrival)
                time = arrival + wait + c.service_time
                
        route_nodes.append(self.instance.get_depot())
        routes.append(Route(nodes=route_nodes))
        return Solution(routes, self.instance)

    def _tournament_selection(self, pop: List[Solution], k=3) -> Solution:
        candidates = random.sample(pop, k)
        return min(candidates, key=lambda x: x.fitness())

    def _ordered_crossover(self, p1: Solution, p2: Solution) -> List[Route]:
        t1 = [n for r in p1.routes for n in r.nodes if n.id != 0]
        t2 = [n for r in p2.routes for n in r.nodes if n.id != 0]
        
        if not t1 or not t2:
            return p1.routes
            
        size = len(t1)
        start, end = sorted(random.sample(range(size), 2))
        
        child_p = [None] * size
        child_p[start:end] = t1[start:end]
        
        current_idx = end
        for item in t2:
            if item not in child_p:
                if current_idx >= size:
                    current_idx = 0
                child_p[current_idx] = item
                current_idx += 1
                
        return self._split_into_routes(child_p).routes

    def _mutate(self, routes: List[Route]) -> List[Route]:
        flat = [n for r in routes for n in r.nodes if n.id != 0]
        if len(flat) < 2:
            return routes
            
        i, j = random.sample(range(len(flat)), 2)
        flat[i], flat[j] = flat[j], flat[i]
        
        return self._split_into_routes(flat).routes
