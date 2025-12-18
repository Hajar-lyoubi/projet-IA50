# 🎓 Hybrid CVRPTW Solver - Pedagogical Guide

This project implements a **Hybrid Metaheuristic** to solve the **Capacitated Vehicle Routing Problem with Time Windows (CVRPTW)**. It is designed for a university final project defense.

---

## 1. The Math: What are we solving?

The CVRPTW is a combinatorial optimization problem. We want to find a set of routes for a fleet of vehicles to serve a set of customers.

### Objective
**Minimize Total Distance** traveled by all vehicles.

### Constraints
1.  **Capacity Constraint**: The total demand of customers in a vehicle cannot exceed its capacity $Q$.
    $$ \sum_{i \in Route} d_i \le Q $$
2.  **Flow Constraint**: Every customer must be visited exactly once. Vehicles start and end at the Depot.
3.  **Time Window Constraint (The Hard Part)**:
    *   Each customer $i$ has a time window $[a_i, b_i]$.
    *   A vehicle arriving at time $t_i$ must wait if $t_i < a_i$.
    *   A vehicle **cannot** arrive after $b_i$ (Hard Constraint).
    *   Relationship: $Arrival_j = Departure_i + TravelTime_{ij}$.

---

## 2. The Code Architecture

We split the code to make it modular and readable:

*   **`src/core/`**: The "Data Layer".
    *   `models.py`: Contains `Node`, `Route`, `CVRPTWInstance`.
    *   `solution.py`: The `Solution` class that tracks metrics and history.
*   **`src/solvers/`**: The "Logic Layer".
    *   Modular solvers (`aco.py`, `ga.py`, `tabu.py`) inheriting from a common `SolverStrategy` interface.
    *   `hybrid.py`: The orchestrator that combines them.
*   **`src/config.py`**: Configuration management using strongly-typed Dataclasses.
*   **`src/cli.py`**: Command-line interface for headless execution.
*   **`app.py`**: The "Presentation Layer" (Streamlit Dashboard).

---

## 3. The Algorithm: Why Hybrid?

We use a 3-Stage Pipeline. This is a "State-of-the-Art" approach in Operations Research because single metaheuristics often get stuck.

### Stage 1: Ant Colony Optimization (ACO)
*   **Role**: *Construction*.
*   **Why?** ACO is excellent at finding valid paths in graphs. It builds solutions step-by-step, which makes it easier to respect Time Windows during construction than to fix them later.
*   **Mechanism**: "Ants" walk the graph. If an edge is short and has high pheromone (used by previous good ants), it's chosen.

### Stage 2: Genetic Algorithm (GA)
*   **Role**: *Global Search / Diversification*.
*   **Why?** GA is great at combining good parts of different solutions.
*   **Mechanism**:
    *   **Crossover (OX)**: Takes part of a route from Parent A and fills the rest from Parent B.
    *   **Mutation**: Swaps two customers to introduce randomness.

### Stage 3: Tabu Search (TS)
*   **Role**: *Local Refinement / Intensification*.
*   **Why?** GA gets us "near" the optimum. Tabu Search climbs the local hill to find the absolute best peak nearby.
*   **Mechanism**: It tries moving a customer from one route to another. It uses a "Tabu List" to remember recent moves and prevent cycling (going back and forth).

---

## 4. How to Present (Defense Tips)

*   **Start with the "Why"**: "Logistics companies lose millions due to inefficient routing. Time Windows add a complexity that standard GPS cannot handle."
*   **Demo First**: Show the Streamlit app immediately. Generate a small instance (20 customers) and solve it. Show the "Wait Time" column in the table.
*   **Explain the "Wait"**: Point out a customer where `Arrival < Ready Time`. Explain that the vehicle sits idle. This proves your algorithm respects the constraints.
*   **Defend the Hybrid Choice**: "I used ACO for initialization because random initialization often fails Time Windows. I used GA for exploration and Tabu for the final polish."
