#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_ROOT/backend"

source .venv/bin/activate

BACKEND="${1:-ollama}"
echo "Running evaluation with backend: $BACKEND"
echo ""

python -m backend.evals.run_eval --backend "$BACKEND"
