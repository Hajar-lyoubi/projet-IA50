import matplotlib.pyplot as plt
import numpy as np
from src.core.models import CVRPTWInstance
from src.core.solution import Solution

def plot_solution(instance: CVRPTWInstance, solution: Solution):
    """
    Plots the solution routes on a 2D map.
    Returns the matplotlib figure.
    """
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Plot Depot
    depot = instance.get_depot()
    ax.scatter(depot.x, depot.y, c='red', s=200, marker='s', label='Depot', zorder=5)
    
    # Plot Customers
    custs = instance.get_customers()
    xs = [c.x for c in custs]
    ys = [c.y for c in custs]
    ax.scatter(xs, ys, c='blue', s=50, alpha=0.6, label='Customers')
    
    # Plot Routes
    colors = plt.cm.rainbow(np.linspace(0, 1, len(solution.routes)))
    
    for idx, route in enumerate(solution.routes):
        r_xs = [n.x for n in route.nodes]
        r_ys = [n.y for n in route.nodes]
        ax.plot(r_xs, r_ys, c=colors[idx], linewidth=2, label=f"Route {idx+1}")
        
        # Arrows
        for i in range(len(r_xs)-1):
            ax.arrow(r_xs[i], r_ys[i], (r_xs[i+1]-r_xs[i])*0.5, (r_ys[i+1]-r_ys[i])*0.5, 
                     head_width=2, color=colors[idx])
    
    ax.legend()
    ax.grid(True, linestyle='--', alpha=0.5)
    ax.set_title(f"Best Solution (Dist: {solution.total_distance:.1f})")
    
    return fig

def plot_convergence(history: list):
    """
    Plots the convergence of the hybrid algorithm.
    History is a list of (stage, step, cost).
    """
    fig, ax = plt.subplots(figsize=(10, 4))
    
    stages = ['ACO', 'GA', 'Tabu']
    colors = {'ACO': 'blue', 'GA': 'green', 'Tabu': 'red'}
    
    # Flatten index
    x = []
    y = []
    c = []
    
    current_x = 0
    for stage, step, cost in history:
        x.append(current_x)
        y.append(cost)
        c.append(colors[stage])
        current_x += 1
        
    ax.plot(x, y, color='gray', alpha=0.5, linestyle='--')
    ax.scatter(x, y, c=c, s=20)
    
    # Create custom legend
    from matplotlib.lines import Line2D
    legend_elements = [Line2D([0], [0], marker='o', color='w', label=stage,
                              markerfacecolor=color, markersize=8)
                       for stage, color in colors.items()]
    
    ax.legend(handles=legend_elements)
    ax.set_xlabel("Iterations / Steps")
    ax.set_ylabel("Total Distance")
    ax.set_title("Convergence Analysis")
    ax.grid(True, alpha=0.3)
    
    return fig

def plot_gantt(solution: Solution):
    """
    Plots a Gantt chart of the schedule.
    """
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Y-axis: Vehicles
    # X-axis: Time
    
    yticks = []
    yticklabels = []
    
    colors = plt.cm.rainbow(np.linspace(0, 1, len(solution.routes)))
    
    for r_idx, route in enumerate(solution.routes):
        y = r_idx * 10
        yticks.append(y)
        yticklabels.append(f"Vehicle {r_idx+1}")
        
        for n_idx, node in enumerate(route.nodes):
            if node.id == 0: continue # Skip depot
            
            # Get schedule
            arrival, wait, start, depart = route.schedule[n_idx]
            
            # Service Bar
            ax.barh(y, node.service_time, left=start, height=5, color=colors[r_idx], edgecolor='black', alpha=0.8)
            
            # Wait Bar (if any)
            if wait > 0:
                ax.barh(y, wait, left=arrival, height=3, color='gray', alpha=0.3, hatch='//')
            
            # Label
            ax.text(start + node.service_time/2, y, str(node.id), ha='center', va='center', color='white', fontsize=8, fontweight='bold')
            
    ax.set_yticks(yticks)
    ax.set_yticklabels(yticklabels)
    ax.set_xlabel("Time")
    ax.set_title("Schedule Gantt Chart (Gray = Waiting)")
    ax.grid(True, axis='x', alpha=0.3)
    
    return fig
