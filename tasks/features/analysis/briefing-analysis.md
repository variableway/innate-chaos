# Briefing Project Analysis Report

> Reference: `references/briefing/` (Day1 Global Briefing)

## 1. Project Overview

A daily financial intelligence dashboard combining real-time market data, AI analysis (Claude), and automated workflows. Built with Next.js 14 + Vercel serverless stack.

## 2. Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 14 App Router, React, TypeScript, SWR |
| Backend | Next.js API Routes (serverless) |
| AI | Claude (claude-sonnet-4-6) via Anthropic SDK |
| Cache | Upstash Redis (24h TTL for analysis) |
| Database | Vercel PostgreSQL (historical metrics) |
| Storage | Vercel Blob (TTS audio) |
| TTS | OpenAI Text-to-Speech |
| Notify | Telegram Bot |
| CI/CD | GitHub Actions (daily 23:00 UTC) |

## 3. Data Sources

| Source | Data | Auth |
|--------|------|------|
| Finnhub API | US stocks (VOO, QQQ, NVDA, TSLA...) | API Key |
| Yahoo Finance | S&P 500, VIX, Gold, Oil, DXY | Free |
| OKX API | Crypto prices (BTC, ETH, SOL...) | Free |
| alternative.me | Crypto Fear & Greed Index | Free |
| CNN | US Stock Fear & Greed Index | Free |
| CoinGlass API | BTC on-chain metrics (20+) | Paid ($29+/mo) |

## 4. Key Architecture Patterns

### Data Flow
```
Frontend (SWR, 5min refresh) -> /api/market-data -> Concurrent API calls -> 60s in-memory cache
```

### Daily Pipeline (GitHub Actions)
1. Fetch market data via APIs
2. Store BTC metrics in PostgreSQL
3. Fetch news (regular + geopolitical)
4. Generate AI analysis via Claude
5. Cache analysis in Redis (24h)
6. Generate TTS audio (optional)
7. Push to Telegram

### AI Analysis Structure
- **Macro Analysis** - Global markets, VIX, gold/oil trends
- **Crypto Analysis** - BTC/ETH performance, sentiment
- **Action Suggestions** - Portfolio recommendations
- **Geopolitical Analysis** - Risk events
- **Top 10 News** - AI-curated with actionable takeaways

## 5. Key Modules

| Module | Responsibility |
|--------|---------------|
| `fetch-stocks.ts` | US stock data via Finnhub |
| `fetch-crypto.ts` | Crypto prices via OKX |
| `fetch-btc-metrics.ts` | 20+ BTC on-chain metrics via CoinGlass |
| `fetch-fear-greed.ts` | Sentiment indices |
| `fetch-news.ts` | Market news aggregation |
| `fetch-geopolitical-news.ts` | Geopolitical risk analysis |
| `generate-analysis.ts` | Claude AI prompt engineering |
| `market-rating.ts` | BTC bottom/top scoring (0-100) |
| `tts.ts` | OpenAI TTS conversion |
| `telegram.ts` | Telegram push notifications |

## 6. Dashboard Tabs

1. **Overview** - Market overview with key indicators
2. **Sentiment** - Fear & Greed indices
3. **BTC Bottom** - On-chain metrics scoring system
4. **Portfolio** - Personal portfolio tracking
5. **News** - AI-curated daily news

## 7. What to Borrow for Findicators

### High Value
- **Multi-source data aggregation pattern** - Use HyperLiquid (already have) + add OKX/Finnhub as fallbacks
- **AI analysis pipeline** - Claude integration for RISK ON/OFF narrative generation
- **Fear & Greed indices** - Free APIs from alternative.me and CNN
- **Market rating system** - BTC bottom/top scoring methodology from `market-rating.ts`
- **News aggregation + AI ranking** - Automated news curation

### Medium Value
- **Telegram notifications** - Push alerts on regime changes
- **TTS audio briefings** - Nice-to-have feature
- **GitHub Actions CI/CD** - Automated daily pipeline

### Skip (Not Applicable)
- Vercel-specific services (PostgreSQL, Blob, Edge) - We use TimescaleDB + local stack
- Serverless architecture - We run local/Tauri
- SWR data fetching - We already use TanStack Query

## 8. Recommended Implementation Priority

1. **Fear & Greed Index** - Free, easy to add, high impact on risk assessment
2. **News Aggregation + AI Analysis** - Core differentiator, use Claude for macro narrative
3. **BTC On-chain Metrics** - If budget allows CoinGlass, otherwise find free alternatives
4. **Market Rating System** - Adapt the 0-100 scoring for our multi-asset risk engine
5. **Telegram Alerts** - Low effort, high value for regime change notifications
