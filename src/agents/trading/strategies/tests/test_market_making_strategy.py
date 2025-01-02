import pytest
from unittest.mock import AsyncMock
from src.agents.trading.strategies.market_making_strategy import MarketMakingStrategy

@pytest.fixture
def strategy_config():
    return {
        "exchange": "binance",
        "api_key": "test",
        "api_secret": "test",
        "symbols": ["BTC/USDT"],
        "position_limits": {"BTC/USDT": {"max_position": 1.0}},
        "spread": 0.002,
        "order_size": 0.1
    }

@pytest.mark.asyncio
async def test_market_making_signal_generation(strategy_config):
    strategy = MarketMakingStrategy(strategy_config)
    strategy.exchange = AsyncMock()
    strategy.message_bus = AsyncMock()
    
    market_data = {
        "symbol": "BTC/USDT",
        "bids": [[39900, 1.0], [39890, 2.0]],
        "asks": [[40100, 1.0], [40110, 2.0]]
    }
    
    signal = await strategy._generate_signal(market_data)
    
    assert signal is not None
    assert len(signal["orders"]) == 2
    assert signal["orders"][0]["side"] == "buy"
    assert signal["orders"][1]["side"] == "sell"
