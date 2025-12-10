#!/bin/bash
# CQE Environment Setup Script

echo "=== CQE Environment Setup ==="

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Install package in editable mode
echo "Installing CQE package..."
pip install -e .

# Create data directories
echo "Creating data directories..."
mkdir -p data/overlays data/rag data/checkpoints data/golden

# Setup pre-commit hooks
echo "Setting up pre-commit hooks..."
pre-commit install

echo ""
echo "✓ Setup complete!"
echo ""
echo "To activate the environment, run:"
echo "  source venv/bin/activate"
echo ""
echo "To run tests:"
echo "  pytest"
echo ""
echo "To start API server:"
echo "  cqe-server"
