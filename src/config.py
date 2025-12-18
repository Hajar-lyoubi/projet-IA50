from dataclasses import dataclass, field

@dataclass
class ACOConfig:
    n_ants: int = 10
    alpha: float = 1.0
    beta: float = 2.0
    rho: float = 0.1
    iterations: int = 5

@dataclass
class GAConfig:
    population_size: int = 50
    generations: int = 50
    mutation_rate: float = 0.1
    elitism_size: int = 1

@dataclass
class TabuConfig:
    max_steps: int = 50
    tabu_tenure: int = 10
    neighborhood_size: int = 50

@dataclass
class HybridConfig:
    aco: ACOConfig = field(default_factory=ACOConfig)
    ga: GAConfig = field(default_factory=GAConfig)
    tabu: TabuConfig = field(default_factory=TabuConfig)
