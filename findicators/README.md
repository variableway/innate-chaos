# Findicators - Macro Financial Dashboard

Real-time macro financial dashboard tracking GOLD, OIL, BTC, ETH, and interest rates with RISK ON / RISK OFF regime classification.

## Quick Start

```bash
# 1. Clone and enter the project
cd findicators

# 2. Copy environment config
cp backend/.env.example backend/.env
# Edit backend/.env and add your FRED_API_KEY (get one free at https://fred.stlouisfed.org/)

# 3. One-command start (DB + Backend + Frontend)
./dev.sh
```

Or start individually:

```bash
# Start database
docker compose up -d

# Start backend
cd backend && uv run uvicorn app.main:app --reload --port 8000

# Start frontend (in another terminal)
cd frontend && pnpm dev
```

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Architecture

```
Frontend (Next.js) ←→ Backend (FastAPI) ←→ TimescaleDB
                          ↓
              HyperLiquid API (BTC, ETH)
              FRED API (GOLD, OIL, Rates)
```

## Data Sources

| Asset | Source | Frequency |
|-------|--------|-----------|
| BTC, ETH | HyperLiquid (free, no auth) | Every 5 min |
| GOLD, OIL | FRED API (free, requires key) | Daily |
| Interest Rates | FRED API | Daily |

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /api/v1/prices/current` | Latest prices for all assets |
| `GET /api/v1/prices/{asset}/history?days=30` | Price history |
| `GET /api/v1/regime/current` | Current RISK ON/OFF assessment |
| `GET /api/v1/regime/history?days=30` | Regime history |
| `GET /api/v1/signals/current` | Signal breakdown by factor |
| `GET /api/v1/allocation/current` | Suggested portfolio allocation |

## RISK ON / RISK OFF Model

The engine calculates a composite risk score (0-1) from 5 weighted factors:

| Factor | Weight | RISK ON Signal | RISK OFF Signal |
|--------|--------|----------------|-----------------|
| Oil Trend | 20% | Stable/rising | Plunging |
| Gold Trend | 25% | Flat/declining | Surging |
| BTC Momentum | 25% | Strong uptrend | Downtrend |
| Yield Curve | 20% | Normal/steepening | Inverted |
| Volatility | 10% | Low | High |

- **Score >= 0.6**: RISK ON → Favor risk assets
- **Score 0.4-0.6**: NEUTRAL → Balanced allocation
- **Score <= 0.4**: RISK OFF → Favor safe havens

## Local Development

### Prerequisites

- [uv](https://docs.astral.sh/uv/) (Python package manager)
- [pnpm](https://pnpm.io/) (Node package manager)
- Docker (for TimescaleDB)

### Backend (uv)

```bash
cd backend
uv sync                # Install dependencies
uv run uvicorn app.main:app --reload --port 8000
```

### Frontend (pnpm)

```bash
cd frontend
pnpm install           # Install dependencies
pnpm dev               # Start dev server
```

### Database (Docker)

```bash
docker compose up -d   # Start TimescaleDB
```

## Tech Stack

- **Backend**: Python, FastAPI, SQLAlchemy, APScheduler, httpx
- **Frontend**: Next.js 14, React, Tailwind CSS, Recharts, TanStack Query
- **Database**: TimescaleDB (PostgreSQL)
- **Infrastructure**: Docker Compose
