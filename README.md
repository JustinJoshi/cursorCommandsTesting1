# Prius Price Tracker

A local web application that compares Toyota Prius prices from Facebook Marketplace using screen capture and a local AI vision model (Qwen2.5-VL-7B). Access the dashboard from your phone via Tailscale.

## How It Works

1. Open Facebook Marketplace in your browser and search "Toyota Prius"
2. Press a hotkey or tap "Capture" in the mobile web UI
3. The app screenshots your display and sends it to a local Qwen2.5-VL model
4. The AI extracts listing data: price, year, model, description
5. Each listing gets an AI-generated deal quality assessment
6. Browse results in a mobile-friendly dashboard from your phone

## Requirements

- **Arch Linux** (primary target, works on any Linux)
- **NVIDIA GPU** with 5+ GB VRAM (RTX 3060+ recommended)
- **Python 3.11+**
- **Node.js 20+**
- **Ollama** (for local AI inference)
- **Tailscale** (for phone access)

## Quick Start

```bash
# 1. Clone and enter the repo
git clone <this-repo>
cd prius-price-tracker

# 2. Run the setup script
./scripts/setup.sh

# 3. Start all services
./scripts/start.sh

# 4. (Optional) Expose to phone via Tailscale
./scripts/tailscale-serve.sh
```

## Manual Setup

### Install Ollama and pull the model

```bash
# Arch Linux
sudo pacman -S ollama

# Pull the vision model (~6GB download)
ollama pull qwen2.5vl:7b
```

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Initialize the database
python -c "from backend.database import init_db; init_db()"

# Start the server
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev -- --host 0.0.0.0
```

### Tailscale (phone access)

```bash
# Make sure Tailscale is running and authenticated
sudo systemctl start tailscaled
sudo tailscale up

# Expose the frontend
tailscale serve --bg 5173

# Access from phone at: https://your-machine.tailXXXXX.ts.net
```

## Usage

### From Desktop

Open `http://localhost:5173` in your browser. The API docs are at `http://localhost:8000/docs`.

### From Phone

1. Connect to your Tailscale VPN
2. Navigate to `https://your-machine-name.your-tailnet.ts.net`
3. Tap "Capture Screen" to trigger a capture on your desktop

### Hotkey

Default: `Super+Shift+P` — triggers capture without needing the web UI.

Configure in `.env`:
```
PRIUS_CAPTURE_HOTKEY=<super>+<shift>+p
```

## Configuration

Create a `.env` file in the `backend/` directory:

```env
# Vision model (default: Ollama local)
PRIUS_EXTRACTION_BACKEND=ollama
PRIUS_OLLAMA_BASE_URL=http://localhost:11434
PRIUS_OLLAMA_MODEL=qwen2.5vl:7b

# Optional: OpenAI fallback
PRIUS_OPENAI_API_KEY=sk-...
PRIUS_OPENAI_MODEL=gpt-4o

# Capture settings
PRIUS_CAPTURE_HOTKEY=<super>+<shift>+p
PRIUS_CAPTURE_MONITOR=0

# Debug
PRIUS_DEBUG=true
```

## Evaluation

Test extraction accuracy against annotated ground truth:

```bash
# Add screenshots + JSON pairs to backend/evals/ground_truth/
# Then run:
./scripts/run_eval.sh ollama
./scripts/run_eval.sh openai  # compare models
```

See `backend/evals/ground_truth/README.md` for the annotation format.

## Project Structure

```
├── backend/
│   ├── main.py              # FastAPI application
│   ├── config.py            # Settings (env vars)
│   ├── database.py          # SQLite + SQLModel
│   ├── models.py            # Database models
│   ├── capture/             # Screen capture (mss + hotkey)
│   ├── extraction/          # AI extraction (Ollama / OpenAI)
│   ├── routers/             # API endpoints
│   └── evals/               # Evaluation framework
├── frontend/
│   ├── src/
│   │   ├── App.tsx          # Main app
│   │   ├── api/client.ts    # API client
│   │   └── components/      # React components
│   └── package.json
├── scripts/
│   ├── setup.sh             # One-time setup
│   ├── start.sh             # Start all services
│   ├── tailscale-serve.sh   # Phone access setup
│   └── run_eval.sh          # Run evaluations
├── PLAN.md                  # Detailed project plan
└── README.md                # This file
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | /api/health | Health check |
| GET | /api/listings | List all listings (with filters) |
| GET | /api/listings/{id} | Get single listing |
| POST | /api/listings | Add a listing manually |
| DELETE | /api/listings/{id} | Remove a listing |
| POST | /api/capture | Trigger screen capture |
| POST | /api/capture/batch | Multi-capture with delay |
| GET | /api/capture/status | Current capture status |
| GET | /api/stats | Aggregate statistics |
| GET | /api/stats/deals | Best deals ranked |

## Tech Stack

- **Backend:** FastAPI, SQLite, SQLModel, mss, pynput
- **Frontend:** React, Vite, Tailwind CSS, Recharts
- **AI:** Qwen2.5-VL-7B via Ollama (local, free)
- **Networking:** Tailscale Serve

## Cost

**$0** — everything runs locally with open-source tools.
