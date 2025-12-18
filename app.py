import streamlit as st
import pandas as pd
import time
from src.core.models import CVRPTWInstance
from src.solvers.hybrid import HybridSolver
from src.config import HybridConfig, ACOConfig, GAConfig, TabuConfig
from src.utils.plotting import plot_solution, plot_convergence, plot_gantt

st.set_page_config(page_title="Hybrid CVRPTW Solver", layout="wide")

st.title("🚛 Hybrid CVRPTW Solver (Professional Edition)")
st.markdown("""
**Capacitated Vehicle Routing Problem with Time Windows**
Solved using a hybrid pipeline: **ACO (Ant Colony) → GA (Genetic Algo) → Tabu Search**.
""")

# --- Sidebar ---
st.sidebar.header("Instance Settings")
n_customers = st.sidebar.slider("Number of Customers", 10, 100, 25)
capacity = st.sidebar.number_input("Vehicle Capacity", 50, 500, 100)
grid_size = st.sidebar.number_input("Grid Size", 50, 500, 100)
tw_width = st.sidebar.slider("Time Window Width Ratio", 0.1, 0.5, 0.2, help="Larger = Looser constraints")

st.sidebar.header("Algorithm Parameters")
n_ants = st.sidebar.slider("ACO Ants", 5, 50, 10)
n_gens = st.sidebar.slider("GA Generations", 10, 200, 50)
tabu_steps = st.sidebar.slider("Tabu Steps", 10, 200, 50)

# --- Main Logic ---
if st.button("Generate Instance & Solve"):
    with st.spinner("Generating Instance..."):
        instance = CVRPTWInstance(
            num_customers=n_customers,
            vehicle_capacity=capacity,
            grid_size=grid_size,
            tw_width_ratio=tw_width
        )
        st.session_state['instance'] = instance
        
    with st.spinner("Running Hybrid Solver..."):
        # Create Config
        config = HybridConfig(
            aco=ACOConfig(n_ants=n_ants, iterations=5),
            ga=GAConfig(population_size=50, generations=n_gens),
            tabu=TabuConfig(max_steps=tabu_steps)
        )
        
        solver = HybridSolver(instance, config)
        start_time = time.time()
        solution = solver.solve()
        end_time = time.time()
        st.session_state['solution'] = solution
        st.session_state['solve_time'] = end_time - start_time

# --- Results Display ---
if 'solution' in st.session_state:
    sol = st.session_state['solution']
    inst = st.session_state['instance']
    
    # Metrics
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Distance", f"{sol.total_distance:.2f}")
    c2.metric("Total Wait Time", f"{sol.total_wait:.2f}")
    c3.metric("Vehicles Used", len(sol.routes))
    c4.metric("Compute Time", f"{st.session_state['solve_time']:.2f}s")
    
    # Visualization
    col_map, col_data = st.columns([2, 1])
    
    with col_map:
        st.subheader("Route Visualization")
        fig = plot_solution(inst, sol)
        st.pyplot(fig)
        
        if hasattr(sol, 'history'):
            st.subheader("Convergence Analysis")
            fig_conv = plot_convergence(sol.history)
            st.pyplot(fig_conv)
            
        st.subheader("Schedule Gantt Chart")
        fig_gantt = plot_gantt(sol)
        st.pyplot(fig_gantt)
        
    with col_data:
        st.subheader("Detailed Schedule")
        schedule_data = []
        for r_idx, route in enumerate(sol.routes):
            for n_idx, node in enumerate(route.nodes):
                if node.id == 0: continue # Skip depot in table for brevity
                
                # Find schedule info
                # route.nodes matches route.schedule indices
                sched = route.schedule[n_idx]
                arrival, wait, start, depart = sched
                
                schedule_data.append({
                    "Vehicle": r_idx + 1,
                    "Customer": node.id,
                    "Arrival": f"{arrival:.1f}",
                    "Window": f"[{node.ready_time:.1f}, {node.due_date:.1f}]",
                    "Wait": f"{wait:.1f}",
                    "Depart": f"{depart:.1f}"
                })
        
        df = pd.DataFrame(schedule_data)
        st.dataframe(df, height=600)

else:
    st.info("Adjust settings and click 'Generate Instance & Solve' to start.")
