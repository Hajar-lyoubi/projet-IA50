#!/bin/bash

echo "========================================"
echo "CVRPTW Hybrid Solver - Starting..."
echo "========================================"
echo ""

# Activate virtual environment
if [ -f .venv/bin/activate ]; then
    echo "Activating virtual environment..."
    source .venv/bin/activate
else
    echo "WARNING: Virtual environment not found!"
    echo "Please run: python -m venv .venv"
    echo "Then: source .venv/bin/activate"
    echo "Then: pip install -r requirements.txt"
    exit 1
fi

# Check if Streamlit is installed
python -c "import streamlit" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
fi

echo ""
echo "Starting Streamlit application..."
echo "The app will open in your browser at http://localhost:8501"
echo ""
echo "Press Ctrl+C to stop the server"
echo "========================================"
echo ""

streamlit run app.py
