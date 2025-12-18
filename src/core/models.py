import math
import random
from dataclasses import dataclass, field
from typing import List, Tuple, Optional

@dataclass(frozen=True)
class Node:
    """Represents a customer or depot in the CVRPTW graph."""
    id: int
    x: float
    y: float
    demand: float
    ready_time: float
    due_date: float
    service_time: float

    def distance_to(self, other: 'Node') -> float:
        return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)

@dataclass
class Route:
    """Represents a vehicle route starting and ending at the depot."""
    nodes: List[Node] = field(default_factory=list)
    total_distance: float = 0.0
    total_load: float = 0.0
    # Schedule stores (arrival_time, wait_time, start_service_time, departure_time) for each node
    schedule: List[Tuple[float, float, float, float]] = field(default_factory=list)
    
    def __post_init__(self):
        # We assume the route is initialized empty or needs recalculation if nodes are passed
        pass

    def is_feasible(self, capacity: float, distance_matrix: List[List[float]]) -> bool:
        """
        Checks if the route is feasible regarding Capacity and Time Windows.
        This method re-calculates the schedule to verify time windows.
        """
        if not self.nodes:
            return True

        # 1. Check Capacity
        if sum(node.demand for node in self.nodes) > capacity:
            return False

        # 2. Check Time Windows & Flow
        current_time = 0.0
        # Assuming the first node is the depot and it starts at 0
        # But usually routes in VRP lists don't include start/end depot explicitly in the list 
        # unless we design it that way. 
        # Let's assume self.nodes includes the full path: Depot -> C1 -> C2 -> ... -> Depot
        
        # However, standard VRP representation usually lists just customers.
        # Let's stick to the standard: self.nodes contains [Depot, C1, C2, ..., Depot]
        # If it doesn't, we can't check feasibility correctly without knowing the depot.
        # For this implementation, we will ensure Route objects always include Depots at start/end.
        
        for i in range(len(self.nodes) - 1):
            curr_node = self.nodes[i]
            next_node = self.nodes[i+1]
            
            dist = distance_matrix[curr_node.id][next_node.id]
            arrival_time = current_time + dist
            
            # Wait if early
            wait_time = max(0.0, next_node.ready_time - arrival_time)
            start_service = arrival_time + wait_time
            
            # Check late
            if start_service > next_node.due_date:
                return False
            
            # Update for next iteration
            current_time = start_service + next_node.service_time
            
        return True

    def calculate_metrics(self, distance_matrix: List[List[float]]):
        """
        Calculates total distance, load, and generates the schedule.
        Assumes self.nodes is [Depot, ..., Depot].
        """
        self.total_distance = 0.0
        self.total_load = 0.0
        self.schedule = []
        
        current_time = 0.0
        
        # Initial node (Depot)
        if not self.nodes:
            return

        # Depot schedule: Arrival=0, Wait=0, Start=0, Depart=0 (simplified)
        # Actually, depot might have a window, but usually we start at 0.
        self.schedule.append((0.0, 0.0, 0.0, 0.0)) 
        
        for i in range(len(self.nodes) - 1):
            curr_node = self.nodes[i]
            next_node = self.nodes[i+1]
            
            dist = distance_matrix[curr_node.id][next_node.id]
            self.total_distance += dist
            
            arrival_time = self.schedule[-1][3] + dist # Depart of prev + dist
            
            wait_time = max(0.0, next_node.ready_time - arrival_time)
            start_service = arrival_time + wait_time
            departure_time = start_service + next_node.service_time
            
            self.schedule.append((arrival_time, wait_time, start_service, departure_time))
            self.total_load += next_node.demand

class CVRPTWInstance:
    """
    Manages the problem instance: nodes, constraints, and distance matrix.
    """
    def __init__(self, num_customers: int, vehicle_capacity: float, 
                 min_demand: int = 1, max_demand: int = 10,
                 grid_size: int = 100, time_horizon: int = 200,
                 tw_width_ratio: float = 0.2):
        self.num_customers = num_customers
        self.vehicle_capacity = vehicle_capacity
        self.nodes: List[Node] = []
        self.distance_matrix: List[List[float]] = []
        
        self._generate_random_instance(min_demand, max_demand, grid_size, time_horizon, tw_width_ratio)

    def _generate_random_instance(self, min_d, max_d, grid, horizon, tw_ratio):
        # 1. Create Depot
        depot = Node(id=0, x=grid/2, y=grid/2, demand=0, 
                     ready_time=0, due_date=horizon, service_time=0)
        self.nodes.append(depot)
        
        # 2. Create Customers
        for i in range(1, self.num_customers + 1):
            x = random.uniform(0, grid)
            y = random.uniform(0, grid)
            demand = random.randint(min_d, max_d)
            service_time = random.randint(1, 5)
            
            # Generate feasible time windows based on distance from depot
            dist_from_depot = depot.distance_to(Node(0, x, y, 0, 0, 0, 0))
            min_arrival = dist_from_depot
            max_arrival = horizon - dist_from_depot - service_time
            
            if min_arrival > max_arrival:
                # Fallback if too far
                min_arrival = 0
                max_arrival = horizon
            
            start_window = random.uniform(min_arrival, max_arrival - 10)
            # Width of time window
            width = horizon * tw_ratio
            end_window = min(start_window + width, max_arrival)
            
            self.nodes.append(Node(i, x, y, demand, start_window, end_window, service_time))
            
        # 3. Compute Distance Matrix
        size = len(self.nodes)
        self.distance_matrix = [[0.0] * size for _ in range(size)]
        for i in range(size):
            for j in range(size):
                self.distance_matrix[i][j] = self.nodes[i].distance_to(self.nodes[j])

    def get_depot(self) -> Node:
        return self.nodes[0]
    
    def get_customers(self) -> List[Node]:
        return self.nodes[1:]
