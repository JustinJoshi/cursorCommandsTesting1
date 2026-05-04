#!/usr/bin/env bash
set -euo pipefail

echo "=== Prius Price Tracker Setup ==="
echo ""

# Check for Ollama
if command -v ollama &> /dev/null; then
    echo "[OK] Ollama found"
else
    echo "[INSTALL] Installing Ollama..."
    if command -v pacman &> /dev/null; then
        sudo pacman -S --noconfirm ollama
    else
        curl -fsSL https://ollama.com/install.sh | sh
    fi
fi

# Pull the vision model
echo ""
echo "[MODEL] Pulling Qwen2.5-VL 7B model (this may take a while on first run)..."
ollama pull qwen2.5vl:7b

# Python backend setup
echo ""
echo "[BACKEND] Setting up Python environment..."
cd "$(dirname "$0")/../backend"

if [ ! -d ".venv" ]; then
    python -m venv .venv
fi

source .venv/bin/activate
pip install -q -r requirements.txt
echo "[OK] Python dependencies installed"

# Initialize database
python -c "
import sys
sys.path.insert(0, '..')
from backend.database import init_db
init_db()
print('[OK] Database initialized')
"

# Frontend setup
echo ""
echo "[FRONTEND] Installing Node.js dependencies..."
cd ../frontend

if command -v npm &> /dev/null; then
    npm install
    echo "[OK] Frontend dependencies installed"
else
    echo "[WARN] npm not found. Install Node.js to set up the frontend."
    echo "       On Arch: sudo pacman -S nodejs npm"
fi

echo ""
echo "=== Setup Complete ==="
echo ""
echo "To start the app, run: ./scripts/start.sh"
