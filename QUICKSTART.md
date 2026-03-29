# HyperTrace - Quick Start Guide

Get the HyperTrace trading dashboard running in minutes!

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)
- Git

## One-Command Setup

```bash
# Clone the repository
git clone <repo-url>
cd hyper-it

# Run the setup script
./scripts/setup.sh
```

That's it! The script will:
1. Check Docker installation
2. Create environment files
3. Build Docker images
4. Start all services

## Access the Dashboard

| Service | URL | Description |
|---------|-----|-------------|
| **Dashboard** | http://localhost:3000 | Trading signal dashboard |
| **API Docs** | http://localhost:8000/docs | Interactive API documentation |
| **Health Check** | http://localhost:8000/health | Backend health status |

## Common Commands

```bash
# View logs
make logs

# Or specific service logs
make logs-backend
make logs-frontend

# Stop services
make stop

# Restart services
make restart

# Clean up (removes volumes)
make clean
```

## What You'll See

### Dashboard Features

1. **Price Ticker** - Real-time prices for ETH, BTC, GOLD, OIL
2. **Market Regime** - Current risk status (Risk-On/Neutral/Risk-Off)
3. **Signal Cards** - Trading signals with strength indicators
4. **Allocation Panel** - Portfolio weights with pie chart
5. **Price Chart** - Historical price visualization

### Signal Interpretation

| Signal | Score | Action |
|--------|-------|--------|
| 🔥 Strong | > 70% | Heavy position |
| 🟢 Moderate | 50-70% | Add position |
| 🟡 Weak | 30-50% | Small position |
| 🔴 Avoid | < 30% | Stay out |

### Regime Colors

- 🟢 **Risk-On** - Favorable for BTC/ETH
- 🟡 **Neutral** - Balanced approach
- 🔴 **Risk-Off** - Defensive, favor GOLD

## Next Steps

### Configure Environment Variables

Edit `backend/.env` to customize:
```env
# Database (default works with Docker)
DATABASE_URL=postgresql+asyncpg://hypertrace:hypertrace_secret@db:5432/hypertrace

# Optional: CoinGecko API key for higher rate limits
COINGECKO_API_KEY=your_key_here

# Update interval (default: 5 minutes)
FETCH_INTERVAL_MINUTES=5
```

### Customize Frontend

Edit `frontend/.env.local`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_REFRESH_INTERVAL=30000  # 30 seconds
```

## Troubleshooting

### Port Conflicts
If ports 3000, 8000, or 5432 are in use, modify `docker-compose.yml`:
```yaml
ports:
  - "3001:3000"  # Use port 3001 instead of 3000
```

### Database Issues
```bash
# Reset database
docker-compose down -v
docker-compose up -d db
```

### Check Service Status
```bash
docker-compose ps
```

## Architecture Overview

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Next.js   │────▶│   FastAPI   │────▶│ TimescaleDB │
│  Frontend   │     │   Backend   │     │   (Prices)  │
└─────────────┘     └──────┬──────┘     └─────────────┘
                           │
                    ┌──────┴──────┐
                    │ HyperLiquid │
                    │    SDK      │
                    └─────────────┘
```

## Support

- 📖 [Full Documentation](./docs/)
- 🔧 [Architecture Details](./docs/02-architecture.md)
- 📚 [API Reference](./docs/03-api-reference.md)
- 🐛 [Issue Tracker](../../issues)

## Disclaimer

This software is for educational purposes only. Not financial advice. Always do your own research before making investment decisions.

---

**Happy Trading! 📈**
