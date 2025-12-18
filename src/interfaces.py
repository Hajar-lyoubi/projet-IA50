from abc import ABC, abstractmethod
from typing import Tuple, List, Any
from src.core.models import CVRPTWInstance
from src.core.solution import Solution

class SolverStrategy(ABC):
    """
    Abstract Base Class for all CVRPTW solvers.
    Enforces a common interface.
    """
    
    @abstractmethod
    def solve(self, *args, **kwargs) -> Any:
        """
        Execute the solving strategy.
        Returns can vary (Solution, or Tuple[Solution, History]), 
        but typically should return the best Solution found.
        """
        pass
