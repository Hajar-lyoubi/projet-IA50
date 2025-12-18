import argparse
import time
from src.core.models import CVRPTWInstance
from src.solvers.hybrid import HybridSolver
from src.config import HybridConfig, ACOConfig, GAConfig, TabuConfig
from src.utils.logger import logger

def main():
    parser = argparse.ArgumentParser(description="Hybrid CVRPTW Solver CLI")
    parser.add_argument("--customers", type=int, default=25, help="Number of customers")
    parser.add_argument("--capacity", type=int, default=100, help="Vehicle capacity")
    parser.add_argument("--ants", type=int, default=10, help="Number of ACO ants")
    parser.add_argument("--gens", type=int, default=50, help="Number of GA generations")
    parser.add_argument("--steps", type=int, default=50, help="Number of Tabu steps")
    
    args = parser.parse_args()
    
    logger.info("Starting Solver via CLI")
    
    instance = CVRPTWInstance(
        num_customers=args.customers,
        vehicle_capacity=args.capacity
    )
    
    config = HybridConfig(
        aco=ACOConfig(n_ants=args.ants),
        ga=GAConfig(generations=args.gens),
        tabu=TabuConfig(max_steps=args.steps)
    )
    
    solver = HybridSolver(instance, config)
    
    start_time = time.time()
    solution = solver.solve()
    end_time = time.time()
    
    logger.info(f"Solved in {end_time - start_time:.2f}s")
    logger.info(f"Total Distance: {solution.total_distance:.2f}")
    logger.info(f"Feasible: {solution.is_feasible}")

if __name__ == "__main__":
    main()
