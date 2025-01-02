import pytest
from unittest.mock import AsyncMock
import numpy as np
from src.agents.trading.strategies.trend_following_strategy import TrendFollowingStrategy

@pytest.fixture
def strategy_config():
    return {
        "exchange": "binance",
        "api_key": "test",
        "api_secret": "test",
        "symbols": ["BTC/USDT"],
        "position_limits": {
            "BTC/USDT": {"max_position": 1.0}
        },
        "short_period": 10,
        "long_period": 20
    }

@pytest.mark.asyncio
async def test_trend_following_signal_generation(strategy_config):
    strategy = TrendFollowingStrategy(strategy_config)
    strategy.exchange = AsyncMock()
    strategy.message_bus = AsyncMock()
    
    # Generate uptrending prices
    prices = list(np.linspace(10000, 11000, 20))
    
    for price in prices[:-1]:
        await strategy._generate_signal({
            "symbol": "BTC/USDT",
            "last_price": price
        })
    
    signal = await strategy._generate_signal({
        "symbol": "BTC/USDT",
        "last_price": prices[-1]
    })
    
    assert signal is not None
    assert signal["side"] == "buy"
    assert signal["size"] == 1.0
