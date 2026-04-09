# Macro Index Dashboard - 架构设计

> 日期: 2026-04-08
> 状态: 初稿

---

## 一、系统架构总览

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (Next.js)                    │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────────┐ │
│  │ Price    │ │ Signal   │ │ Regime   │ │ Allocation │ │
│  │ Dashboard│ │ Cards    │ │ Indicator│ │ Panel      │ │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └─────┬──────┘ │
│       └─────────────┴───────────┴─────────────┘        │
│                         │ REST API                      │
└─────────────────────────┼───────────────────────────────┘
                          │
┌─────────────────────────┼───────────────────────────────┐
│                Backend (FastAPI)                         │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────────┐ │
│  │ Price    │ │ Signal   │ │ Risk     │ │ Allocation │ │
│  │ Service  │ │ Engine   │ │ Engine   │ │ Engine     │ │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └─────┬──────┘ │
│       │             │            │              │        │
│  ┌────┴─────────────┴────────────┴──────────────┴──────┐ │
│  │              Scheduler (APScheduler)                │ │
│  │     每5分钟: 加密货币  |  每日: 经济数据              │ │
│  └────┬────────────────────────────────────────────────┘ │
│       │                                                  │
│  ┌────┴─────────────────────────────────────────────┐   │
│  │            Data Source Adapters                   │   │
│  │  ┌──────────────┐  ┌──────────────────────────┐  │   │
│  │  │ HyperLiquid  │  │ FRED API                 │  │   │
│  │  │ Adapter      │  │ Adapter                  │  │   │
│  │  │ (BTC, ETH)   │  │ (GOLD, OIL, RATES)      │  │   │
│  │  └──────────────┘  └──────────────────────────┘  │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
                          │
┌─────────────────────────┼───────────────────────────────┐
│              TimescaleDB (PostgreSQL)                    │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────────┐│
│  │ prices       │ │ signals      │ │ regime_history   ││
│  │ (hypertable) │ │ (hypertable) │ │ (hypertable)     ││
│  └──────────────┘ └──────────────┘ └──────────────────┘│
└─────────────────────────────────────────────────────────┘
```

---

## 二、项目结构

```
macro-dashboard/
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI 入口
│   │   ├── config.py               # 配置管理
│   │   ├── database.py             # 数据库连接
│   │   ├── models/
│   │   │   ├── price.py            # 价格数据模型
│   │   │   ├── signal.py           # 信号数据模型
│   │   │   └── regime.py           # 市场状态模型
│   │   ├── schemas/
│   │   │   ├── price.py            # Pydantic schemas
│   │   │   ├── signal.py
│   │   │   └── regime.py
│   │   ├── services/
│   │   │   ├── price_service.py    # 价格聚合服务
│   │   │   ├── signal_engine.py    # 信号计算引擎
│   │   │   ├── risk_engine.py      # 风险评估引擎
│   │   │   └── allocation_engine.py # 资产配置引擎
│   │   ├── adapters/
│   │   │   ├── base.py             # 数据源适配器基类
│   │   │   ├── hyperliquid.py      # HyperLiquid 适配器
│   │   │   └── fred.py             # FRED API 适配器
│   │   ├── api/
│   │   │   ├── prices.py           # /api/v1/prices
│   │   │   ├── signals.py          # /api/v1/signals
│   │   │   ├── regime.py           # /api/v1/regime
│   │   │   └── allocation.py       # /api/v1/allocation
│   │   └── scheduler.py            # 定时任务
│   ├── requirements.txt
│   ├── Dockerfile
│   └── tests/
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── layout.tsx
│   │   │   ├── page.tsx            # 主 Dashboard 页
│   │   │   └── globals.css
│   │   ├── components/
│   │   │   ├── PriceTicker.tsx      # 实时价格条
│   │   │   ├── PriceChart.tsx       # 价格走势图
│   │   │   ├── RegimeIndicator.tsx  # RISK ON/OFF 指示器
│   │   │   ├── SignalPanel.tsx      # 信号面板
│   │   │   ├── AllocationPanel.tsx  # 配置建议面板
│   │   │   └── MacroSummary.tsx     # 宏观摘要
│   │   ├── lib/
│   │   │   ├── api.ts              # API 客户端
│   │   │   └── types.ts            # TypeScript 类型
│   │   └── hooks/
│   │       └── useMacroData.ts     # 数据获取 hook
│   ├── package.json
│   ├── tailwind.config.ts
│   └── Dockerfile
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## 三、数据模型设计

### 3.1 prices 表 (TimescaleDB Hypertable)

```sql
CREATE TABLE prices (
    time        TIMESTAMPTZ NOT NULL,
    asset       VARCHAR(10) NOT NULL,   -- GOLD, OIL, BTC, ETH, DFF, DGS10, etc.
    price       DECIMAL(18, 4) NOT NULL,
    source      VARCHAR(20) NOT NULL,   -- hyperliquid, fred
    change_24h  DECIMAL(10, 4),         -- 24小时变化
    volume_24h  DECIMAL(20, 4)          -- 24小时成交量(加密货币)
);

SELECT create_hypertable('prices', 'time');
```

### 3.2 signals 表

```sql
CREATE TABLE signals (
    time          TIMESTAMPTZ NOT NULL,
    asset         VARCHAR(10) NOT NULL,
    signal_value  DECIMAL(5, 4) NOT NULL,  -- 0.0 ~ 1.0
    score_breakdown JSONB,                  -- 各因子得分明细
    action        VARCHAR(20) NOT NULL      -- STRONG_BUY/BUY/HOLD/SELL/STRONG_SELL
);

SELECT create_hypertable('signals', 'time');
```

### 3.3 regime_history 表

```sql
CREATE TABLE regime_history (
    time         TIMESTAMPTZ NOT NULL,
    regime       VARCHAR(20) NOT NULL,     -- RISK_ON/NEUTRAL/RISK_OFF
    risk_score   DECIMAL(5, 4) NOT NULL,   -- 综合风险评分
    factor_scores JSONB,                    -- 各因子评分
    description  TEXT                       -- 判定依据描述
);

SELECT create_hypertable('regime_history', 'time');
```

---

## 四、API 设计

### 4.1 价格 API

```
GET /api/v1/prices/current
Response: {
  "timestamp": "2026-04-08T10:30:00Z",
  "assets": {
    "GOLD":  { "price": 2345.60, "change_24h": 0.35, "source": "fred" },
    "OIL":   { "price": 78.50,   "change_24h": -1.20, "source": "fred" },
    "BTC":   { "price": 82345.0, "change_24h": 2.15, "source": "hyperliquid" },
    "ETH":   { "price": 1920.25, "change_24h": 3.40, "source": "hyperliquid" },
    "DFF":   { "price": 4.33,    "source": "fred" },
    "DGS10": { "price": 4.25,    "source": "fred" },
    "T10Y2Y":{ "price": -0.35,   "source": "fred" }
  }
}

GET /api/v1/prices/{asset}/history?days=30
Response: {
  "asset": "BTC",
  "data": [
    { "time": "2026-04-08T00:00:00Z", "price": 82345.0, "volume": 1234567890 },
    ...
  ]
}
```

### 4.2 信号 API

```
GET /api/v1/signals/current
Response: {
  "timestamp": "2026-04-08T10:30:00Z",
  "signals": {
    "BTC": { "value": 0.75, "action": "BUY", "breakdown": { "momentum": 0.8, "risk": 0.7 } },
    "ETH": { "value": 0.70, "action": "BUY", "breakdown": { "momentum": 0.75, "risk": 0.65 } },
    "GOLD": { "value": 0.40, "action": "HOLD", "breakdown": { "momentum": 0.3, "risk": 0.5 } }
  }
}
```

### 4.3 市场状态 API

```
GET /api/v1/regime/current
Response: {
  "timestamp": "2026-04-08T10:30:00Z",
  "regime": "RISK_ON",
  "risk_score": 0.72,
  "factor_scores": {
    "oil_trend":     0.80,
    "gold_trend":    0.65,
    "btc_momentum":  0.85,
    "yield_curve":   0.60,
    "volatility":    0.70
  },
  "description": "原油稳定，BTC强势上涨，收益率曲线正常，市场风险偏好高",
  "suggestion": {
    "summary": "建议增持风险资产",
    "actions": [
      "增持 BTC、ETH 至组合 50-60%",
      "黄金维持 15-20% 底仓",
      "可适度使用杠杆"
    ]
  }
}
```

### 4.4 资产配置 API

```
GET /api/v1/allocation/current
Response: {
  "timestamp": "2026-04-08T10:30:00Z",
  "regime": "RISK_ON",
  "weights": {
    "BTC":  0.30,
    "ETH":  0.20,
    "GOLD": 0.20,
    "OIL":  0.10,
    "CASH": 0.20
  },
  "last_rebalance": "2026-04-07T00:00:00Z"
}
```

---

## 五、信号引擎设计

### 5.1 数据流

```
价格数据 → 趋势计算 → 因子评分 → 加权聚合 → Regime 判定 → 操作建议
```

### 5.2 因子计算

```python
class SignalEngine:
    def calculate_risk_score(self) -> RiskAssessment:
        # 1. 原油趋势因子 (7日变化率)
        oil_trend = self._calculate_trend("OIL", days=7)
        oil_score = self._normalize(oil_trend, threshold=3.0)  # ±3% 为阈值

        # 2. 黄金趋势因子 (7日变化率)
        gold_trend = self._calculate_trend("GOLD", days=7)
        gold_score = 1.0 - self._normalize(gold_trend, threshold=2.0)  # 金涨=风险低

        # 3. BTC 动量因子 (7日变化率)
        btc_momentum = self._calculate_trend("BTC", days=7)
        btc_score = self._normalize(btc_momentum, threshold=5.0)

        # 4. 收益率曲线因子
        spread = self._get_yield_spread()  # T10Y2Y
        curve_score = self._normalize(spread, threshold=0.5)

        # 5. 波动率因子
        volatility = self._calculate_volatility(["BTC", "ETH", "OIL"], days=20)
        vol_score = 1.0 - self._normalize(volatility, threshold=2.0)

        # 加权聚合
        risk_score = (
            0.20 * oil_score +
            0.25 * gold_score +
            0.25 * btc_score +
            0.20 * curve_score +
            0.10 * vol_score
        )

        # 判定 Regime
        regime = self._classify_regime(risk_score)
        return RiskAssessment(risk_score, regime, factor_scores, suggestion)
```

### 5.3 Regime 分类

```python
def _classify_regime(self, score: float) -> Regime:
    if score >= 0.6:
        return Regime.RISK_ON
    elif score <= 0.4:
        return Regime.RISK_OFF
    else:
        return Regime.NEUTRAL
```

---

## 六、前端组件设计

### 6.1 页面布局

```
┌────────────────────────────────────────────────────┐
│  Macro Index Dashboard           [RISK ON ● ]      │
├────────────────────────────────────────────────────┤
│  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐     │
│  │ GOLD   │ │ OIL    │ │ BTC    │ │ ETH    │     │
│  │ $2345  │ │ $78.5  │ │ $82345 │ │ $1920  │     │
│  │ +0.35% │ │ -1.20% │ │ +2.15% │ │ +3.40% │     │
│  └────────┘ └────────┘ └────────┘ └────────┘     │
├────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────────────┐ │
│  │  Interest Rates │  │  Risk Score Gauge       │ │
│  │  DFF: 4.33%     │  │       ╭─────╮           │ │
│  │  10Y: 4.25%     │  │      │ 0.72 │           │ │
│  │  2Y:  4.60%     │  │       ╰─────╯           │ │
│  │  Spread: -35bp  │  │    RISK ON              │ │
│  └─────────────────┘  └─────────────────────────┘ │
├────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────┐ │
│  │  Price Charts (Tab: GOLD | OIL | BTC | ETH)  │ │
│  │  ┌──────────────────────────────────────┐    │ │
│  │  │         📈 价格走势图 (30天)         │    │ │
│  │  └──────────────────────────────────────┘    │ │
│  └──────────────────────────────────────────────┘ │
├────────────────────────────────────────────────────┤
│  ┌──────────────────┐  ┌────────────────────────┐ │
│  │ Factor Breakdown │  │ Suggested Allocation   │ │
│  │ 🟢 Oil Trend: 80│  │ BTC  ████████ 30%      │ │
│  │ 🟢 BTC Mom:  85 │  │ ETH  ██████   20%      │ │
│  │ 🟡 Gold:     40 │  │ GOLD █████    20%      │ │
│  │ 🟢 Curve:   60 │  │ OIL  ███      10%      │ │
│  │ 🟢 Vol:     70 │  │ CASH ███      20%      │ │
│  └──────────────────┘  └────────────────────────┘ │
├────────────────────────────────────────────────────┤
│  操作建议:                                         │
│  • 增持 BTC、ETH 至组合 50-60%                      │
│  • 黄金维持 15-20% 底仓                             │
│  • 收益率曲线正常，风险偏好可适度提升                  │
└────────────────────────────────────────────────────┘
```

### 6.2 组件清单

| 组件 | 功能 | 刷新频率 |
|------|------|----------|
| PriceTicker | 实时价格卡片 (GOLD/OIL/BTC/ETH) | 30秒 |
| RatePanel | 利率面板 (DFF/10Y/2Y/Spread) | 5分钟 |
| RegimeIndicator | RISK ON/OFF 状态指示器 | 5分钟 |
| RiskScoreGauge | 风险评分仪表盘 (0-1) | 5分钟 |
| PriceChart | 价格历史走势 (Recharts) | 手动 |
| FactorBreakdown | 因子评分明细 | 5分钟 |
| AllocationPanel | 建议资产配置比例 | 5分钟 |
| SuggestionPanel | 操作建议文字面板 | 5分钟 |

---

## 七、技术栈

| 层 | 技术 | 版本 |
|---|------|------|
| Backend | FastAPI | 0.109+ |
| ORM | SQLAlchemy (async) | 2.0+ |
| Database | TimescaleDB | Latest |
| Scheduler | APScheduler | 3.10+ |
| HTTP Client | httpx | 0.27+ |
| Frontend | Next.js | 14+ |
| UI | React + Tailwind CSS | 18 + 3.3 |
| Charts | Recharts | 2.10+ |
| State | Zustand | 4.0+ |
| Data Fetching | TanStack Query | 5.0+ |
| Deploy | Docker Compose | Latest |

---

## 八、配置管理

```yaml
# .env.example
# HyperLiquid
HYPERLIQUID_API_URL=https://api.hyperliquid.xyz

# FRED
FRED_API_KEY=your_fred_api_key_here

# Database
DATABASE_URL=postgresql+asyncpg://postgres:password@timescaledb:5432/macro_dashboard

# Scheduler
CRYPTO_FETCH_INTERVAL=300       # 5分钟
ECONOMIC_FETCH_INTERVAL=86400   # 24小时

# Signal Engine
OIL_TREND_DAYS=7
GOLD_TREND_DAYS=7
BTC_MOMENTUM_DAYS=7
VOLATILITY_WINDOW=20
RISK_ON_THRESHOLD=0.6
RISK_OFF_THRESHOLD=0.4
```
