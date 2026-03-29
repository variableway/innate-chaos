# HyperTrace Database Design

## Overview

We use **TimescaleDB** (PostgreSQL extension) for optimal time-series data storage and querying.

## Why TimescaleDB?

| Feature | Benefit |
|---------|---------|
| **Hypertables** | Automatic partitioning by time |
| **Compression** | 90%+ storage reduction |
| **Continuous Aggregates** | Pre-computed rollups |
| **Time-based Queries** | Optimized for range scans |
| **Retention Policies** | Automatic data lifecycle |

## Database Schema

### Hypertables (Time-Series Data)

#### prices
```sql
-- Create regular table first
CREATE TABLE prices (
    time TIMESTAMPTZ NOT NULL,
    asset TEXT NOT NULL,
    price DECIMAL(18, 8) NOT NULL,
    source TEXT NOT NULL,
    change_24h DECIMAL(10, 4),
    volume_24h DECIMAL(20, 2)
);

-- Convert to hypertable
SELECT create_hypertable('prices', 'time');

-- Create indexes
CREATE INDEX idx_prices_asset_time ON prices (asset, time DESC);

-- Enable compression
ALTER TABLE prices SET (
    timescaledb.compress,
    timescaledb.compress_segmentby = 'asset'
);

-- Compression policy: compress after 7 days
SELECT add_compression_policy('prices', INTERVAL '7 days');

-- Retention policy: drop after 90 days
SELECT add_retention_policy('prices', INTERVAL '90 days');
```

#### signals
```sql
CREATE TABLE signals (
    time TIMESTAMPTZ NOT NULL,
    asset TEXT NOT NULL,
    signal_value DECIMAL(3, 2) NOT NULL,
    policy_score DECIMAL(3, 2),
    momentum_score DECIMAL(3, 2),
    risk_score DECIMAL(3, 2),
    regime TEXT NOT NULL
);

SELECT create_hypertable('signals', 'time');
CREATE INDEX idx_signals_asset_time ON signals (asset, time DESC);
```

### Regular Tables

#### allocations
```sql
CREATE TABLE allocations (
    id SERIAL PRIMARY KEY,
    time TIMESTAMPTZ DEFAULT NOW(),
    eth_weight DECIMAL(4, 3) NOT NULL,
    btc_weight DECIMAL(4, 3) NOT NULL,
    gold_weight DECIMAL(4, 3) NOT NULL,
    cash_weight DECIMAL(4, 3) NOT NULL,
    regime TEXT NOT NULL,
    macro_state TEXT,
    rebalance_triggered BOOLEAN DEFAULT FALSE
);

CREATE INDEX idx_allocations_time ON allocations (time DESC);
```

#### news
```sql
CREATE TABLE news (
    id SERIAL PRIMARY KEY,
    time TIMESTAMPTZ DEFAULT NOW(),
    source TEXT NOT NULL,
    title TEXT,
    content TEXT NOT NULL,
    url TEXT,
    policy_score DECIMAL(3, 2) DEFAULT 0,
    sentiment DECIMAL(3, 2),
    category TEXT,
    keywords TEXT
);

CREATE INDEX idx_news_time ON news (time DESC);
CREATE INDEX idx_news_source ON news (source, time DESC);
```

## Continuous Aggregates

### Price Hourly Aggregates
```sql
CREATE MATERIALIZED VIEW prices_hourly
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('1 hour', time) AS bucket,
    asset,
    first(price, time) AS open,
    max(price) AS high,
    min(price) AS low,
    last(price, time) AS close,
    avg(price) AS avg_price
FROM prices
GROUP BY bucket, asset;

-- Refresh policy
SELECT add_continuous_aggregate_policy('prices_hourly',
    start_offset => INTERVAL '1 month',
    end_offset => INTERVAL '1 hour',
    schedule_interval => INTERVAL '1 hour'
);
```

### Daily Signal Averages
```sql
CREATE MATERIALIZED VIEW signals_daily
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('1 day', time) AS bucket,
    asset,
    avg(signal_value) AS avg_signal,
    max(signal_value) AS max_signal,
    min(signal_value) AS min_signal
FROM signals
GROUP BY bucket, asset;
```

## Python Models (SQLAlchemy)

### TimescaleDB Hypertable Model
```python
from sqlalchemy import Column, String, Float, DateTime
from sqlalchemy.dialects.postgresql import TIMESTAMP
from app.database import Base

class Price(Base):
    """Price model using TimescaleDB hypertable."""
    __tablename__ = "prices"
    
    time = Column(TIMESTAMP(timezone=True), primary_key=True)
    asset = Column(String(10), primary_key=True)
    price = Column(Float, nullable=False)
    source = Column(String(50), nullable=False)
    change_24h = Column(Float)
    volume_24h = Column(Float)
```

## Connection URL

```
# TimescaleDB Cloud
DATABASE_URL=postgresql://username:password@host.timescaledb.io:5432/hypertrace

# Self-hosted TimescaleDB
DATABASE_URL=postgresql://user:pass@localhost:5432/hypertrace

# Docker (timescale/timescaledb:latest-pg16)
DATABASE_URL=postgresql://user:pass@db:5432/hypertrace
```

## Docker Compose with TimescaleDB

```yaml
version: '3.8'

services:
  db:
    image: timescale/timescaledb:latest-pg16
    environment:
      POSTGRES_USER: hypertrace
      POSTGRES_PASSWORD: hypertrace_password
      POSTGRES_DB: hypertrace
    volumes:
      - timescale_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

volumes:
  timescale_data:
```

## Query Examples

### Last 24h Price Data
```sql
SELECT time, price
FROM prices
WHERE asset = 'ETH'
  AND time > NOW() - INTERVAL '24 hours'
ORDER BY time;
```

### Aggregate OHLC
```sql
SELECT
    time_bucket('1 hour', time) AS hour,
    first(price, time) AS open,
    max(price) AS high,
    min(price) AS low,
    last(price, time) AS close
FROM prices
WHERE asset = 'BTC'
  AND time > NOW() - INTERVAL '7 days'
GROUP BY hour
ORDER BY hour;
```

### Gap Filling (interpolate missing data)
```sql
SELECT
    time_bucket_gapfill('5 minutes', time) AS bucket,
    asset,
    locf(avg(price)) AS price  -- last observation carried forward
FROM prices
WHERE asset = 'ETH'
  AND time > NOW() - INTERVAL '1 hour'
GROUP BY bucket, asset;
```

## Migration Script

```python
# migrations/001_create_hypertables.py
from alembic import op

def upgrade():
    # Create hypertables
    op.execute("""
        SELECT create_hypertable('prices', 'time', if_not_exists => TRUE);
    """)
    op.execute("""
        SELECT create_hypertable('signals', 'time', if_not_exists => TRUE);
    """)
    
    # Enable compression
    op.execute("""
        ALTER TABLE prices SET (
            timescaledb.compress,
            timescaledb.compress_segmentby = 'asset'
        );
    """)
    
    # Add policies
    op.execute("""
        SELECT add_compression_policy('prices', INTERVAL '7 days');
    """)
    
    op.execute("""
        SELECT add_retention_policy('prices', INTERVAL '90 days');
    """)

def downgrade():
    pass
```

## Performance Tips

1. **Always use time-based filters** - Enables chunk exclusion
2. **Use segmentby for compression** - Better compression ratios
3. **Create continuous aggregates** - Faster queries for rollups
4. **Set appropriate chunk intervals** - Default 7 days, adjust based on data volume
