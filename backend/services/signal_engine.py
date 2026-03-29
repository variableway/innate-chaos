"""Signal engine for calculating trading signals."""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from app.config import settings
from models.price import Price
from models.signal import Signal
from models.news import News

logger = logging.getLogger(__name__)


class ETHSignalEngine:
    """ETH signal calculation engine."""
    
    def __init__(self):
        self.keywords = [
            "clarity", "staking", "approved", "regulation clear", 
            "sec", "etf", "institutional", "adoption"
        ]
    
    def calculate_policy_score(self, news_items: List[News]) -> float:
        """
        Calculate policy score based on news keywords.
        Score: 0.0 to 1.0
        """
        if not news_items:
            return 0.5  # Neutral when no news
        
        score = 0
        for news in news_items:
            text = (news.content + " " + (news.title or "")).lower()
            for keyword in self.keywords:
                if keyword in text:
                    score += 0.25
        
        return min(score, 1.0)
    
    def calculate_momentum_score(self, eth_prices: List[Price], 
                                  btc_prices: List[Price]) -> float:
        """
        Calculate momentum score based on ETH/BTC ratio vs 7-period MA.
        Score: 0.0 or 1.0 (can be enhanced for gradient)
        """
        if len(eth_prices) < 7 or len(btc_prices) < 7:
            return 0.5  # Neutral when insufficient data
        
        # Get latest prices
        eth_current = eth_prices[-1].price
        btc_current = btc_prices[-1].price
        
        # Calculate ETH/BTC ratio
        eth_btc_current = eth_current / btc_current if btc_current > 0 else 0
        
        # Calculate 7-period MA of ETH/BTC ratio
        eth_btc_ratios = []
        for i in range(min(7, len(eth_prices), len(btc_prices))):
            idx = -1 - i
            if abs(idx) <= len(eth_prices) and abs(idx) <= len(btc_prices):
                e = eth_prices[idx].price
                b = btc_prices[idx].price
                if b > 0:
                    eth_btc_ratios.append(e / b)
        
        if not eth_btc_ratios:
            return 0.5
        
        eth_btc_ma7 = sum(eth_btc_ratios) / len(eth_btc_ratios)
        
        # Score: 1.0 if current > MA, 0.0 otherwise
        return 1.0 if eth_btc_current > eth_btc_ma7 else 0.0
    
    def calculate_risk_score(self, oil_change: float, gold_change: float) -> float:
        """
        Calculate risk score based on OIL and GOLD changes.
        Score: 0.0 to 1.0 (higher = more risk)
        """
        score = 0
        
        # OIL > 5% = significant risk
        if oil_change > 0.05:
            score += 0.6
        elif oil_change > 0.03:
            score += 0.3
        
        # GOLD > 2% = risk off
        if gold_change > 0.02:
            score += 0.4
        elif gold_change > 0.01:
            score += 0.2
        
        return min(score, 1.0)
    
    def calculate(self, eth_prices: List[Price], btc_prices: List[Price],
                  oil_change: float, gold_change: float,
                  news_items: List[News]) -> float:
        """
        Calculate ETH signal.
        Formula: policy * 0.4 + momentum * 0.4 - risk * 0.2
        """
        policy = self.calculate_policy_score(news_items)
        momentum = self.calculate_momentum_score(eth_prices, btc_prices)
        risk = self.calculate_risk_score(oil_change, gold_change)
        
        signal = policy * 0.4 + momentum * 0.4 - risk * 0.2
        
        # Clamp to 0-1 range
        return max(0.0, min(1.0, signal))


class BTCSignalEngine:
    """BTC signal calculation engine."""
    
    def calculate_momentum(self, btc_prices: List[Price]) -> float:
        """Calculate BTC momentum score."""
        if len(btc_prices) < 7:
            return 0.5
        
        current = btc_prices[-1].price
        
        # 7-period MA
        ma7_prices = [p.price for p in btc_prices[-7:]]
        ma7 = sum(ma7_prices) / len(ma7_prices)
        
        if current > ma7:
            return min(1.0, (current - ma7) / ma7 + 0.5)
        else:
            return max(0.0, 0.5 - (ma7 - current) / ma7)
    
    def calculate(self, btc_prices: List[Price], oil_change: float,
                  regime: str) -> float:
        """
        Calculate BTC signal.
        Based on momentum and regime.
        """
        momentum = self.calculate_momentum(btc_prices)
        
        if regime == "RISK_ON":
            base = 0.8
        elif regime == "RISK_OFF":
            base = 0.3
        else:
            base = 0.5
        
        # Adjust by momentum
        signal = base * 0.7 + momentum * 0.3
        
        return max(0.0, min(1.0, signal))


class GOLDSignalEngine:
    """GOLD signal calculation engine."""
    
    def calculate_momentum(self, gold_prices: List[Price]) -> float:
        """Calculate GOLD momentum score."""
        if len(gold_prices) < 7:
            return 0.5
        
        current = gold_prices[-1].price
        
        # 7-period MA
        ma7_prices = [p.price for p in gold_prices[-7:]]
        ma7 = sum(ma7_prices) / len(ma7_prices)
        
        if current > ma7:
            return min(1.0, (current - ma7) / ma7 + 0.5)
        else:
            return max(0.0, 0.5 - (ma7 - current) / ma7)
    
    def calculate(self, gold_prices: List[Price], oil_change: float,
                  regime: str) -> float:
        """
        Calculate GOLD signal.
        Based on OIL and regime.
        """
        momentum = self.calculate_momentum(gold_prices)
        
        if regime == "RISK_OFF":
            base = 0.8
        elif regime == "RISK_ON":
            base = 0.2
        else:
            base = 0.5
        
        # Adjust by momentum
        signal = base * 0.7 + momentum * 0.3
        
        return max(0.0, min(1.0, signal))


class SignalEngine:
    """Main signal engine coordinating all asset signals."""
    
    def __init__(self):
        self.eth_engine = ETHSignalEngine()
        self.btc_engine = BTCSignalEngine()
        self.gold_engine = GOLDSignalEngine()
    
    async def fetch_price_history(self, db: AsyncSession, asset: str,
                                   hours: int = 168) -> List[Price]:
        """Fetch price history for an asset from TimescaleDB."""
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        
        query = select(Price).where(
            Price.asset == asset,
            Price.time >= cutoff
        ).order_by(Price.time)
        
        result = await db.execute(query)
        return result.scalars().all()
    
    async def fetch_recent_news(self, db: AsyncSession, 
                                 hours: int = 24) -> List[News]:
        """Fetch recent news for policy scoring."""
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        
        query = select(News).where(
            News.created_at >= cutoff
        ).order_by(desc(News.created_at))
        
        result = await db.execute(query)
        return result.scalars().all()
    
    async def calculate_all_signals(self, db: AsyncSession, regime: str,
                                     oil_change: float, gold_change: float) -> Dict[str, Signal]:
        """
        Calculate all asset signals.
        
        Returns dict of asset -> Signal
        """
        # Fetch price histories
        eth_prices = await self.fetch_price_history(db, "ETH")
        btc_prices = await self.fetch_price_history(db, "BTC")
        gold_prices = await self.fetch_price_history(db, "GOLD")
        
        # Fetch news for ETH policy scoring
        news_items = await self.fetch_recent_news(db)
        
        signals = {}
        now = datetime.utcnow()
        
        # ETH Signal
        if eth_prices and btc_prices:
            eth_value = self.eth_engine.calculate(
                eth_prices, btc_prices, oil_change, gold_change, news_items
            )
            signals["ETH"] = Signal(
                asset="ETH",
                signal_value=eth_value,
                policy_score=self.eth_engine.calculate_policy_score(news_items),
                momentum_score=self.eth_engine.calculate_momentum_score(eth_prices, btc_prices),
                risk_score=self.eth_engine.calculate_risk_score(oil_change, gold_change),
                regime=regime,
                time=now
            )
        
        # BTC Signal
        if btc_prices:
            btc_value = self.btc_engine.calculate(btc_prices, oil_change, regime)
            signals["BTC"] = Signal(
                asset="BTC",
                signal_value=btc_value,
                momentum_score=self.btc_engine.calculate_momentum(btc_prices),
                regime=regime,
                time=now
            )
        
        # GOLD Signal
        if gold_prices:
            gold_value = self.gold_engine.calculate(gold_prices, oil_change, regime)
            signals["GOLD"] = Signal(
                asset="GOLD",
                signal_value=gold_value,
                momentum_score=self.gold_engine.calculate_momentum(gold_prices),
                regime=regime,
                time=now
            )
        
        return signals
    
    async def save_signals(self, db: AsyncSession, signals: Dict[str, Signal]):
        """Save signals to TimescaleDB."""
        for signal in signals.values():
            db.add(signal)
        
        await db.commit()
        logger.info(f"Saved {len(signals)} signals to TimescaleDB")
