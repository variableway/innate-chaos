# HyperTrace - Trading Signal Dashboard

A comprehensive trading tracking dashboard that integrates HyperLiquid API data with an intelligent signal engine for ETH, BTC, and GOLD trading decisions.

## Core Concept

> **"OIL decides the world's danger, BTC decides if you make money, GOLD decides if you lose big."**

The dashboard implements a multi-asset trading signal system:
- **ETH**: Offensive/amplifier position (high conviction only)
- **BTC**: Base risk asset (risk-on primary)
- **GOLD**: Hedge (risk-off core)
- **OIL**: Risk engine (sole core driver)

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        FRONTEND (Next.js)                        │
│                   React + TypeScript + Tailwind                  │
└───────────────────────────┬─────────────────────────────────────┘
                            │ HTTP
┌───────────────────────────┴─────────────────────────────────────┐
│                      BACKEND (FastAPI)                           │
│              Python + HyperLiquid SDK + TimescaleDB              │
└───────────────────────────┬─────────────────────────────────────┘
                            │ SQLAlchemy/asyncpg
┌───────────────────────────┴─────────────────────────────────────┐
│                    DATABASE (TimescaleDB)                        │
│         Time-series hypertables for prices & signals             │
└───────────────────────────┬─────────────────────────────────────┘
                            │
┌───────────────────────────┴─────────────────────────────────────┐
│                     EXTERNAL APIs                                │
│   HyperLiquid SDK (OIL, BTC, ETH)  │  CoinGecko (GOLD)         │
└─────────────────────────────────────────────────────────────────┘
```

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Node.js 18+ (for local frontend development)
- Python 3.11+ (for local backend development)

### Run with Docker Compose

```bash
# Clone the repository
git clone <repo-url>
cd hyper-it

# Start all services
docker-compose up -d

# Access the dashboard
open http://localhost:3000

# Access API docs
open http://localhost:8000/docs
```

### Manual Setup

#### 1. Start TimescaleDB
```bash
docker run -d --name timescaledb \
  -e POSTGRES_PASSWORD=hypertrace_secret \
  -e POSTGRES_DB=hypertrace \
  -p 5432:5432 \
  timescale/timescaledb:latest-pg16
```

#### 2. Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env with your configuration

# Run migrations and start
uvicorn app.main:app --reload --port 8000
```

#### 3. Frontend Setup
```bash
cd frontend
npm install

# Create .env.local file
cp .env.local.example .env.local
# Edit .env.local with your configuration

npm run dev
```

## Signal Calculation

### ETH Signal
```
ETH Signal = policy_score * 0.4 + momentum_score * 0.4 - risk_score * 0.2

- Policy Score: Based on regulatory news keywords (0-1)
- Momentum Score: ETH/BTC vs 7-day MA (0 or 1)
- Risk Score: OIL (>5%) + GOLD (>2%) changes (0-1)
```

### Market Regime
```
RISK_OFF: OIL > +5% AND GOLD > 0%     → Defensive, favor GOLD
RISK_ON:  OIL < -3% AND GOLD <= 0%    → Aggressive, favor BTC/ETH
NEUTRAL:  Everything else             → Balanced
```

### Portfolio Allocation
```
Base: Signal-based weights
Apply: Macro filter (TIGHT/EASING)
Reserve: 30% cash buffer
Trigger: Rebalance when change > 10%
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/prices/current` | GET | Current prices for all assets |
| `/api/v1/prices/{asset}` | GET | Price history |
| `/api/v1/signals/current` | GET | Current trading signals |
| `/api/v1/allocation/current` | GET | Portfolio allocation |
| `/api/v1/allocation/rebalance` | POST | Trigger rebalance |
| `/health` | GET | Health check |

## Features

### Implemented ✅
- [x] Real-time price fetching from HyperLiquid SDK
- [x] Signal calculation engine (ETH, BTC, GOLD)
- [x] Market regime detection (Risk-On/Off/Neutral)
- [x] Dynamic portfolio allocation
- [x] TimescaleDB time-series storage
- [x] Next.js dashboard with shadcn/ui
- [x] Interactive price charts
- [x] Signal visualization with progress bars
- [x] Rebalance functionality

### Roadmap 📋
- [ ] WebSocket real-time updates
- [ ] News ingestion pipeline
- [ ] Alert system (webhooks/telegram)
- [ ] Historical backtesting
- [ ] Multi-timeframe analysis
- [ ] Authentication & user preferences

## Project Structure

```
hyper-it/
├── docs/                      # Documentation
│   ├── 01-overview.md
│   ├── 02-architecture.md
│   ├── 03-api-reference.md
│   └── ...
│
├── backend/                   # Python FastAPI
│   ├── app/
│   │   ├── main.py           # FastAPI entry
│   │   ├── config.py         # Settings
│   │   ├── database.py       # TimescaleDB setup
│   │   ├── scheduler.py      # Background jobs
│   │   └── routers/          # API endpoints
│   ├── models/               # Database models
│   ├── services/             # Business logic
│   │   ├── data_fetcher.py   # HyperLiquid SDK
│   │   ├── signal_engine.py  # Signal calculations
│   │   ├── risk_classifier.py
│   │   └── allocation_engine.py
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/                  # Next.js + shadcn/ui
│   ├── app/                  # Next.js app router
│   ├── components/
│   │   ├── dashboard/        # Dashboard components
│   │   └── ui/               # shadcn components
│   ├── lib/                  # Utils & API client
│   ├── hooks/                # React hooks
│   ├── types/                # TypeScript types
│   └── Dockerfile
│
├── docker-compose.yml
└── README.md
```

## Technology Stack

### Backend
- **FastAPI** - Modern Python web framework
- **HyperLiquid Python SDK** - Official SDK for HL API
- **TimescaleDB** - Time-series PostgreSQL extension
- **SQLAlchemy 2.0** - Async ORM
- **APScheduler** - Background job scheduling

### Frontend
- **Next.js 14** - React framework with App Router
- **TypeScript** - Type safety
- **Tailwind CSS** - Utility-first styling
- **shadcn/ui** - Beautiful UI components
- **Recharts** - Data visualization
- **Zustand** - State management

### Infrastructure
- **Docker** - Containerization
- **TimescaleDB** - Time-series data storage
- **Nginx** - Reverse proxy (optional)

## Environment Variables

### Backend (.env)
```env
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/hypertrace
HYPERLIQUID_API_URL=https://api.hyperliquid.xyz
COINGECKO_API_KEY=your_key_here
DEBUG=false
LOG_LEVEL=INFO
FETCH_INTERVAL_MINUTES=5
```

### Frontend (.env.local)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_APP_NAME=HyperTrace
NEXT_PUBLIC_REFRESH_INTERVAL=30000
```

## Database Schema

### Hypertables (Time-Series)
- **prices** - Asset prices (7-day chunks, compressed after 7 days)
- **signals** - Trading signals (7-day chunks)

### Regular Tables
- **allocations** - Portfolio weights
- **news** - Policy/news data

## Decision Thresholds

| Signal Range | Action |
|--------------|--------|
| > 0.7 | 🔥 Strong Trend: Heavy position |
| 0.5 - 0.7 | 🟢 Early Trend: Add position |
| 0.3 - 0.5 | 🟡 Watch: Small position |
| < 0.3 | 🔴 Avoid |

## Screenshots

*Coming soon*

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

MIT License - see LICENSE file for details

## Disclaimer

This software is for educational purposes only. Not financial advice. Always do your own research before making investment decisions.

## Acknowledgments

- [HyperLiquid](https://hyperliquid.xyz/) for the excellent API and SDK
- [TimescaleDB](https://www.timescale.com/) for time-series database
- [shadcn/ui](https://ui.shadcn.com/) for beautiful UI components
