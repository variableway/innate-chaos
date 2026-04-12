# Findicators Gap Analysis

> Comparison: `references/briefing/` vs `findicators/`

## Current State Summary

| Feature | Findicators | Briefing |
|---------|-------------|----------|
| Price Data (BTC, ETH, GOLD, OIL) | HyperLiquid adapter | OKX + Finnhub + Yahoo |
| Interest Rates | FRED API + Yahoo fallback | N/A |
| Fear & Greed Index | Missing | alternative.me + CNN |
| AI Macro Analysis | Missing | Claude daily analysis |
| News Aggregation | Missing | Regular + Geopolitical |
| On-chain Metrics | Missing | CoinGlass (20+ metrics) |
| Risk Engine | 5-factor scoring | Basic sentiment |
| Regime Detection | RISK ON/OFF/NEUTRAL | N/A |
| Portfolio Allocation | Yes | Basic |
| Telegram Alerts | Missing | Yes |
| TTS Audio | Missing | OpenAI TTS |
| Database | TimescaleDB | Vercel PostgreSQL |
| Frontend | Next.js + TanStack Query | Next.js + SWR |
| Desktop App | Planned (Tauri) | Web only |

## Key Gaps to Fill

### Data Layer
- [ ] Fear & Greed Index (crypto + stock) - Free APIs
- [ ] News data source integration
- [ ] BTC on-chain metrics (free alternatives to CoinGlass)
- [ ] More stock indices (S&P 500, NASDAQ)

### Intelligence Layer
- [ ] Claude AI integration for macro narrative generation
- [ ] News aggregation and AI ranking
- [ ] Market rating / scoring system (adapt from briefing)

### Output Layer
- [ ] Telegram notifications for regime changes
- [ ] Daily briefing report generation
- [ ] TTS audio briefing (optional)

### Infrastructure
- [ ] Tauri desktop app adaptation
- [ ] Production deployment setup
- [ ] Monitoring and health checks
