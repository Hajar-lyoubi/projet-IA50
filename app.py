# app.py
import os
import io
import time
from pathlib import Path

import streamlit as st
import pandas as pd

from src.core.models import CVRPTWInstance
from src.solvers.hybrid import HybridSolver
from src.config import HybridConfig, ACOConfig, GAConfig, TabuConfig
from src.utils.plotting import plot_solution, plot_convergence, plot_gantt

from src.utils.solomon_loader import instance_from_solomon


# -----------------------------
# Helpers
# -----------------------------
def project_root() -> Path:
    # app.py est à la racine du projet
    return Path(__file__).resolve().parent


def solomon_dir() -> Path:
    # ✅ Corrige le bug "No Solomon .txt files found":
    # tes fichiers sont dans src/data/solomon (pas data/solomon)
    return project_root() / "src" / "data" / "solomon"


def list_solomon_files() -> list[str]:
    folder = solomon_dir()
    if not folder.exists():
        return []
    return sorted([p.name for p in folder.iterdir() if p.is_file() and p.suffix.lower() == ".txt"])


def run_solver(instance: CVRPTWInstance, n_ants: int, n_gens: int, tabu_steps: int):
    config = HybridConfig(
        aco=ACOConfig(n_ants=n_ants, iterations=5),
        ga=GAConfig(population_size=50, generations=n_gens),
        tabu=TabuConfig(max_steps=tabu_steps),
    )
    solver = HybridSolver(instance, config)
    t0 = time.time()
    sol = solver.solve()
    t1 = time.time()
    return sol, (t1 - t0)


# -----------------------------
# UI
# -----------------------------
st.set_page_config(page_title="Hybrid CVRPTW Solver", layout="wide")

st.title("🚛 Hybrid CVRPTW Solver (Professional Edition)")
st.markdown(
    """
**Capacitated Vehicle Routing Problem with Time Windows**
Solved using a hybrid pipeline: **ACO (Ant Colony) → GA (Genetic Algo) → Tabu Search**.
"""
)

# ✅ 2 pages (Solver / Benchmarks)
page = st.sidebar.radio("Navigation", ["Solver (Random/Solomon - single run)", "Benchmarks (Solomon - batch)"])

# Shared algorithm params
st.sidebar.header("Algorithm Parameters")
n_ants = st.sidebar.slider("ACO Ants", 5, 50, 10)
n_gens = st.sidebar.slider("GA Generations", 10, 200, 50)
tabu_steps = st.sidebar.slider("Tabu Steps", 10, 200, 50)


 # =========================================
# PAGE 1: Solver (Random - single run)
# =========================================
if page.startswith("Solver"):
    st.subheader("🧩 Problem Configuration (Random Instance)")

    st.sidebar.header("Instance Settings")
    n_customers = st.sidebar.slider("Number of Customers", 10, 100, 25)
    capacity = st.sidebar.number_input("Vehicle Capacity", 50, 500, 100)
    grid_size = st.sidebar.number_input("Grid Size", 50, 500, 100)
    tw_width = st.sidebar.slider(
        "Time Window Width Ratio",
        0.10,
        0.50,
        0.20,
        help="Larger = looser constraints (wider time windows)",
    )

    if st.button("Generate Instance & Solve"):
        with st.spinner("Generating random instance..."):
            instance = CVRPTWInstance(
                num_customers=n_customers,
                vehicle_capacity=capacity,
                grid_size=grid_size,
                tw_width_ratio=tw_width,
            )
            st.session_state["instance"] = instance

        with st.spinner("Running Hybrid Solver..."):
            solution, solve_time = run_solver(
                instance,
                n_ants=n_ants,
                n_gens=n_gens,
                tabu_steps=tabu_steps,
            )
            st.session_state["solution"] = solution
            st.session_state["solve_time"] = solve_time

    # Display results
    if "solution" in st.session_state:
        sol = st.session_state["solution"]
        inst = st.session_state["instance"]

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Distance", f"{sol.total_distance:.2f}")
        c2.metric("Total Wait Time", f"{sol.total_wait:.2f}")
        c3.metric("Vehicles Used", len(sol.routes))
        c4.metric("Compute Time", f"{st.session_state['solve_time']:.2f}s")

        col_map, col_data = st.columns([2, 1])

        with col_map:
            st.subheader("Route Visualization")
            st.pyplot(plot_solution(inst, sol))

            if hasattr(sol, "history"):
                st.subheader("Convergence Analysis")
                st.pyplot(plot_convergence(sol.history))

            st.subheader("Schedule Gantt Chart")
            st.pyplot(plot_gantt(sol))

        with col_data:
            st.subheader("Detailed Schedule")
            schedule_data = []
            for r_idx, route in enumerate(sol.routes):
                for n_idx, node in enumerate(route.nodes):
                    if node.id == 0:
                        continue
                    arrival, wait, start, depart = route.schedule[n_idx]
                    schedule_data.append(
                        {
                            "Vehicle": r_idx + 1,
                            "Customer": node.id,
                            "Arrival": f"{arrival:.1f}",
                            "Window": f"[{node.ready_time:.1f}, {node.due_date:.1f}]",
                            "Wait": f"{wait:.1f}",
                            "Depart": f"{depart:.1f}",
                        }
                    )
            st.dataframe(pd.DataFrame(schedule_data), height=600)
    else:
        st.info("Adjust settings and click 'Generate Instance & Solve' to start.")


# =========================================
# PAGE 2: Benchmarks (Solomon batch runs)
# =========================================
else:
    st.subheader("📊 Benchmarks (Solomon) — batch evaluation")

    files = list_solomon_files()
    if len(files) == 0:
        st.error(
            f"No Solomon .txt files found in:\n{solomon_dir()}\n\n"
            f"➡️ Place your files here: src/data/solomon/*.txt"
        )
        st.stop()

    chosen_mode = st.radio("Benchmark mode", ["Run ONE file", "Run ALL files"], horizontal=True)
    if chosen_mode == "Run ONE file":
        chosen_files = [st.selectbox("Choose file", files)]
    else:
        chosen_files = files

    runs_per_instance = st.number_input("Runs per instance (to average randomness)", min_value=1, max_value=50, value=5)

    if st.button("Run Benchmarks"):
        rows = []
        progress = st.progress(0)
        total_jobs = len(chosen_files) * int(runs_per_instance)
        done = 0

        for fname in chosen_files:
            path = solomon_dir() / fname
            # Load once
            instance = instance_from_solomon(str(path))

            costs = []
            times = []
            vehicles = []
            infeasible = 0

            for r in range(int(runs_per_instance)):
                sol, dt = run_solver(instance, n_ants=n_ants, n_gens=n_gens, tabu_steps=tabu_steps)

                cost = sol.fitness()  # distance si faisable, inf sinon
                costs.append(cost)
                times.append(dt)
                vehicles.append(len(sol.routes))
                if cost == float("inf") or (hasattr(sol, "is_feasible") and not sol.is_feasible):
                    infeasible += 1

                done += 1
                progress.progress(min(1.0, done / total_jobs))

            # Aggregate
            costs_finite = [c for c in costs if c != float("inf")]
            row = {
                "instance": fname,
                "runs": int(runs_per_instance),
                "best_cost": min(costs_finite) if costs_finite else float("inf"),
                "avg_cost": (sum(costs_finite) / len(costs_finite)) if costs_finite else float("inf"),
                "avg_time_s": sum(times) / len(times) if times else 0.0,
                "avg_vehicles": sum(vehicles) / len(vehicles) if vehicles else 0.0,
                "infeasible_runs": infeasible,
                "aco_ants": n_ants,
                "ga_gens": n_gens,
                "tabu_steps": tabu_steps,
            }
            rows.append(row)

        df = pd.DataFrame(rows).sort_values(["avg_cost", "best_cost"], ascending=True)
        st.success("Benchmarks finished ✅")
        st.dataframe(df, use_container_width=True)

        # download csv
        csv_bytes = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "Download CSV",
            data=csv_bytes,
            file_name="benchmark_results.csv",
            mime="text/csv",
        )

        st.markdown(
            """
**How to interpret results (quick):**
- **best_cost / avg_cost**: smaller is better (distance).
- **infeasible_runs**: should be 0 (otherwise the solver violates constraints sometimes).
- Run multiple times because ACO/GA are stochastic (random).
"""
        )
