# HyperTrace - Architecture Design

## System Design Overview

This document describes the detailed architecture of the HyperTrace trading dashboard system.

---

## 1. Data Flow Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           EXTERNAL APIS                                  │
├─────────────────────────────────────────────────────────────────────────┤
│  HyperLiquid              CoinGecko              News RSS               │
│  ├─ OIL (perp)           ├─ GOLD price         ├─ Twitter/X            │
│  ├─ BTC (perp)           └─ Crypto data        ├─ Bloomberg            │
│  └─ ETH (perp)                                 └─ Reuters               │
└───────┬───────────────────────┬───────────────────────┬─────────────────┘
        │                       │                       │
        └───────────────────────┼───────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        DATA FETCHER SERVICE                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                   │
│  │ HL Client    │  │ Price        │  │ News         │                   │
│  │              │  │ Aggregator   │  │ Parser       │                   │
│  │ - Connect    │  │              │  │              │                   │
│  │ - Subscribe  │  │ - Normalize  │  │ - Keywords   │                   │
│  │ - Cache      │  │ - Validate   │  │ - Score      │                   │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘                   │
│         └─────────────────┼─────────────────┘                           │
│                           │                                             │
└───────────────────────────┼─────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      SIGNAL ENGINE SERVICE                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌─────────────┐  │
│  │ ETH Signal   │  │ BTC Signal   │  │ GOLD Signal  │  │ Risk        │  │
│  │ Calculator   │  │ Calculator   │  │ Calculator   │  │ Classifier  │  │
│  │              │  │              │  │              │  │             │  │
│  │ Inputs:      │  │ Inputs:      │  │ Inputs:      │  │ Inputs:     │  │
│  │ - ETH/BTC    │  │ - BTC mom    │  │ - GOLD mom   │  │ - OIL       │  │
│  │ - Policy     │  │ - OIL        │  │ - OIL        │  │ - GOLD      │  │
│  │ - OIL/GOLD   │  │ - Regime     │  │ - Regime     │  │             │  │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └──────┬──────┘  │
│         └─────────────────┴─────────────────┴─────────────────┘         │
│                                           │                             │
│  ┌────────────────────────────────────────┴────────────────────────┐   │
│  │                      ALLOCATION ENGINE                           │   │
│  │  - Weight calculation                                             │   │
│  │  - Macro filter (TIGHT/EASING)                                   │   │
│  │  - Threshold check                                               │   │
│  └──────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         DATABASE LAYER                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌─────────────┐  │
│  │ prices       │  │ signals      │  │ allocations  │  │ news        │  │
│  │              │  │              │  │              │  │             │  │
│  │ - asset      │  │ - asset      │  │ - timestamp  │  │ - source    │  │
│  │ - price      │  │ - signal     │  │ - weights    │  │ - content   │  │
│  │ - timestamp  │  │ - score      │  │ - regime     │  │ - score     │  │
│  │ - source     │  │ - timestamp  │  │              │  │ - timestamp │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  └─────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                           API LAYER                                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌─────────────┐  │
│  │ GET          │  │ GET          │  │ GET          │  │ POST        │  │
│  │ /prices      │  │ /signals     │  │ /allocation  │  │ /alerts     │  │
│  │              │  │              │  │              │  │             │  │
│  │ Query:       │  │ Query:       │  │ Response:    │  │ Body:       │  │
│  │ - asset      │  │ - asset      │  │ - weights    │  │ - threshold │  │
│  │ - limit      │  │ - timeframe  │  │ - regime     │  │ - webhook   │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  └─────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        FRONTEND LAYER                                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌─────────────┐  │
│  │ Dashboard    │  │ Asset Detail │  │ History      │  │ Settings    │  │
│  │              │  │              │  │              │  │             │  │
│  │ - Overview   │  │ - Charts     │  │ - Signals    │  │ - Alerts    │  │
│  │ - Signals    │  │ - Metrics    │  │ - Prices     │  │ - Display   │  │
│  │ - Allocation │  │ - Analysis   │  │ - Performance│  │             │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  └─────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Component Details

### 2.1 Data Fetcher Service

**Responsibility**: Fetch and normalize data from external sources

```python
class DataFetcher:
    """
    Orchestrates data collection from multiple sources
    """
    
    async def fetch_all():
        """Fetch all required data in parallel"""
        return await asyncio.gather(
            fetch_hl_prices(),
            fetch_coingecko_prices(),
            fetch_news()
        )
    
    async def fetch_hl_prices():
        """Fetch OIL, BTC, ETH from HyperLiquid"""
        pass
    
    async def fetch_coingecko_prices():
        """Fetch GOLD and other prices from CoinGecko"""
        pass
    
    async def fetch_news():
        """Fetch and parse news for policy signals"""
        pass
```

**Schedule**: Every 5 minutes via APScheduler

---

### 2.2 Signal Engine

**Responsibility**: Calculate trading signals for each asset

#### ETH Signal
```python
class ETHSignalEngine:
    """
    ETH Signal = policy_score * 0.4 + momentum_score * 0.4 - risk_score * 0.2
    """
    
    def calculate_policy_score(self, news_items: List[News]) -> float:
        """
        Score based on regulatory/policy keywords
        Keywords: clarity, staking, approved, regulation clear
        """
        keywords = ["clarity", "staking", "approved", "regulation clear", "sec"]
        score = 0
        for news in news_items:
            text = news.content.lower()
            for keyword in keywords:
                if keyword in text:
                    score += 0.25
        return min(score, 1.0)
    
    def calculate_momentum_score(self, eth_prices: List[float], 
                                  btc_prices: List[float]) -> float:
        """
        Score based on ETH/BTC ratio vs 7-day MA
        """
        eth_btc_current = eth_prices[-1] / btc_prices[-1]
        eth_btc_ma7 = sum(e/b for e,b in zip(eth_prices[-7:], btc_prices[-7:])) / 7
        
        return 1.0 if eth_btc_current > eth_btc_ma7 else 0.0
    
    def calculate_risk_score(self, oil_change: float, gold_change: float) -> float:
        """
        Score based on OIL and GOLD changes
        """
        score = 0
        if oil_change > 0.05:
            score += 0.6
        if gold_change > 0.02:
            score += 0.4
        return min(score, 1.0)
```

#### BTC Signal
```python
class BTCSignalEngine:
    """
    BTC Signal based on OIL risk + momentum
    """
    
    def calculate(self, oil_change: float, btc_momentum: float, 
                  regime: str) -> float:
        if regime == "RISK_ON":
            return 0.8 + btc_momentum * 0.2
        elif regime == "RISK_OFF":
            return 0.3 + btc_momentum * 0.2
        else:
            return 0.5 + btc_momentum * 0.3
```

#### GOLD Signal
```python
class GOLDSignalEngine:
    """
    GOLD Signal based on OIL movement
    """
    
    def calculate(self, oil_change: float, gold_momentum: float,
                  regime: str) -> float:
        if regime == "RISK_OFF":
            return 0.8 + gold_momentum * 0.2
        elif regime == "RISK_ON":
            return 0.2 + gold_momentum * 0.2
        else:
            return 0.4 + gold_momentum * 0.3
```

---

### 2.3 Risk Classifier

**Responsibility**: Determine market regime based on OIL and GOLD

```python
class RiskClassifier:
    """
    Classify market into RISK_ON, RISK_OFF, or NEUTRAL
    """
    
    def classify(self, oil_change: float, gold_change: float) -> Regime:
        """
        Rules:
        - RISK_OFF: OIL > +5% AND GOLD > 0%
        - RISK_ON: OIL < -3% AND GOLD <= 0%
        - NEUTRAL: Everything else
        """
        if oil_change > 0.05 and gold_change > 0:
            return Regime.RISK_OFF
        elif oil_change < -0.03 and gold_change <= 0:
            return Regime.RISK_ON
        else:
            return Regime.NEUTRAL
```

---

### 2.4 Allocation Engine

**Responsibility**: Calculate portfolio weights

```python
class AllocationEngine:
    """
    Calculate asset allocation based on signals and regime
    """
    
    def calculate_weights(self, eth_signal: float, btc_signal: float,
                         gold_signal: float, regime: Regime,
                         macro_state: str = "TIGHT") -> Dict[str, float]:
        """
        Base allocation:
        - Normalize signals to weights
        - Apply macro filter
        - Ensure minimum cash buffer
        """
        # Base weights from signals
        total = eth_signal + btc_signal + gold_signal
        
        if total == 0:
            return {"CASH": 1.0}
        
        weights = {
            "ETH": eth_signal / total,
            "BTC": btc_signal / total,
            "GOLD": gold_signal / total
        }
        
        # Apply macro filter
        if macro_state == "TIGHT":
            weights["ETH"] *= 0.7  # Reduce ETH in tight conditions
            weights["BTC"] *= 0.9
            weights["GOLD"] *= 1.1
        
        # Normalize again
        total = sum(weights.values())
        weights = {k: v/total * 0.7 for k, v in weights.items()}  # 30% cash
        weights["CASH"] = 0.3
        
        return weights
    
    def should_rebalance(self, current: Dict, target: Dict, threshold: float = 0.1) -> bool:
        """Check if rebalancing is needed"""
        for asset in target:
            if abs(target[asset] - current.get(asset, 0)) > threshold:
                return True
        return False
```

---

## 3. Database Schema

### Entity Relationship Diagram

```
┌──────────────┐       ┌──────────────┐       ┌──────────────┐
│   prices     │       │   signals    │       │ allocations  │
├──────────────┤       ├──────────────┤       ├──────────────┤
│ id (PK)      │       │ id (PK)      │       │ id (PK)      │
│ asset        │       │ asset        │       │ timestamp    │
│ price        │       │ signal_value │       │ eth_weight   │
│ timestamp    │       │ score        │       │ btc_weight   │
│ source       │       │ regime       │       │ gold_weight  │
│ change_24h   │       │ timestamp    │       │ cash_weight  │
│ change_7d    │       └──────────────┘       │ regime       │
└──────────────┘                              └──────────────┘
                                                        │
       ┌──────────────┐                                │
       │    news      │                                │
       ├──────────────┤                                │
       │ id (PK)      │                                │
       │ source       │                                │
       │ content      │                                │
       │ score        │                                │
       │ timestamp    │                                │
       └──────────────┘                                │
                                                      │
┌──────────────┐       ┌──────────────┐               │
│   alerts     │       │  historical  │◄──────────────┘
├──────────────┤       ├──────────────┤
│ id (PK)      │       │ id (PK)      │
│ asset        │       │ date         │
│ threshold    │       │ signal_avg   │
│ condition    │       │ price_avg    │
│ webhook_url  │       │ performance  │
│ active       │       │ regime       │
└──────────────┘       └──────────────┘
```

### Table Definitions

#### prices
```sql
CREATE TABLE prices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    asset VARCHAR(10) NOT NULL,  -- ETH, BTC, GOLD, OIL
    price DECIMAL(18, 8) NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    source VARCHAR(50) NOT NULL,  -- hyperliquid, coingecko
    change_24h DECIMAL(10, 4),
    change_7d DECIMAL(10, 4),
    volume_24h DECIMAL(20, 2),
    INDEX idx_asset_timestamp (asset, timestamp)
);
```

#### signals
```sql
CREATE TABLE signals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    asset VARCHAR(10) NOT NULL,  -- ETH, BTC, GOLD
    signal_value DECIMAL(3, 2) NOT NULL,  -- 0.0 to 1.0
    policy_score DECIMAL(3, 2),
    momentum_score DECIMAL(3, 2),
    risk_score DECIMAL(3, 2),
    regime VARCHAR(20) NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_asset_timestamp (asset, timestamp)
);
```

#### allocations
```sql
CREATE TABLE allocations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    eth_weight DECIMAL(4, 3) NOT NULL,
    btc_weight DECIMAL(4, 3) NOT NULL,
    gold_weight DECIMAL(4, 3) NOT NULL,
    cash_weight DECIMAL(4, 3) NOT NULL,
    regime VARCHAR(20) NOT NULL,
    macro_state VARCHAR(10),
    rebalance_triggered BOOLEAN DEFAULT FALSE
);
```

---

## 4. API Endpoints

### REST API Structure

```
/api/v1/
├── /prices
│   ├── GET /prices/current                    # Current prices for all assets
│   ├── GET /prices/{asset}                    # Price history for asset
│   └── GET /prices/{asset}/latest             # Latest price for asset
│
├── /signals
│   ├── GET /signals/current                   # Current signals for all assets
│   ├── GET /signals/{asset}                   # Signal history
│   └── GET /signals/{asset}/latest            # Latest signal
│
├── /regime
│   ├── GET /regime/current                    # Current market regime
│   └── GET /regime/history                    # Regime history
│
├── /allocation
│   ├── GET /allocation/current                # Current allocation
│   ├── GET /allocation/history                # Allocation history
│   └── POST /allocation/rebalance             # Trigger rebalance
│
└── /alerts
    ├── GET /alerts                            # List alerts
    ├── POST /alerts                           # Create alert
    ├── PUT /alerts/{id}                       # Update alert
    └── DELETE /alerts/{id}                    # Delete alert
```

---

## 5. Frontend Architecture

### Component Hierarchy

```
DashboardPage
├── Header
│   ├── Logo
│   ├── LastUpdated
│   └── SettingsButton
├── RegimeIndicator
│   ├── CurrentRegimeBadge
│   ├── OilChangeDisplay
│   └── RecommendationText
├── SignalCards
│   ├── ETHCard
│   │   ├── SignalScore
│   │   ├── TrendIndicator
│   │   └── ActionBadge
│   ├── BTCCard
│   └── GOLDCard
├── AllocationPanel
│   ├── WeightChart (Pie/Doughnut)
│   ├── WeightTable
│   └── RebalanceButton
├── PriceCharts
│   ├── MainChart (multi-asset)
│   └── TimeframeSelector
└── AlertPanel
    ├── AlertList
    └── CreateAlertButton

AssetDetailPage
├── Breadcrumb
├── AssetHeader
│   ├── Symbol
│   ├── CurrentPrice
│   └── Change24h
├── SignalSection
├── PriceChart (detailed)
├── MetricsGrid
│   ├── MomentumMetric
│   ├── VolatilityMetric
│   └── VolumeMetric
└── HistoryTable
```

### State Management

```typescript
// Zustand Store
interface DashboardState {
  // Data
  prices: Record<string, Price>;
  signals: Record<string, Signal>;
  allocation: Allocation;
  regime: Regime;
  
  // Loading states
  isLoading: boolean;
  lastUpdated: Date;
  
  // Actions
  fetchDashboard: () => Promise<void>;
  refreshPrices: () => Promise<void>;
  setAlert: (alert: AlertConfig) => void;
}
```

---

## 6. Background Jobs

### Scheduler Configuration

```python
# APScheduler jobs
JOBS = [
    {
        "id": "fetch_prices",
        "func": "services.data_fetcher:fetch_all_prices",
        "trigger": "interval",
        "minutes": 5,
        "max_instances": 1
    },
    {
        "id": "calculate_signals",
        "func": "services.signal_engine:calculate_all_signals",
        "trigger": "interval",
        "minutes": 5,
        "max_instances": 1
    },
    {
        "id": "update_allocation",
        "func": "services.allocation_engine:update_allocation",
        "trigger": "interval",
        "minutes": 5,
        "max_instances": 1
    },
    {
        "id": "cleanup_old_data",
        "func": "services.cleanup:cleanup_old_data",
        "trigger": "cron",
        "hour": 0,
        "minute": 0
    }
]
```

---

## 7. Security Considerations

1. **API Rate Limiting**: Prevent abuse of endpoints
2. **CORS**: Restrict to known frontend origins
3. **Input Validation**: Pydantic models for all inputs
4. **No Sensitive Data**: Don't store API keys in database
5. **HTTPS Only**: Enforce TLS in production

---

## 8. Error Handling Strategy

| Component | Error Type | Handling |
|-----------|-----------|----------|
| Data Fetcher | API timeout | Retry 3x, then use cached data |
| Data Fetcher | API error | Log error, keep last valid data |
| Signal Engine | Insufficient data | Return neutral signal (0.5) |
| Database | Connection error | Retry with backoff |
| API | Validation error | Return 400 with details |
| Frontend | API error | Show error toast, keep stale data |
