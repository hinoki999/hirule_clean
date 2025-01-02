import pytest
from unittest.mock import MagicMock, AsyncMock
from src.agents.trading.strategies.base_trading_strategy import BaseTradingStrategy, TradingStrategyError

@pytest.fixture
def base_config():
    return {
        "exchange": "binance",
        "api_key": "test_key",
        "api_secret": "test_secret",
        "symbols": ["BTC/USDT", "ETH/USDT"],
        "position_limits": {
            "BTC/USDT": {"max_position": 1.0},
            "ETH/USDT": {"max_position": 10.0}
        }
    }

@pytest.mark.asyncio
async def test_initialization(base_config):
    strategy = BaseTradingStrategy(base_config)
    assert strategy.symbols == ["BTC/USDT", "ETH/USDT"]
    assert strategy.position_limits == base_config["position_limits"]

@pytest.mark.asyncio
async def test_invalid_config():
    with pytest.raises(TradingStrategyError):
        BaseTradingStrategy({})

@pytest.mark.asyncio
async def test_setup(base_config):
    strategy = BaseTradingStrategy(base_config)
    strategy.message_bus = AsyncMock()
    strategy.exchange.fetch_positions = AsyncMock(return_value=[])
    strategy.exchange.fetch_open_orders = AsyncMock(return_value=[])
    await strategy.setup()
    strategy.message_bus.subscribe.assert_called()
