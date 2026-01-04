# 🚚 CVRPTW Hybrid Solver

> *Because manually planning delivery routes is so 2010...*

Hey! Welcome to my AI50 project - a hybrid metaheuristic solver for the **Capacitated Vehicle Routing Problem with Time Windows** (aka the "how do I deliver stuff efficiently without breaking physics" problem).

## 🎯 What's This About?

Ever wondered how Amazon delivers your stuff on time? Or how delivery companies figure out which truck goes where? That's what this solves! 

**The Problem:** 
- You have customers scattered around a city
- Each customer wants their delivery in a specific time window (no early, no late)
- Your trucks have limited capacity
- You want to minimize total distance traveled

**The Solution:**
I built a hybrid solver combining three algorithms:
- 🐜 **Ant Colony Optimization** - Ants finding the best paths (nature is cool)
- 🧬 **Genetic Algorithm** - Evolution but for routes
- 🎯 **Tabu Search** - Local optimization with memory

## 🚀 Quick Start

### Option 1: For the Lazy (Recommended 😎)

**Windows:**
```bash
# Just double-click this bad boy
run_app.bat
```

**Linux/Mac:**
```bash
chmod +x run_app.sh
./run_app.sh
```

Wait 30 seconds while it installs stuff, then boom - app opens in your browser!

### Option 2: For the "I Know What I'm Doing" People

```bash
# Create virtual environment
python -m venv .venv

# Activate it
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Mac/Linux

# Install stuff
pip install -r requirements.txt

# Run it
streamlit run app.py
```

## 📁 Project Structure

```
projet-IA50/
├── app.py                  # Main Streamlit app (the pretty UI)
├── src/
│   ├── solvers/           # The brain of the operation
│   │   ├── aco.py         # Ant algorithm
│   │   ├── ga.py          # Genetic algorithm
│   │   ├── tabu.py        # Tabu search
│   │   └── hybrid.py      # The conductor
│   ├── core/              # Data models and stuff
│   ├── utils/             # Helper functions
│   └── data/solomon/      # Benchmark instances
├── docs/                  # Technical report & diagrams
└── run_app.bat            # Your new best friend
```

## 🎮 How to Use

1. **Launch the app** (see Quick Start above)
2. **Pick a Solomon instance** (c101, r101, etc.) or upload your own
3. **Adjust parameters** if you're feeling adventurous
4. **Hit "Solve"** and watch the magic happen
5. **Check out the results:**
   - 🗺️ Route visualization (color-coded trucks)
   - 📊 Convergence graphs (seeing the algorithm improve)
   - 📅 Gantt chart (timeline of deliveries)

## 🧪 What I Tested

Used the famous **Solomon benchmark instances** - basically the industry standard for "does your solver suck or not?"

**Results:**
- ✅ 100% feasibility rate (no cheating with invalid routes)
- ✅ Competitive with state-of-the-art (within 5-10% of best known)
- ✅ Fast execution (~1-2 seconds for 100 customers)

Check `docs/RAPPORT_TECHNIQUE.pdf` for all the nerdy details.

## 🛠️ Tech Stack

- **Python 3.10+** (because we're modern)
- **Streamlit** (for the slick UI)
- **NumPy** (for the math magic)
- **Matplotlib** (for pretty graphs)
- **Pandas** (because data)

## 📚 What I Learned

- Hybrid algorithms > individual algorithms (teamwork makes the dream work)
- Time windows are WAY harder than just capacity constraints
- Python dataclasses are criminally underrated
- Streamlit is amazing for quick prototypes
- ACO is basically controlled chaos and it works

## 🐛 Known Issues

- Sometimes the first run takes a minute (installing dependencies)
- If port 8501 is busy, change it with `streamlit run app.py --server.port 8502`
- Tabu search can be picky about parameters (RTFM in the docs)

## 📖 Documentation

- **Technical Report:** `docs/RAPPORT_TECHNIQUE.pdf` (all the academic stuff)
- **Executable Guide:** `EXECUTABLE_README.md` (for troubleshooting)
- **Code Documentation:** Check the docstrings in the code

## 🎓 Academic Context

**Course:** AI50 - Optimization and Artificial Intelligence  
**University:** UTBM (University of Technology of Belfort-Montbéliard)  
**Date:** January 2026  

## 🤝 Contributing

This is a student project, but if you find bugs or have ideas:
1. Fork it
2. Create a branch
3. Make your changes
4. Submit a PR

Or just open an issue and tell me what's broken 🙃

## 📝 License

MIT License - do whatever you want with it, just don't blame me if your delivery company goes bankrupt.

## 🙏 Acknowledgments

- **Solomon** for the benchmark instances
- **Coffee** for existing
- **Stack Overflow** for debugging my life
- **My brain** for occasionally working

---

**TL;DR:** Download → Run `run_app.bat` → Get optimized delivery routes → Profit? 📦

*Made with ☕ and mild panic by a student who procrastinated until the last week*
