import pytest
import pytest_asyncio
from unittest.mock import MagicMock
import numpy as np
import time
from datetime import datetime

from src.communication.message_bus import MessageBus
from src.agents.capability import Capability
from src.agents.trading.capabilities.market_regime_detector import (
    MarketRegimeDetector,
    MarketRegimeError,
    InvalidMarketDataError,
    MessageBusError,
    MarketData,
    SymbolData,
    MARKET_REGIMES
)

@pytest.fixture
def base_config():
    return {
        "volatility_window": 5,
        "volume_window": 5,
        "price_change_threshold": 0.02,
        "volume_change_threshold": 0.5,
        "max_symbols": 100,
        "cleanup_interval": 0,
        "symbol_timeout": 3600
    }

@pytest.mark.asyncio
async def test_invalid_config():
    invalid_configs = [
        {"volatility_window": 5, "volume_window": 5, "price_change_threshold": 0.02},
        {"volatility_window": "5", "volume_window": 5, "price_change_threshold": 0.02, "volume_change_threshold": 0.5},
        {"volatility_window": -5, "volume_window": 5, "price_change_threshold": 0.02, "volume_change_threshold": 0.5},
    ]
    
    for config in invalid_configs:
        with pytest.raises(MarketRegimeError):
            MarketRegimeDetector(config)

@pytest.mark.asyncio
async def test_invalid_market_data(base_config):
    detector = MarketRegimeDetector(base_config)
    detector.message_bus = MagicMock(spec=MessageBus)
    await detector.setup()
    
    invalid_data = [
        {"symbol": "BTC/USDT", "last_price": "100"},
        {"symbol": "BTC/USDT", "last_price": "invalid", "volume": "1000", "timestamp": "2024-01-01T00:00:00Z"},
        {"symbol": "BTC/USDT", "last_price": "100", "volume": "-1000", "timestamp": "2024-01-01T00:00:00Z"},
    ]
    
    for data in invalid_data:
        with pytest.raises(InvalidMarketDataError):
            await detector._validate_market_data(data)

@pytest.mark.asyncio
async def test_memory_cleanup(base_config):
    config = base_config.copy()
    config.update({
        "max_symbols": 2,
        "cleanup_interval": 0,
        "symbol_timeout": 0
    })
    
    detector = MarketRegimeDetector(config)
    detector.message_bus = MagicMock(spec=MessageBus)
    await detector.setup()
    
    symbols = ["BTC/USDT", "ETH/USDT"]
    for symbol in symbols:
        await detector._update_history(symbol, 100.0, 1000.0)
    
    assert len(detector.symbols) == 2
    await detector._cleanup_old_data()
    assert len(detector.symbols) == 0

@pytest.mark.asyncio
async def test_regime_detection_trending(base_config):
    detector = MarketRegimeDetector(base_config)
    detector.message_bus = MagicMock(spec=MessageBus)
    await detector.setup()
    
    prices = [100.0, 102.0, 104.0, 106.0, 108.0]
    for price in prices:
        await detector._update_history("BTC/USDT", price, 1000.0)
    
    regime = detector._detect_regime("BTC/USDT")
    assert regime == MARKET_REGIMES["trending"]

@pytest.mark.asyncio
async def test_regime_detection_volatile(base_config):
    detector = MarketRegimeDetector(base_config)
    detector.message_bus = MagicMock(spec=MessageBus)
    await detector.setup()
    
    prices = [100.0, 110.0, 90.0, 115.0, 85.0]
    for price in prices:
        await detector._update_history("BTC/USDT", price, 1000.0)
    
    regime = detector._detect_regime("BTC/USDT")
    assert regime == MARKET_REGIMES["high_volatility"]
@pytest.mark.asyncio
async def test_memory_cleanup(base_config):
    config = base_config.copy()
    config.update({
        "max_symbols": 2,
        "cleanup_interval": 0,
        "symbol_timeout": 0
    })
    
    detector = MarketRegimeDetector(config)
    detector.message_bus = MagicMock(spec=MessageBus)
    await detector.setup()
    
    # Add symbols one by one and verify
    symbols = ["BTC/USDT", "ETH/USDT"]
    for symbol in symbols:
        await detector._update_history(symbol, 100.0, 1000.0)
        assert symbol in detector.symbols
        
    # Verify both symbols added
    assert len(detector.symbols) == 2
    
    # Force cleanup
    await detector._cleanup_old_data()
    assert len(detector.symbols) == 0
