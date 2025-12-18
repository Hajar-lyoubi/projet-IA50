from src.core.models import CVRPTWInstance
from src.core.solution import Solution
from src.interfaces import SolverStrategy
from src.config import HybridConfig
from src.solvers.aco import ACOSolver
from src.solvers.ga import GASolver
from src.solvers.tabu import TabuSolver
from src.utils.logger import logger

class HybridSolver(SolverStrategy):
    def __init__(self, instance: CVRPTWInstance, config: HybridConfig):
        self.instance = instance
        self.config = config
        self.aco = ACOSolver(instance, config.aco)
        self.ga = GASolver(instance, config.ga)
        self.tabu = TabuSolver(instance, config.tabu)
        logger.info("Initialized HybridSolver")

    def solve(self) -> Solution:
        full_history = []
        
        # Stage 1: ACO
        logger.info("Starting Stage 1: ACO")
        aco_solutions, aco_hist = self.aco.solve()
        full_history.extend([('ACO', i, cost) for i, cost in enumerate(aco_hist)])
        
        # Stage 2: GA
        logger.info("Starting Stage 2: GA")
        ga_solution, ga_hist = self.ga.solve(aco_solutions)
        full_history.extend([('GA', i, cost) for i, cost in enumerate(ga_hist)])
        
        # Stage 3: Tabu
        logger.info("Starting Stage 3: Tabu")
        final_solution, tabu_hist = self.tabu.solve(ga_solution)
        full_history.extend([('Tabu', i, cost) for i, cost in enumerate(tabu_hist)])
        
        # Attach history to solution for plotting
        final_solution.history = full_history
        logger.info(f"Hybrid Solver Finished. Final Cost: {final_solution.fitness():.2f}")
        
        return final_solution
