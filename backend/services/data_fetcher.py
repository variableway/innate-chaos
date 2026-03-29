"""Data fetcher service for collecting price data using HyperLiquid SDK."""

import asyncio
import httpx
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from hyperliquid.info import Info
from app.config import settings
from models.price import Price

logger = logging.getLogger(__name__)


class DataFetcher:
    """Service for fetching data from external APIs using HyperLiquid SDK."""
    
    def __init__(self):
        # Initialize HyperLiquid SDK client
        self.hl_client = Info(base_url=settings.HYPERLIQUID_API_URL)
        self.cg_base_url = "https://api.coingecko.com/api/v3"
        self.http_client = httpx.AsyncClient(timeout=30.0)
    
    async def close(self):
        """Close HTTP client."""
        await self.http_client.aclose()
    
    async def fetch_all_prices(self) -> Dict[str, dict]:
        """Fetch all prices in parallel."""
        results = {}
        
        try:
            # Fetch from HyperLiquid using SDK (OIL, BTC, ETH)
            hl_prices = await self.fetch_hyperliquid_prices_sdk()
            results.update(hl_prices)
            
            # Fetch from CoinGecko (GOLD)
            gold_price = await self.fetch_gold_price()
            if gold_price:
                results["GOLD"] = gold_price
                
        except Exception as e:
            logger.error(f"Error fetching prices: {e}")
        
        return results
    
    async def fetch_hyperliquid_prices_sdk(self) -> Dict[str, dict]:
        """
        Fetch prices from HyperLiquid using the official SDK.
        
        Uses the allMids endpoint which returns mid prices for all assets.
        """
        try:
            # Use SDK to fetch all mid prices
            # This is a synchronous call in the SDK, run in thread pool
            loop = asyncio.get_event_loop()
            all_mids = await loop.run_in_executor(
                None, 
                self.hl_client.all_mids
            )
            
            prices = {}
            timestamp = datetime.utcnow()
            
            # Map HL symbols to our assets
            asset_mapping = {
                "ETH": "ETH",
                "BTC": "BTC",
                "OIL": "OIL"
            }
            
            for asset, hl_symbol in asset_mapping.items():
                if hl_symbol in all_mids:
                    try:
                        price_value = float(all_mids[hl_symbol])
                        
                        # Calculate 24h change if possible
                        change_24h = await self.calculate_24h_change_sdk(hl_symbol)
                        
                        price_data = {
                            "asset": asset,
                            "price": price_value,
                            "time": timestamp,  # 'time' for TimescaleDB
                            "source": "hyperliquid",
                            "change_24h": change_24h
                        }
                        prices[asset] = price_data
                        logger.debug(f"Fetched {asset} price: {price_value}")
                    except (ValueError, TypeError) as e:
                        logger.warning(f"Invalid price data for {asset}: {e}")
            
            logger.info(f"Fetched {len(prices)} prices from HyperLiquid SDK")
            return prices
            
        except Exception as e:
            logger.error(f"Error fetching HyperLiquid prices via SDK: {e}")
            return {}
    
    async def calculate_24h_change_sdk(self, coin: str) -> Optional[float]:
        """Calculate 24h price change using SDK candle data."""
        try:
            loop = asyncio.get_event_loop()
            
            # Get candles for the last 24 hours (using 1h candles)
            now_ms = int(datetime.utcnow().timestamp() * 1000)
            day_ago_ms = now_ms - (24 * 60 * 60 * 1000)
            
            candles = await loop.run_in_executor(
                None,
                lambda: self.hl_client.candles(
                    coin=coin,
                    interval="1h",
                    startTime=day_ago_ms,
                    endTime=now_ms
                )
            )
            
            if candles and len(candles) >= 2:
                # candles format: [[timestamp, open, high, low, close, volume], ...]
                first_close = float(candles[0][4])  # close price of first candle
                last_close = float(candles[-1][4])  # close price of last candle
                
                if first_close > 0:
                    return (last_close - first_close) / first_close
            
            return None
            
        except Exception as e:
            logger.debug(f"Could not calculate 24h change for {coin}: {e}")
            return None
    
    async def fetch_gold_price(self) -> Optional[dict]:
        """Fetch GOLD price from CoinGecko."""
        try:
            # Using Tether Gold (XAUT) as proxy for gold price
            params = {
                "ids": "tether-gold",
                "vs_currencies": "usd",
                "include_24hr_change": "true",
                "include_24hr_vol": "true"
            }
            
            headers = {}
            if settings.COINGECKO_API_KEY:
                headers["x-cg-demo-api-key"] = settings.COINGECKO_API_KEY
            
            response = await self.http_client.get(
                f"{self.cg_base_url}/simple/price",
                params=params,
                headers=headers
            )
            response.raise_for_status()
            data = response.json()
            
            if "tether-gold" in data:
                gold_data = data["tether-gold"]
                return {
                    "asset": "GOLD",
                    "price": float(gold_data["usd"]),
                    "time": datetime.utcnow(),  # 'time' for TimescaleDB
                    "source": "coingecko",
                    "change_24h": float(gold_data.get("usd_24h_change", 0)) / 100
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error fetching gold price: {e}")
            return None
    
    async def fetch_hl_candles_sdk(self, coin: str, interval: str = "5m",
                                    limit: int = 100) -> List[list]:
        """
        Fetch candle data from HyperLiquid using SDK.
        
        Args:
            coin: Asset symbol (ETH, BTC, OIL)
            interval: Candle interval (1m, 5m, 15m, 1h, 4h, 1d)
            limit: Number of candles to fetch
        
        Returns:
            List of candles: [[timestamp, open, high, low, close, volume], ...]
        """
        try:
            loop = asyncio.get_event_loop()
            
            now_ms = int(datetime.utcnow().timestamp() * 1000)
            # Estimate start time based on interval and limit
            interval_ms = {
                "1m": 60 * 1000,
                "5m": 5 * 60 * 1000,
                "15m": 15 * 60 * 1000,
                "1h": 60 * 60 * 1000,
                "4h": 4 * 60 * 60 * 1000,
                "1d": 24 * 60 * 60 * 1000
            }.get(interval, 5 * 60 * 1000)
            
            start_ms = now_ms - (interval_ms * limit)
            
            candles = await loop.run_in_executor(
                None,
                lambda: self.hl_client.candles(
                    coin=coin,
                    interval=interval,
                    startTime=start_ms,
                    endTime=now_ms
                )
            )
            
            return candles if candles else []
            
        except Exception as e:
            logger.error(f"Error fetching candles for {coin}: {e}")
            return []
    
    async def save_prices(self, db: AsyncSession, prices: Dict[str, dict]):
        """Save prices to TimescaleDB."""
        for asset, price_data in prices.items():
            try:
                price = Price(
                    asset=price_data["asset"],
                    price=price_data["price"],
                    time=price_data.get("time", datetime.utcnow()),  # Use 'time' for TimescaleDB
                    source=price_data.get("source", "unknown"),
                    change_24h=price_data.get("change_24h")
                )
                db.add(price)
            except Exception as e:
                logger.error(f"Error saving price for {asset}: {e}")
        
        await db.commit()
        logger.info(f"Saved {len(prices)} prices to TimescaleDB")
    
    async def get_price_changes(self, db: AsyncSession, asset: str, 
                                hours: int = 24) -> dict:
        """Calculate price changes over time using TimescaleDB."""
        from sqlalchemy import select, func
        
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        
        # Use TimescaleDB time_bucket for efficient aggregation
        query = select(Price).where(
            Price.asset == asset,
            Price.time >= cutoff
        ).order_by(Price.time)
        
        result = await db.execute(query)
        prices = result.scalars().all()
        
        if len(prices) < 2:
            return {"change": 0, "percent_change": 0}
        
        first_price = prices[0].price
        last_price = prices[-1].price
        
        change = last_price - first_price
        percent_change = change / first_price if first_price > 0 else 0
        
        return {
            "change": change,
            "percent_change": percent_change,
            "first_price": first_price,
            "last_price": last_price,
            "data_points": len(prices)
        }
