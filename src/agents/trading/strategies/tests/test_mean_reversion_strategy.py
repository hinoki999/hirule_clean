import pytest
from unittest.mock import AsyncMock
from src.agents.trading.strategies.mean_reversion_strategy import MeanReversionStrategy

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
        "lookback_period": 20,
        "entry_std": 2.0,
        "exit_std": 0.5
    }

@pytest.mark.asyncio
async def test_mean_reversion_signal_generation(strategy_config):
    strategy = MeanReversionStrategy(strategy_config)
    strategy.exchange = AsyncMock()
    strategy.message_bus = AsyncMock()
    
    # Simulate price series
    prices = [10000] * 19 + [11000]  # Significant deviation
    
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
    assert signal["side"] == "sell"
    assert signal["size"] == 1.0
