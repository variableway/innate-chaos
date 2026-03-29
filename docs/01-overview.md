# HyperLiquid Trading Dashboard - Overview

## Project Name: HyperTrace

A comprehensive trading tracking dashboard that integrates HyperLiquid API data with an intelligent signal engine for ETH, BTC, and GOLD trading decisions based on the OIL-driven risk regime framework.

---

## Core Concept

> **"OIL decides the world's danger, BTC decides if you make money, GOLD decides if you lose big."**

The dashboard implements a multi-asset trading signal system:
- **ETH**: Offensive/amplifier position (high conviction only)
- **BTC**: Base risk asset (risk-on primary)
- **GOLD**: Hedge (risk-off core)
- **OIL**: Risk engine (sole core driver)

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        DATA LAYER                                │
├─────────────────────────────────────────────────────────────────┤
│  HyperLiquid API  │  CoinGecko  │  News Sources  │  Database   │
└─────────┬─────────┴──────┬──────┴───────┬────────┴──────┬──────┘
          │                │              │               │
          ▼                ▼              ▼               ▼
┌─────────────────────────────────────────────────────────────────┐
│                    PROCESSING LAYER (Python)                     │
├─────────────────────────────────────────────────────────────────┤
│  Data Fetcher  │  Signal Engine  │  Risk Classifier  │  DB Ops  │
│                │                 │                   │          │
│  - OIL prices  │  - ETH signal   │  - Regime detect  │  Store   │
│  - GOLD data   │  - BTC signal   │  - Risk score     │  Query   │
│  - BTC/ETH     │  - GOLD signal  │  - Allocation     │  History │
└─────────┬────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────┐
│                      API LAYER (FastAPI)                         │
├─────────────────────────────────────────────────────────────────┤
│  /api/signals        │  /api/prices       │  /api/history       │
│  /api/regime         │  /api/allocation   │  /api/alerts        │
└─────────┬────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────┐
│                   PRESENTATION LAYER (Next.js)                   │
├─────────────────────────────────────────────────────────────────┤
│  Dashboard  │  Signal Cards  │  Charts  │  Regime Indicator     │
│             │                │          │                       │
│  - Overview │  - ETH Score   │  - Price │  - Current State      │
│  - Weights  │  - BTC Score   │  - Trend │  - Recommendations    │
│  - Alerts   │  - GOLD Score  │  - Hist  │  - Actions            │
└─────────────────────────────────────────────────────────────────┘
```

---

## Key Features

### 1. Real-time Signal Engine
- **ETH Signal**: Based on ETH/BTC trend + policy news + OIL risk filter
- **BTC Signal**: Based on OIL risk + BTC momentum + market sentiment
- **GOLD Signal**: Based on OIL movement + GOLD momentum

### 2. Risk Regime Detection
- **Risk-On**: OIL down > 3% → Favor BTC (60%), Reduce GOLD (10%)
- **Neutral**: OIL ±3% → Balanced (BTC 40%, GOLD 30%)
- **Risk-Off**: OIL up > 5% → Favor GOLD (50%), Reduce BTC (20%)

### 3. Dynamic Allocation
- Automatic weight calculation based on signal scores
- Macro filter (TIGHT/EASING) adjustment
- Threshold-based rebalancing (min 10% change)

### 4. Dashboard Views
- **Overview**: Current signals, regime, recommended allocation
- **Asset Detail**: Individual asset metrics and trends
- **History**: Historical signals and performance
- **Alerts**: Configurable signal thresholds

---

## Data Sources

| Data | Source | Frequency |
|------|--------|-----------|
| OIL Prices | HyperLiquid API | 5 minutes |
| BTC/ETH Prices | HyperLiquid API | 5 minutes |
| GOLD Prices | CoinGecko/Yahoo | 5 minutes |
| News/Policy | RSS/Twitter | Real-time |

---

## Signal Calculation Formula

### ETH Signal
```
eth_signal = policy_score * 0.4 + momentum_score * 0.4 - risk_score * 0.2

Where:
- policy_score: 0-1 based on regulatory news keywords
- momentum_score: 0-1 based on ETH/BTC vs MA7
- risk_score: 0-1 based on OIL + GOLD changes
```

### Risk Regime
```
if oil_change > 0.05 and gold_change > 0:
    regime = "RISK_OFF"
elif oil_change < -0.03 and gold_change <= 0:
    regime = "RISK_ON"
else:
    regime = "NEUTRAL"
```

### Allocation Weights
```
compute_weights(eth, btc, gold) with macro_state filter
```

---

## Decision Thresholds

| Signal Range | Action |
|--------------|--------|
| > 0.7 | 🔥 Strong Trend: Heavy ETH position |
| 0.5 - 0.7 | 🟢 Early Trend: Add ETH |
| 0.3 - 0.5 | 🟡 Watch: Small position |
| < 0.3 | 🔴 Avoid ETH |

---

## Technical Stack

### Backend
- **Python 3.11+**
- **FastAPI**: REST API framework
- **SQLAlchemy**: ORM for database
- **SQLite/PostgreSQL**: Data storage
- **Hyperliquid-Python**: Official SDK
- **APScheduler**: Background jobs
- **Pydantic**: Data validation

### Frontend
- **Next.js 14** (App Router)
- **TypeScript**
- **Tailwind CSS**
- **shadcn/ui**: UI components
- **Recharts**: Charts
- **TanStack Query**: Data fetching
- **Zustand**: State management

---

## Project Structure

```
hyper-it/
├── docs/                      # Documentation
│   ├── 01-overview.md
│   ├── 02-architecture.md
│   ├── 03-api-reference.md
│   └── 04-deployment.md
│
├── backend/                   # Python backend
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py           # FastAPI app
│   │   ├── config.py         # Configuration
│   │   ├── database.py       # DB connection
│   │   └── routers/
│   │       ├── signals.py
│   │       ├── prices.py
│   │       └── allocation.py
│   ├── models/
│   │   ├── signal.py
│   │   ├── price.py
│   │   └── allocation.py
│   ├── services/
│   │   ├── hyperliquid.py    # API client
│   │   ├── signal_engine.py  # Signal calculations
│   │   ├── data_fetcher.py   # Data collection
│   │   └── risk_classifier.py
│   ├── utils/
│   │   ├── constants.py
│   │   └── helpers.py
│   ├── tests/
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/                  # Next.js frontend
│   ├── app/
│   │   ├── page.tsx          # Dashboard
│   │   ├── layout.tsx
│   │   ├── api/              # API routes
│   │   └── assets/           # Asset detail pages
│   ├── components/
│   │   ├── dashboard/        # Dashboard components
│   │   ├── ui/               # shadcn components
│   │   └── charts/           # Chart components
│   ├── lib/
│   │   ├── api.ts            # API client
│   │   └── utils.ts
│   ├── types/
│   ├── hooks/
│   ├── package.json
│   └── Dockerfile
│
├── docker-compose.yml
└── README.md
```

---

## Implementation Phases

### Phase 1: Backend Core (Days 1-3)
1. Database models and schema
2. HyperLiquid API integration
3. Signal engine implementation
4. FastAPI endpoints

### Phase 2: Frontend Core (Days 4-6)
1. Next.js project setup with shadcn
2. Dashboard layout and components
3. API integration
4. Charts and visualizations

### Phase 3: Integration & Polish (Days 7-8)
1. End-to-end testing
2. Docker setup
3. Documentation
4. Deployment

---

## Success Metrics

1. **Data Freshness**: Prices updated every 5 minutes
2. **Signal Accuracy**: Correlation with actual market movements
3. **Response Time**: Dashboard loads < 2 seconds
4. **Uptime**: 99%+ availability

---

## Future Enhancements

1. AI-powered news analysis (LLM integration)
2. Historical backtesting
3. Telegram/Discord alerts
4. Paper trading integration
5. Multi-timeframe analysis
6. Correlation matrices
