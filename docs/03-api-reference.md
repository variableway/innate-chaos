# HyperTrace - API Reference

## Base URL
```
Development: http://localhost:8000/api/v1
Production: https://api.hypertrace.io/api/v1
```

---

## Authentication
Currently, the API is open (no authentication required for dashboard use).

---

## Endpoints

### Prices

#### Get Current Prices
```http
GET /prices/current
```

Returns current prices for all tracked assets.

**Response:**
```json
{
  "success": true,
  "data": {
    "timestamp": "2026-03-30T12:00:00Z",
    "prices": [
      {
        "asset": "ETH",
        "price": 1850.50,
        "change_24h": 0.025,
        "change_7d": -0.035,
        "source": "hyperliquid"
      },
      {
        "asset": "BTC",
        "price": 68500.00,
        "change_24h": 0.015,
        "change_7d": 0.008,
        "source": "hyperliquid"
      },
      {
        "asset": "GOLD",
        "price": 2250.30,
        "change_24h": 0.008,
        "change_7d": 0.012,
        "source": "coingecko"
      },
      {
        "asset": "OIL",
        "price": 82.45,
        "change_24h": 0.055,
        "change_7d": 0.08,
        "source": "hyperliquid"
      }
    ]
  }
}
```

#### Get Price History
```http
GET /prices/{asset}?limit=100&from=2026-03-01&to=2026-03-30
```

**Parameters:**
- `asset` (path): Asset symbol (ETH, BTC, GOLD, OIL)
- `limit` (query): Number of records (default: 100, max: 1000)
- `from` (query): Start date (ISO format)
- `to` (query): End date (ISO format)

**Response:**
```json
{
  "success": true,
  "data": {
    "asset": "ETH",
    "prices": [
      {
        "timestamp": "2026-03-30T12:00:00Z",
        "price": 1850.50,
        "change_24h": 0.025
      }
    ]
  }
}
```

---

### Signals

#### Get Current Signals
```http
GET /signals/current
```

Returns current trading signals for all assets.

**Response:**
```json
{
  "success": true,
  "data": {
    "timestamp": "2026-03-30T12:00:00Z",
    "regime": "RISK_OFF",
    "signals": [
      {
        "asset": "ETH",
        "signal": 0.28,
        "score_breakdown": {
          "policy": 0.5,
          "momentum": 0.3,
          "risk": 0.85
        },
        "action": "AVOID",
        "action_text": "🔴 Avoid ETH"
      },
      {
        "asset": "BTC",
        "signal": 0.45,
        "score_breakdown": {
          "oil_factor": -0.2,
          "momentum": 0.65
        },
        "action": "NEUTRAL",
        "action_text": "🟡 Neutral - Reduce"
      },
      {
        "asset": "GOLD",
        "signal": 0.82,
        "score_breakdown": {
          "oil_factor": 0.6,
          "momentum": 0.55
        },
        "action": "STRONG",
        "action_text": "🟢 Strong - Accumulate"
      }
    ]
  }
}
```

#### Get Signal History
```http
GET /signals/{asset}?limit=168
```

**Parameters:**
- `asset` (path): Asset symbol (ETH, BTC, GOLD)
- `limit` (query): Number of records (default: 168 = 1 week of 1h data)

**Response:**
```json
{
  "success": true,
  "data": {
    "asset": "ETH",
    "signals": [
      {
        "timestamp": "2026-03-30T12:00:00Z",
        "signal": 0.28,
        "regime": "RISK_OFF"
      }
    ]
  }
}
```

---

### Regime

#### Get Current Regime
```http
GET /regime/current
```

**Response:**
```json
{
  "success": true,
  "data": {
    "timestamp": "2026-03-30T12:00:00Z",
    "regime": "RISK_OFF",
    "regime_text": "Risk-Off",
    "oil_change_24h": 0.055,
    "gold_change_24h": 0.012,
    "description": "OIL up >5% and GOLD positive - Risk escalation detected",
    "recommendation": "Increase GOLD position, reduce ETH exposure"
  }
}
```

#### Get Regime History
```http
GET /regime/history?days=30
```

**Parameters:**
- `days` (query): Number of days (default: 30)

**Response:**
```json
{
  "success": true,
  "data": {
    "history": [
      {
        "timestamp": "2026-03-30T12:00:00Z",
        "regime": "RISK_OFF",
        "oil_change": 0.055,
        "gold_change": 0.012
      }
    ],
    "statistics": {
      "risk_off_days": 12,
      "risk_on_days": 8,
      "neutral_days": 10
    }
  }
}
```

---

### Allocation

#### Get Current Allocation
```http
GET /allocation/current
```

**Response:**
```json
{
  "success": true,
  "data": {
    "timestamp": "2026-03-30T12:00:00Z",
    "regime": "RISK_OFF",
    "macro_state": "TIGHT",
    "weights": {
      "ETH": 0.15,
      "BTC": 0.20,
      "GOLD": 0.35,
      "CASH": 0.30
    },
    "rebalance_needed": true,
    "threshold_exceeded": ["ETH", "GOLD"],
    "rationale": "Oil up 5.5% triggers risk-off. Reducing ETH by 20%, increasing GOLD by 40%."
  }
}
```

#### Get Allocation History
```http
GET /allocation/history?limit=50
```

**Response:**
```json
{
  "success": true,
  "data": {
    "allocations": [
      {
        "timestamp": "2026-03-30T12:00:00Z",
        "weights": {
          "ETH": 0.15,
          "BTC": 0.20,
          "GOLD": 0.35,
          "CASH": 0.30
        },
        "regime": "RISK_OFF",
        "rebalance_triggered": true
      }
    ]
  }
}
```

#### Trigger Rebalance
```http
POST /allocation/rebalance
```

Manually trigger a rebalance calculation.

**Response:**
```json
{
  "success": true,
  "data": {
    "previous_weights": {
      "ETH": 0.35,
      "BTC": 0.35,
      "GOLD": 0.00,
      "CASH": 0.30
    },
    "new_weights": {
      "ETH": 0.15,
      "BTC": 0.20,
      "GOLD": 0.35,
      "CASH": 0.30
    },
    "changes": {
      "ETH": -0.20,
      "BTC": -0.15,
      "GOLD": 0.35,
      "CASH": 0.00
    },
    "regime": "RISK_OFF"
  }
}
```

---

### Dashboard

#### Get Full Dashboard Data
```http
GET /dashboard
```

Returns all data needed for the dashboard in a single request.

**Response:**
```json
{
  "success": true,
  "data": {
    "timestamp": "2026-03-30T12:00:00Z",
    "prices": { /* ... */ },
    "signals": { /* ... */ },
    "regime": { /* ... */ },
    "allocation": { /* ... */ },
    "chart_data": {
      "eth_btc_ratio": [ /* 30 days */ ],
      "oil_prices": [ /* 30 days */ ],
      "signal_history": { /* ... */ }
    }
  }
}
```

---

### Alerts

#### List Alerts
```http
GET /alerts
```

**Response:**
```json
{
  "success": true,
  "data": {
    "alerts": [
      {
        "id": 1,
        "asset": "ETH",
        "type": "signal_threshold",
        "condition": "above",
        "threshold": 0.7,
        "active": true,
        "webhook_url": "https://hooks.slack.com/..."
      }
    ]
  }
}
```

#### Create Alert
```http
POST /alerts
Content-Type: application/json

{
  "asset": "ETH",
  "type": "signal_threshold",
  "condition": "above",
  "threshold": 0.7,
  "webhook_url": "https://hooks.slack.com/..."
}
```

#### Update Alert
```http
PUT /alerts/{id}
Content-Type: application/json

{
  "threshold": 0.65,
  "active": true
}
```

#### Delete Alert
```http
DELETE /alerts/{id}
```

---

## WebSocket API (Future)

### Connect
```
ws://localhost:8000/ws
```

### Events

#### price_update
```json
{
  "type": "price_update",
  "data": {
    "asset": "ETH",
    "price": 1850.50,
    "timestamp": "2026-03-30T12:00:00Z"
  }
}
```

#### signal_update
```json
{
  "type": "signal_update",
  "data": {
    "asset": "ETH",
    "signal": 0.72,
    "action": "STRONG"
  }
}
```

#### regime_change
```json
{
  "type": "regime_change",
  "data": {
    "previous": "RISK_ON",
    "current": "RISK_OFF",
    "trigger": "oil_spike",
    "timestamp": "2026-03-30T12:00:00Z"
  }
}
```

---

## Error Responses

### Standard Error Format
```json
{
  "success": false,
  "error": {
    "code": "INVALID_ASSET",
    "message": "Asset 'XYZ' is not supported",
    "details": {
      "supported_assets": ["ETH", "BTC", "GOLD", "OIL"]
    }
  }
}
```

### Error Codes
| Code | HTTP Status | Description |
|------|-------------|-------------|
| `INVALID_ASSET` | 400 | Asset not supported |
| `INVALID_DATE_RANGE` | 400 | Invalid date range |
| `RATE_LIMITED` | 429 | Too many requests |
| `INTERNAL_ERROR` | 500 | Server error |
| `SERVICE_UNAVAILABLE` | 503 | External API unavailable |

---

## Rate Limits

| Endpoint | Limit |
|----------|-------|
| All endpoints | 100 requests/minute |
| Dashboard | 30 requests/minute |
| Rebalance | 5 requests/hour |
