# HyperLiquid SDK Usage Guide

This project uses the official [HyperLiquid Python SDK](https://github.com/hyperliquid-dex/hyperliquid-python-sdk) for all HyperLiquid API interactions.

## Installation

```bash
pip install hyperliquid-python-sdk
```

## SDK Client Initialization

```python
from hyperliquid.info import Info
from hyperliquid.exchange import Exchange
from hyperliquid.utils import constants

# Initialize read-only client (no wallet needed for public data)
info = Info(base_url="https://api.hyperliquid.xyz")

# Initialize exchange client (requires wallet for trading)
# exchange = Exchange(wallet, base_url="https://api.hyperliquid.xyz")
```

## SDK Methods Used

### 1. Get All Mid Prices
```python
# Get mid prices for all assets
all_mids = info.all_mids()
# Returns: {'ETH': '1850.5', 'BTC': '68500.0', 'OIL': '82.45', ...}

eth_price = float(all_mids['ETH'])
```

### 2. Get Candle Data
```python
# Get historical candles
candles = info.candles(
    coin="ETH",
    interval="1h",  # "1m", "5m", "15m", "1h", "4h", "1d"
    startTime=1711800000000,  # milliseconds
    endTime=1711886400000
)
# Returns: [[timestamp, open, high, low, close, volume], ...]
```

### 3. Get Market Metadata
```python
# Get market metadata
meta = info.meta()
# Returns: {'universe': [{'name': 'ETH', 'maxLeverage': 50, ...}, ...]}
```

### 4. Get Order Book
```python
# Get L2 order book
l2_book = info.l2_snapshot(coin="ETH")
# Returns: {'coin': 'ETH', 'levels': [[{'px': '...', 'sz': '...'}, ...], ...]}
```

### 5. Get Recent Trades
```python
# Get recent trades
trades = info.recent_trades(coin="ETH")
```

## Async Usage

Since the SDK is synchronous, we run it in an executor:

```python
import asyncio

async def fetch_prices_async():
    loop = asyncio.get_event_loop()
    
    # Run synchronous SDK call in thread pool
    all_mids = await loop.run_in_executor(None, info.all_mids)
    
    return all_mids
```

## Error Handling

```python
from hyperliquid.utils.errors import HyperliquidError

try:
    candles = info.candles(coin="ETH", interval="1h", startTime=..., endTime=...)
except HyperliquidError as e:
    logger.error(f"HyperLiquid API error: {e}")
except Exception as e:
    logger.error(f"Unexpected error: {e}")
```

## Rate Limiting

The SDK handles rate limiting internally. For high-frequency requests, implement backoff:

```python
import asyncio
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
async def fetch_with_retry(coin):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, info.all_mids)
```

## Benefits of Using SDK vs Raw HTTP

1. **Type Safety**: SDK provides typed responses
2. **Error Handling**: Built-in error types and handling
3. **Updates**: Automatic updates when API changes
4. **Validation**: Input/output validation
5. **Documentation**: Inline documentation and examples

## References

- [SDK GitHub](https://github.com/hyperliquid-dex/hyperliquid-python-sdk)
- [HyperLiquid Docs](https://hyperliquid.gitbook.io/hyperliquid-docs)
- [API Reference](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api)
