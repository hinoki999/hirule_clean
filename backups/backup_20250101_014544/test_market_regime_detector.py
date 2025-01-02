import pytest
from unittest.mock import MagicMock, patch
import numpy as np
from src.communication.message_bus import MessageBus
from src.agents.capability import Capability
from src.agents.trading.capabilities.market_regime_detector import (
    MarketRegimeDetector,
    MARKET_REGIMES,
    MarketRegimeError,
    InvalidMarketDataError,
    MessageBusError,
    MarketData
)

@pytest.mark.asyncio
async def test_invalid_config():
    """Test invalid configuration handling"""
    invalid_configs = [
        # Missing required parameter
        {"volatility_window": 5, "volume_window": 5, "price_change_threshold": 0.02},
        # Invalid parameter type
        {"volatility_window": "5", "volume_window": 5, "price_change_threshold": 0.02, "volume_change_threshold": 0.5},
        # Invalid parameter value
        {"volatility_window": -5, "volume_window": 5, "price_change_threshold": 0.02, "volume_change_threshold": 0.5},
    ]
    
    for config in invalid_configs:
        with pytest.raises(MarketRegimeError):
            MarketRegimeDetector(config)

@pytest.mark.asyncio
async def test_invalid_market_data():
    """Test invalid market data handling"""
    config = {
        "volatility_window": 5,
        "volume_window": 5,
        "price_change_threshold": 0.02,
        "volume_change_threshold": 0.5
    }
    detector = MarketRegimeDetector(config)
    detector.message_bus = MagicMock(spec=MessageBus)
    await detector.setup()
    
    invalid_data = [
        # Missing fields
        {"symbol": "BTC/USDT", "last_price": "100"},
        # Invalid price
        {"symbol": "BTC/USDT", "last_price": "invalid", "volume": "1000", "timestamp": "2024-01-01T00:00:00Z"},
        # Negative volume
        {"symbol": "BTC/USDT", "last_price": "100", "volume": "-1000", "timestamp": "2024-01-01T00:00:00Z"},
    ]
    
    for data in invalid_data:
        with pytest.raises(InvalidMarketDataError):
            await detector._handle_market_data(data)

@pytest.mark.asyncio
async def test_regime_detection_trending():
    """Test trending market detection"""
    config = {
        "volatility_window": 5,
        "volume_window": 5,
        "price_change_threshold": 0.02,
        "volume_change_threshold": 0.5
    }
    detector = MarketRegimeDetector(config)
    detector.message_bus = MagicMock(spec=MessageBus)
    await detector.setup()
    
    # Simulate trending market
    prices = [100.0, 102.0, 104.0, 106.0, 108.0]
    for price in prices:
        await detector._handle_market_data({
            "symbol": "NLT/USDT",
            "last_price": str(price),
            "volume": "1000",
            "timestamp": "2024-01-01T00:00:00Z"
        })
    
    regime = detector._detect_regime("NLT/USDT")
    assert regime == MARKET_REGIMES["trending"]

@pytest.mark.asyncio
async def test_regime_detection_volatile():
    """Test volatile market detection"""
    config = {
        "volatility_window": 5,
        "volume_window": 5,
        "price_change_threshold": 0.02,
        "volume_change_threshold": 0.5
    }
    detector = MarketRegimeDetector(config)
    detector.message_bus = MagicMock(spec=MessageBus)
    await detector.setup()
    
    # Simulate volatile market
    prices = [100.0, 105.0, 95.0, 110.0, 90.0]
    for price in prices:
        await detector._handle_market_data({
            "symbol": "NLT/USDT",
            "last_price": str(price),
            "volume": "1000",
            "timestamp": "2024-01-01T00:00:00Z"
        })
    
    regime = detector._detect_regime("NLT/USDT")
    assert regime == MARKET_REGIMES["high_volatility"]

@pytest.mark.asyncio
async def test_message_bus_error_handling():
    """Test handling of message bus failures"""
    config = {
        "volatility_window": 5,
        "volume_window": 5,
        "price_change_threshold": 0.02,
        "volume_change_threshold": 0.5
    }
    detector = MarketRegimeDetector(config)
    
    # Mock message bus to simulate failure
    mock_bus = MagicMock(spec=MessageBus)
    mock_bus.publish.side_effect = Exception("Simulated message bus failure")
    detector.message_bus = mock_bus
    await detector.setup()
    
    # Attempt to process data with failing message bus
    with pytest.raises(MessageBusError) as exc_info:
        await detector._handle_market_data({
            "symbol": "NLT/USDT",
            "last_price": "100.0",
            "volume": "1000",
            "timestamp": "2024-01-01T00:00:00Z"
        })
    assert "Failed to publish regime update" in str(exc_info.value)

@pytest.mark.asyncio
async def test_multiple_symbols():
    """Test handling multiple symbols simultaneously"""
    config = {
        "volatility_window": 5,
        "volume_window": 5,
        "price_change_threshold": 0.02,
        "volume_change_threshold": 0.5
    }
    detector = MarketRegimeDetector(config)
    detector.message_bus = MagicMock(spec=MessageBus)
    await detector.setup()
    
    # Process data for multiple symbols
    symbols = ["BTC/USDT", "ETH/USDT"]
    for symbol in symbols:
        for price in [100.0, 102.0, 104.0, 106.0, 108.0]:
            await detector._handle_market_data({
                "symbol": symbol,
                "last_price": str(price),
                "volume": "1000",
                "timestamp": "2024-01-01T00:00:00Z"
            })
    
    # Verify each symbol has its own history
    for symbol in symbols:
        assert symbol in detector.price_history
        assert symbol in detector.volume_history
        assert len(detector.price_history[symbol]) == config["volatility_window"]
        regime = detector._detect_regime(symbol)
        assert regime == MARKET_REGIMES["trending"]
