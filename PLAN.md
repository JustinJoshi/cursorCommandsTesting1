# Prius Price Tracker

A local web application that compares Toyota Prius prices from Facebook Marketplace using screen capture + local vision AI for extraction, with mobile access via Tailscale.

---

## Hardware

**Primary machine (capture + inference):**
- GPU: NVIDIA RTX 5080 (16GB VRAM)
- CPU: AMD 9900X
- OS: Arch Linux

**Secondary machine (optional, can run frontend or backup inference):**
- GPU: NVIDIA RTX 4060 (8GB VRAM)
- CPU: Intel i7-4770
- OS: Arch Linux

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     Your Computer (Arch)                      │
│                                                              │
│  ┌──────────┐    ┌──────────────┐    ┌──────────────────┐   │
│  │  Screen   │───▶│  Qwen2.5-VL  │───▶│  FastAPI Backend  │   │
│  │  Capture  │    │  (Ollama)    │    │  + SQLite DB      │   │
│  │  (mss)    │    └──────────────┘    └────────┬─────────┘   │
│  └──────────┘                                  │             │
│                                                │             │
│  ┌──────────────────────────────────────────────┘             │
│  │                                                           │
│  │  ┌──────────────────┐                                     │
│  └──▶│  React Frontend   │◀── Tailscale Serve ──▶ Phone      │
│      │  (Vite + Tailwind)│                                   │
│      └──────────────────┘                                    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## How It Works

1. You open Facebook Marketplace in your browser and search "Toyota Prius"
2. Press a hotkey (e.g., Super+Shift+P) or tap "Capture" in the web UI from your phone
3. The Python server screenshots your display using `mss`
4. The screenshot is sent to Qwen2.5-VL-7B running locally via Ollama
5. The model extracts structured data: price, year, model, description, link
6. Data is stored in SQLite
7. An AI price analysis is generated (deal quality assessment)
8. Results appear in the mobile-friendly web dashboard
9. You browse to the next page/listing and repeat

---

## Tech Stack

| Layer | Technology | Rationale |
|-------|-----------|-----------|
| Vision Model | Qwen2.5-VL-7B via Ollama | Free, local, 94.8% DocVQA, runs in ~5GB VRAM quantized |
| Model Fallback | GPT-4o Vision (optional) | Pluggable swap if local model insufficient |
| Backend | FastAPI + Uvicorn | Async, auto-docs at /docs, fast |
| Database | SQLite + SQLModel | Zero-config, type-safe ORM + Pydantic |
| Frontend | React + Vite + Tailwind CSS | Mobile-first responsive design |
| Mobile Access | Tailscale Serve | Private HTTPS access within tailnet |
| Screen Capture | mss | Fast, pure Python, no deps, multi-monitor |
| Hotkey | pynput | Global hotkey listener |
| Evals | pytest + custom metrics | Regression testing for extraction quality |

---

## Project Structure

```
prius-price-tracker/
├── backend/
│   ├── main.py                     # FastAPI app, lifespan, middleware
│   ├── config.py                   # Settings (model, DB path, ports, API keys)
│   ├── database.py                 # SQLite engine + session management
│   ├── models.py                   # SQLModel table definitions
│   │
│   ├── capture/
│   │   ├── __init__.py
│   │   ├── screen.py               # mss screenshot capture
│   │   └── hotkey.py               # pynput global hotkey listener
│   │
│   ├── extraction/
│   │   ├── __init__.py
│   │   ├── base.py                 # Abstract extractor interface
│   │   ├── qwen_local.py           # Qwen2.5-VL via Ollama HTTP API
│   │   ├── openai_vision.py        # GPT-4o Vision fallback
│   │   └── prompts.py              # System/user prompts for extraction
│   │
│   ├── analysis/
│   │   ├── __init__.py
│   │   ├── price_analyzer.py       # Deal quality assessment via LLM
│   │   └── market_data.py          # Fair market value lookup (VinAudit optional)
│   │
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── listings.py             # GET/POST/DELETE listings
│   │   ├── capture.py              # POST /capture trigger
│   │   └── stats.py                # GET /stats (aggregations)
│   │
│   ├── evals/
│   │   ├── ground_truth/           # Screenshot PNGs + expected JSON
│   │   │   ├── listing_001.png
│   │   │   ├── listing_001.json
│   │   │   └── ...
│   │   ├── run_eval.py             # Eval runner (compares model output to ground truth)
│   │   ├── metrics.py              # Exact match, fuzzy match, ROUGE, schema validity
│   │   └── results/                # Timestamped eval run reports
│   │
│   └── requirements.txt
│
├── frontend/
│   ├── index.html
│   ├── package.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   ├── tsconfig.json
│   ├── src/
│   │   ├── main.tsx
│   │   ├── App.tsx
│   │   ├── api/
│   │   │   └── client.ts           # Fetch wrapper for backend API
│   │   ├── components/
│   │   │   ├── ListingCard.tsx      # Mobile card view
│   │   │   ├── ListingTable.tsx     # Desktop table view
│   │   │   ├── PriceChart.tsx       # Price visualizations
│   │   │   ├── DealBadge.tsx        # Good/Fair/Overpriced badge
│   │   │   ├── CaptureButton.tsx    # Trigger capture from phone
│   │   │   ├── FilterBar.tsx        # Year, price range, sort
│   │   │   └── MobileNav.tsx        # Bottom nav for mobile
│   │   └── pages/
│   │       ├── Dashboard.tsx        # Main listing view
│   │       └── ListingDetail.tsx    # Full listing + AI analysis
│   └── public/
│
├── scripts/
│   ├── setup.sh                    # Full setup (ollama, deps, DB init)
│   ├── start.sh                    # Start backend + frontend + tailscale
│   └── run_eval.sh                 # Quick eval runner
│
└── README.md                       # Setup & usage instructions
```

---

## Database Schema

```sql
CREATE TABLE listings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    price REAL NOT NULL,
    year INTEGER NOT NULL,
    model TEXT NOT NULL,              -- "Prius", "Prius Prime", "Prius V", "Prius C"
    trim TEXT,                        -- "LE", "XLE", "Limited", etc.
    mileage INTEGER,                 -- If extractable
    description TEXT,
    link TEXT,                        -- Facebook Marketplace URL
    image_path TEXT,                  -- Local path to saved screenshot crop
    ai_summary TEXT,                  -- Deal quality analysis
    deal_rating TEXT,                 -- "great", "good", "fair", "overpriced"
    estimated_market_value REAL,      -- Fair market estimate
    source_screenshot TEXT,           -- Path to full screenshot used for extraction
    captured_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE eval_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    model_name TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    price_accuracy REAL,
    year_accuracy REAL,
    model_accuracy REAL,
    description_rouge REAL,
    link_extraction_rate REAL,
    valid_json_rate REAL,
    overall_score REAL,
    notes TEXT
);
```

---

## API Endpoints

### Listings
- `GET /api/listings` — List all (query params: year, min_price, max_price, sort_by, limit, offset)
- `GET /api/listings/{id}` — Single listing with full AI analysis
- `POST /api/listings` — Manually add a listing
- `DELETE /api/listings/{id}` — Remove a listing

### Capture
- `POST /api/capture` — Trigger screen capture + extraction (can be called from phone)
- `POST /api/capture/batch` — Capture multiple times with delay (auto-scroll mode)
- `GET /api/capture/status` — Current capture status (idle/processing)

### Stats
- `GET /api/stats` — Aggregate stats (avg/min/max price by year, count by model)
- `GET /api/stats/deals` — Best deals ranked

### Evals
- `POST /api/evals/run` — Trigger an eval run
- `GET /api/evals/results` — List past eval results

---

## Extraction Prompt Strategy

The extraction prompt instructs the model to look at a Facebook Marketplace screenshot and return JSON:

```
You are analyzing a screenshot of Facebook Marketplace Toyota Prius listings.
Extract ALL visible listings into structured JSON.

For each listing, extract:
- title: The listing title as shown
- price: Numeric price in USD (number only, no $ sign)
- year: The model year (integer)
- model: The Prius variant ("Prius", "Prius Prime", "Prius V", "Prius C")
- trim: Trim level if visible ("LE", "XLE", "Limited", etc.) or null
- mileage: Mileage if shown (integer) or null
- description: Any visible description text
- link_text: Any visible URL or link identifier

Return a JSON array of objects. If no listings are visible, return [].
```

---

## Evaluation Framework

### Ground Truth Creation
1. Take 30 screenshots of Facebook Marketplace Prius listings
2. Manually annotate each with correct extracted data
3. Store as pairs: `listing_XXX.png` + `listing_XXX.json`

### Metrics
| Metric | Method | Pass Threshold |
|--------|--------|---------------|
| Price accuracy | Exact numeric match | ≥95% |
| Year accuracy | Exact integer match | ≥98% |
| Model accuracy | Fuzzy string match (≥0.9 similarity) | ≥90% |
| Description quality | ROUGE-L score | ≥0.75 avg |
| Link extraction | Binary (found/not found) | ≥85% |
| Valid JSON rate | Schema validation | 100% |

### Running Evals
```bash
cd backend
python -m evals.run_eval --model qwen2.5vl:7b
python -m evals.run_eval --model gpt-4o  # compare
```

---

## Tailscale Setup

### Prerequisites
Tailscale is already installed on both machines and phone.

### Expose the Frontend

```bash
# On your primary machine (AMD 9900X), after starting the frontend on port 5173:
tailscale serve --bg 5173
```

This makes the frontend accessible at `https://<your-machine>.tail<xxxxx>.ts.net` from any device on your tailnet.

### Expose the Backend API (for direct API calls from phone)

```bash
# Expose backend on a different port path:
tailscale serve --bg --set-path /api http://localhost:8000
```

Or expose on a separate port:
```bash
tailscale serve --bg --tcp 8443 localhost:8000
```

### Access from Phone
1. Open Tailscale app on phone (ensure connected to tailnet)
2. Navigate to `https://<your-machine-name>.tail<xxxxx>.ts.net`
3. The React frontend loads with full mobile responsiveness
4. Tap "Capture" button to trigger screen capture on your computer

### Verify Setup
```bash
tailscale serve status    # See what's being served
tailscale status          # See devices on your tailnet
```

### Reset if Needed
```bash
tailscale serve --bg --remove /    # Remove all serve configs
```

---

## Mobile UI Design

Mobile-first, responsive breakpoints:
- **< 640px (phone):** Single-column card stack, bottom nav, large touch targets
- **640-1024px (tablet):** Two-column grid, side filters
- **> 1024px (desktop):** Table view with inline details, sidebar stats

Key mobile features:
- Large "Capture" FAB (floating action button) always visible
- Pull-to-refresh for latest listings
- Swipe cards to dismiss/archive
- Color-coded deal badges (green=great, yellow=fair, red=overpriced)
- Sticky header with current stats (total listings, avg price)

---

## Setup & Running (Arch Linux)

### One-Time Setup

```bash
# 1. Install Ollama
sudo pacman -S ollama
# Or: curl -fsSL https://ollama.com/install.sh | sh

# 2. Pull the vision model
ollama pull qwen2.5vl:7b

# 3. Install Python dependencies
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 4. Install frontend dependencies
cd ../frontend
npm install

# 5. Initialize database
cd ../backend
python -c "from database import init_db; init_db()"
```

### Running

```bash
# Terminal 1: Start Ollama (if not running as service)
ollama serve

# Terminal 2: Start backend
cd backend
source .venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Terminal 3: Start frontend
cd frontend
npm run dev -- --host 0.0.0.0

# Terminal 4: Expose via Tailscale
tailscale serve --bg 5173
```

Then open Facebook Marketplace in your browser, search "Toyota Prius", and either:
- Press the capture hotkey (Super+Shift+P)
- Or tap "Capture" in the web UI from your phone

---

## Implementation Order

1. Project scaffolding (repo structure, configs, dependency files)
2. Database layer (SQLModel models, engine, migrations)
3. Extraction engine (Ollama client, prompts, pluggable interface)
4. Screen capture module (mss, hotkey listener)
5. FastAPI backend (CRUD routes, capture endpoint)
6. Evaluation framework (ground truth format, metrics, runner)
7. AI price analyzer (deal quality via LLM)
8. React frontend (mobile-first dashboard)
9. Tailscale integration (setup script, docs)
10. End-to-end testing + prompt tuning

---

## Cost

**$0.** Everything runs locally:
- Qwen2.5-VL-7B: Free, Apache 2.0 license
- Ollama: Free, open source
- Tailscale: Free tier (up to 100 devices)
- SQLite: Free
- All libraries: MIT/Apache licensed

Optional paid additions:
- GPT-4o Vision fallback: ~$0.01-0.03 per screenshot
- VinAudit API for market values: ~$0.10 per lookup
