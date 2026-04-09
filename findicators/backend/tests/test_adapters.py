"""Tests for HyperLiquid and FRED adapter response parsing."""

import pytest
from unittest.mock import AsyncMock, patch
from datetime import datetime, timezone


# --- HyperLiquid adapter mock data and tests ---

HYPERLIQUID_MID_PRICE_RESPONSE = [
    {"coin": "BTC", "midPx": "65000.5"},
    {"coin": "ETH", "midPx": "3500.25"},
]

HYPERLIQUID_CANDLE_RESPONSE = [
    {"t": 1712505600000, "o": "64000", "h": "66000", "l": "63500", "c": "65000", "v": "1234.5"},
    {"t": 1712592000000, "o": "65000", "h": "67000", "l": "64500", "c": "66500", "v": "2345.6"},
]


def parse_hyperliquid_mid_price(data: list[dict]) -> dict[str, float]:
    """Parse mid-price response from HyperLiquid."""
    result = {}
    for entry in data:
        coin = entry["coin"]
        price = float(entry["midPx"])
        result[coin] = price
    return result


def parse_hyperliquid_candles(data: list[dict]) -> list[dict]:
    """Parse candle response from HyperLiquid."""
    candles = []
    for entry in data:
        candles.append({
            "timestamp": datetime.fromtimestamp(entry["t"] / 1000, tz=timezone.utc),
            "open": float(entry["o"]),
            "high": float(entry["h"]),
            "low": float(entry["l"]),
            "close": float(entry["c"]),
            "volume": float(entry["v"]),
        })
    return candles


class TestHyperLiquidAdapter:
    """Tests for HyperLiquid response parsing."""

    def test_parse_mid_price_basic(self):
        result = parse_hyperliquid_mid_price(HYPERLIQUID_MID_PRICE_RESPONSE)
        assert "BTC" in result
        assert "ETH" in result
        assert result["BTC"] == 65000.5
        assert result["ETH"] == 3500.25

    def test_parse_mid_price_returns_float(self):
        result = parse_hyperliquid_mid_price(HYPERLIQUID_MID_PRICE_RESPONSE)
        for price in result.values():
            assert isinstance(price, float)

    def test_parse_mid_price_empty_response(self):
        result = parse_hyperliquid_mid_price([])
        assert result == {}

    def test_parse_mid_price_single_entry(self):
        data = [{"coin": "SOL", "midPx": "180.75"}]
        result = parse_hyperliquid_mid_price(data)
        assert result == {"SOL": 180.75}

    def test_parse_candles_basic(self):
        result = parse_hyperliquid_candles(HYPERLIQUID_CANDLE_RESPONSE)
        assert len(result) == 2

    def test_parse_candles_fields(self):
        result = parse_hyperliquid_candles(HYPERLIQUID_CANDLE_RESPONSE)
        candle = result[0]
        assert "timestamp" in candle
        assert "open" in candle
        assert "high" in candle
        assert "low" in candle
        assert "close" in candle
        assert "volume" in candle

    def test_parse_candles_values(self):
        result = parse_hyperliquid_candles(HYPERLIQUID_CANDLE_RESPONSE)
        candle = result[0]
        assert candle["open"] == 64000.0
        assert candle["high"] == 66000.0
        assert candle["low"] == 63500.0
        assert candle["close"] == 65000.0
        assert candle["volume"] == 1234.5

    def test_parse_candles_timestamp_is_datetime(self):
        result = parse_hyperliquid_candles(HYPERLIQUID_CANDLE_RESPONSE)
        assert isinstance(result[0]["timestamp"], datetime)

    def test_parse_candles_empty(self):
        result = parse_hyperliquid_candles([])
        assert result == []

    def test_parse_candles_all_floats(self):
        result = parse_hyperliquid_candles(HYPERLIQUID_CANDLE_RESPONSE)
        for candle in result:
            for key in ("open", "high", "low", "close", "volume"):
                assert isinstance(candle[key], float), f"{key} is not float"


# --- FRED adapter mock data and tests ---

FRED_SERIES_RESPONSE = {
    "observations": [
        {"date": "2024-01-01", "value": "5.50"},
        {"date": "2024-02-01", "value": "5.50"},
        {"date": "2024-03-01", "value": "5.33"},
    ]
}

FRED_SERIES_WITH_DOT = {
    "observations": [
        {"date": "2024-01-01", "value": "5.50"},
        {"date": "2024-02-01", "value": "."},
        {"date": "2024-03-01", "value": "5.33"},
    ]
}


def parse_fred_series(data: dict) -> list[dict]:
    """Parse FRED series observation response."""
    observations = data.get("observations", [])
    result = []
    for obs in observations:
        value_str = obs["value"]
        if value_str == ".":
            continue
        result.append({
            "date": obs["date"],
            "value": float(value_str),
        })
    return result


def get_latest_fred_value(data: dict) -> float | None:
    """Get the most recent value from a FRED series."""
    parsed = parse_fred_series(data)
    if not parsed:
        return None
    return parsed[-1]["value"]


class TestFREDAdapter:
    """Tests for FRED response parsing."""

    def test_parse_series_basic(self):
        result = parse_fred_series(FRED_SERIES_RESPONSE)
        assert len(result) == 3

    def test_parse_series_values(self):
        result = parse_fred_series(FRED_SERIES_RESPONSE)
        assert result[0]["date"] == "2024-01-01"
        assert result[0]["value"] == 5.50
        assert result[2]["value"] == 5.33

    def test_parse_series_skips_dot_values(self):
        result = parse_fred_series(FRED_SERIES_WITH_DOT)
        assert len(result) == 2
        assert result[0]["value"] == 5.50
        assert result[1]["value"] == 5.33

    def test_parse_series_empty_observations(self):
        result = parse_fred_series({"observations": []})
        assert result == []

    def test_parse_series_all_floats(self):
        result = parse_fred_series(FRED_SERIES_RESPONSE)
        for obs in result:
            assert isinstance(obs["value"], float)

    def test_get_latest_value(self):
        result = get_latest_fred_value(FRED_SERIES_RESPONSE)
        assert result == 5.33

    def test_get_latest_value_empty(self):
        result = get_latest_fred_value({"observations": []})
        assert result is None

    def test_get_latest_value_all_dots(self):
        data = {"observations": [
            {"date": "2024-01-01", "value": "."},
            {"date": "2024-02-01", "value": "."},
        ]}
        result = get_latest_fred_value(data)
        assert result is None
