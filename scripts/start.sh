#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

echo "=== Starting Prius Price Tracker ==="
echo ""

# Check if Ollama is running
if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "[START] Starting Ollama server..."
    ollama serve &
    OLLAMA_PID=$!
    sleep 2
    echo "[OK] Ollama started (PID: $OLLAMA_PID)"
else
    echo "[OK] Ollama already running"
fi

# Start backend
echo "[START] Starting FastAPI backend on port 8000..."
cd "$PROJECT_ROOT/backend"
source .venv/bin/activate
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!
echo "[OK] Backend started (PID: $BACKEND_PID)"

# Start frontend
echo "[START] Starting frontend on port 5173..."
cd "$PROJECT_ROOT/frontend"
npm run dev &
FRONTEND_PID=$!
echo "[OK] Frontend started (PID: $FRONTEND_PID)"

echo ""
echo "=== All services running ==="
echo ""
echo "  Frontend:  http://localhost:5173"
echo "  Backend:   http://localhost:8000"
echo "  API Docs:  http://localhost:8000/docs"
echo ""
echo "  Press Ctrl+C to stop all services"
echo ""

# Trap to clean up on exit
cleanup() {
    echo ""
    echo "Shutting down..."
    kill $FRONTEND_PID 2>/dev/null || true
    kill $BACKEND_PID 2>/dev/null || true
    [ -n "${OLLAMA_PID:-}" ] && kill $OLLAMA_PID 2>/dev/null || true
    echo "Done."
}
trap cleanup EXIT INT TERM

# Wait for any process to exit
wait
