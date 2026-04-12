# Macro Index 

## Taks 1: 展示宏观品种的价格

宏观品种主要是:
1. GOLD
2. OIL
3. BTC
4. ETH
5. 利率

希望有一个Dashboard可以展示这些价格指数，然后可以有一个金融的判断：
1.  RISK ON模式
2. RISK Off 模式
4. RISK ON 模式操作建议
5. RISK OFF 模式操作建议

GOLD，OIL，BTC，ETH，利率这些都代表什么，战争因素，通胀预期，实际利率，BTC/ETH资产查看，完成这个任务的计划分析，
理解这些指标的宏观含义，然后数据可以考虑hyperliquid获取，经济数据，可能从路易斯安联储网站上查看

请完成一个可行性报告，计划，架构设计，任务分解，所有记录都需要保留，如果代码实现就从一个全新的项目开始

## Task 2: Bug Fix

```
 > [backend internal] load metadata for docker.io/library/python:3.12-slim:
------
Dockerfile:1

--------------------

   1 | >>> FROM python:3.12-slim

   2 |     

   3 |     WORKDIR /app

--------------------

target backend: failed to solve: python:3.12-slim: failed to resolve source metadata for docker.io/library/python:3.12-slim: failed to copy: httpReadSeeker: failed open: failed to do request: Get "https://docker.registry.cyou/v2/library/python/blobs/sha256:d7b0b4e330022bb59824af47e157a93cc31c6af3a75ae6b14004444a14a6292f?ns=docker.io": EOF
```

## Task 2: Setup Local Dev Environment

1. use UV to setup python dev environment, add .gitignore
2. use pnpm to setup local dev environment
3. use docker to setup local dev environment
4. create script to run dev local environment
5. create .gitignore file
6. local dev environment 使用timescale docker作为数据库，数据库名称为macro_index

## Task 3: Do the macro index feature

### 3.0 Analysis Report (DONE)
- [Analysis: Briefing Project](./analysis/briefing-analysis.md) - Complete analysis of reference project
- [Analysis: Findicators Gap Analysis](./analysis/findicators-gap-analysis.md) - Current gaps vs briefing

### 3.1 Data Layer Improvements

#### 3.1.1 Fear & Greed Index Integration

**Crypto Fear & Greed Index** (Primary - Free, No Auth)
- API: `https://api.alternative.me/fng/?limit=1&date_format=kr`
- No API key required
- Response: `{ "data": [{ "value": "45", "value_classification": "Neutral", "timestamp": "2026-04-11" }] }`
- Classifications: 0-24 Extreme Fear, 25-44 Fear, 45-55 Neutral, 56-75 Greed, 76-100 Extreme Greed
- Historical: `?limit=30&date_format=kr` for 30 days

**CNN Fear & Greed Index** (Stock Market)
- No official public API available
- Recommendation: Use alternative.me as primary (covers crypto sentiment well)
- Alternative: Web scraping `https://edition.cnn.com/markets/fear-and-greed` with BeautifulSoup
- Third-party: RapidAPI has `cnn-fear-greed-index` endpoint but reliability varies

**Implementation Plan:**
- [ ] Create `backend/app/adapters/fear_greed.py` following existing `BaseAdapter` pattern
- [ ] Add `sentiment` table to DB: `(time, source, value, classification)`
- [ ] Add API endpoint `GET /api/v1/sentiment/current`
- [ ] Add to scheduler: fetch every 1 hour
- [ ] Integrate sentiment score into SignalEngine as additional risk factor

---

#### 3.1.2 News Aggregation Data Source

**Recommended Stack (All Free Tier):**

| Source | Free Tier | Best For | Auth |
|--------|-----------|----------|------|
| [Finnhub](https://finnhub.io/) | 60 calls/min | Market news, company news | API Key (free) |
| [NewsAPI](https://newsapi.org/) | 100 req/day | General financial news | API Key (free) |
| [Alpha Vantage](https://www.alphavantage.co/) | 500 calls/day, 5/min | News + sentiment scores | API Key (free) |
| [CryptoPanic API](https://cryptopanic.com/api/) | Free tier limited | Crypto-specific news | API Key (free) |

**Recommended Primary: Finnhub + Alpha Vantage**
- Finnhub: `GET https://finnhub.io/api/v1/news?category=general&token=KEY`
- Alpha Vantage: `GET https://www.alphavantage.co/query?function=NEWS_SENTIMENT&apikey=KEY&limit=50`

**Implementation Plan:**
- [ ] Create `backend/app/adapters/news.py` - Finnhub news adapter
- [ ] Add `news` table to DB: `(time, source, title, url, sentiment, category, summary)`
- [ ] Add API endpoints: `GET /api/v1/news/latest`, `GET /api/v1/news/{category}`
- [ ] Add to scheduler: fetch every 30 minutes
- [ ] Feed news data into AI analysis pipeline (Task 3.2)

---

#### 3.1.3 BTC On-Chain Metrics (Free Alternatives to CoinGlass)

| Source | Free Data | URL |
|--------|-----------|-----|
| [Mempool.space](https://mempool.space/docs/api/rest) | Network stats, mempool, fees, hashrate | Free, no auth |
| [Glassnode](https://docs.glassnode.com/data/metric-catalog) | Basic on-chain metrics (freemium) | Free tier limited |
| [Blockchain.info](https://www.blockchain.com/api) | Block explorer data, transaction stats | Free |
| [CryptoQuant](https://userguide.cryptoquant.com/) | Exchange flows, derivatives | Free tier available |

**Primary Recommendation: Mempool.space + Glassnode Free Tier**
- Mempool.space: `GET https://mempool.space/api/v1/mining/hashrate` (free, no auth)
- Glassnode: Basic metrics like active addresses, transaction count (free tier)

**Implementation Plan:**
- [ ] Create `backend/app/adapters/onchain.py` - Mempool.space adapter
- [ ] Add `onchain_metrics` table: `(time, metric_name, value, source)`
- [ ] Fetch: hashrate, mempool size, avg fee, difficulty
- [ ] Add to scheduler: fetch every 15 minutes
- [ ] Use as supplementary signals in risk engine

---

#### 3.1.4 Stock Indices via Yahoo Finance

**Library:** [yfinance](https://pypi.org/project/yfinance/) - Free, no auth
- Already partially implemented in `backend/app/adapters/yahoo_finance.py`
- Extend to cover additional symbols:

| Index | Yahoo Symbol | Description |
|-------|-------------|-------------|
| S&P 500 | `SPY` | US large cap ETF |
| NASDAQ | `QQQ` | US tech ETF |
| VIX | `^VIX` | Volatility index |
| DXY | `DX-Y.NYB` | US Dollar index |
| Russell 2000 | `IWM` | US small cap ETF |

**Rate Limits:** ~360 req/hour (add 1s delay between requests), cache aggressively

**Implementation Plan:**
- [ ] Extend `yahoo_finance.py` adapter with new symbols
- [ ] Add SPY, QQQ, ^VIX, DXY to symbol mapping
- [ ] Add to existing scheduler economic data fetch (24h)
- [ ] Integrate VIX into SignalEngine as volatility factor (replace or complement BTC vol)
- [ ] Add DXY as macro strength indicator

---

#### 3.1.5 HyperLiquid SDK Integration

**SDK:** [hyperliquid-python-sdk](https://github.com/hyperliquid-dex/hyperliquid-python-sdk)
- Free for public data (spot prices, order books, funding rates)
- No API key needed for read-only operations
- Already implemented in `backend/app/adapters/hyperliquid.py`

**Current Coverage:** BTC, ETH, GOLD (PAXG)
**Extend to:**
- OIL futures (if available on HyperLiquid)
- Funding rates for BTC/ETH perpetuals
- Open interest data

**Implementation Plan:**
- [ ] Enhance `hyperliquid.py` to also fetch funding rates and open interest
- [ ] Add these metrics to on-chain metrics table
- [ ] Use funding rates as sentiment signal in risk engine

---

#### 3.1.6 Current Adapter Architecture (Reference)

All adapters follow the `BaseAdapter` pattern:
```
BaseAdapter (abstract)
├── fetch_latest() -> {"asset", "price", "source", "change_24h", "volume_24h"}
├── hyperliquid.py     ✅ BTC, ETH, GOLD
├── coingecko.py       ✅ BTC, ETH, GOLD (fallback)
├── yahoo_finance.py   ✅ OIL, Treasury yields, GOLD
└── fred.py            ✅ Fed rates, yields (requires API key)
```

**New adapters to add:**
```
├── fear_greed.py      🆕 Crypto sentiment (alternative.me)
├── news.py            🆕 Market news (Finnhub + Alpha Vantage)
├── onchain.py         🆕 BTC on-chain (Mempool.space + Glassnode)
```

**Existing adapters to extend:**
```
├── yahoo_finance.py   📝 Add SPY, QQQ, ^VIX, DXY, IWM
└── hyperliquid.py     📝 Add funding rates, open interest
```

---

#### 3.1.7 Frontend Priority (Web First)

Complete web version first using `innate-frontend` skill before Tauri adaptation.
- Use existing Next.js + TanStack Query + Recharts stack
- Add new panels: Sentiment Gauge, News Feed, On-chain Metrics
- Responsive design for desktop browser first

**Implementation Order:**
1. Extend data adapters (backend)
2. Add new DB tables and API endpoints
3. Update scheduler for new data sources
4. Build frontend components for new data
5. Integrate new signals into risk engine

### 3.2 Intelligence Layer 
1. Integrate Claude AI for daily macro narrative generation
2. Build news aggregation + AI ranking pipeline
3. Adapt briefing's market rating system (0-100 scoring) for multi-asset risk engine

### 3.3 Output & Notification Layer
1. Telegram bot for regime change alerts
2. Daily briefing report generation (markdown + optional TTS)

### 3.4 Desktop App (Tauri)
1. Adapt current Next.js frontend for Tauri desktop/web application
2. Ensure API calls work in both web and desktop contexts

### 3.5 Current Project Status
- [Current Project](../../findicators/) has solid foundation: FastAPI backend + Next.js frontend + TimescaleDB
- Risk engine (5-factor) and regime detection already working
- Missing: AI analysis, news, Fear & Greed, notifications, Tauri integration