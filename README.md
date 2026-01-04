# 🚚 CVRPTW Hybrid Solver

## 🎯 Overview

A hybrid metaheuristic solver for the Capacitated Vehicle Routing Problem with Time Windows (CVRPTW).

**The Problem:** 
- Customers distributed across a geographical area
- Each customer has a time window for service
- Vehicles have capacity constraints
- Objective: minimize total travel distance

**Our Solution:**
A hybrid solver combining three algorithms:
- 🐜 **Ant Colony Optimization** - Constructive route generation
- 🧬 **Genetic Algorithm** - Population-based evolution
- 🎯 **Tabu Search** - Local optimization

## 🚀 Quick Start

### Windows
```bash
run_app.bat
```

### Linux/Mac
```bash
chmod +x run_app.sh
./run_app.sh
```

The script will automatically create a virtual environment, install dependencies, and launch the application.

### Manual Installation

```bash
# Create virtual environment
python -m venv .venv

# Activate it
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Run application
streamlit run app.py
```

## 📁 Project Structure

```
projet-IA50/
├── app.py                  # Main Streamlit application
├── src/
│   ├── solvers/           # Algorithm implementations
│   │   ├── aco.py         # Ant Colony Optimization
│   │   ├── ga.py          # Genetic Algorithm
│   │   ├── tabu.py        # Tabu Search
│   │   └── hybrid.py      # Hybrid solver orchestrator
│   ├── core/              # Data models
│   ├── utils/             # Utility functions
│   └── data/solomon/      # Benchmark instances
├── docs/                  # Technical report & diagrams
└── run_app.bat            # Windows executable
```

## 🎮 Usage

1. Launch the application
2. Select a Solomon benchmark instance or upload custom data
3. Configure algorithm parameters
4. Execute the solver
5. View results:
   - Route visualization
   - Convergence analysis
   - Gantt chart scheduling

## 🧪 Testing & Results

Tested on Solomon benchmark instances, the industry standard for CVRPTW validation.

**Performance:**
- 100% feasibility rate across all instances
- Solution quality within 5-10% of best known results
- Average execution time: 1-2 seconds for 100-customer instances

Detailed results available in `docs/RAPPORT_TECHNIQUE.pdf`.

## 🛠️ Tech Stack

- **Python 3.10+**
- **Streamlit** - Web interface
- **NumPy** - Numerical computations
- **Matplotlib** - Visualization
- **Pandas** - Data handling

## 📚 Key Findings

- Hybrid algorithms outperform individual metaheuristics
- Time window constraints significantly increase problem complexity
- Sequential pipeline approach balances exploration and exploitation
- Proper constraint handling is critical for solution feasibility

## 🐛 Known Issues

- Initial setup may take 1-2 minutes for dependency installation
- Default port 8501 - use `--server.port` flag if occupied
- Parameter tuning may be required for optimal performance on specific instances

## 📖 Documentation

- **Technical Report:** `docs/RAPPORT_TECHNIQUE.pdf`
- **Executable Guide:** `EXECUTABLE_README.md`
- **Code Documentation:** Inline docstrings

## 🎓 Academic Context

**Course:** AI50  
**University:** UTBM (University of Technology of Belfort-Montbéliard)  
**Date:** January 2026  



**Download → Run `run_app.bat` → Solve CVRPTW instances**
