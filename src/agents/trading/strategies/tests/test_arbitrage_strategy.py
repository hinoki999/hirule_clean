import pytest
from unittest.mock import AsyncMock
from src.agents.trading.strategies.arbitrage_strategy import ArbitrageStrategy

@pytest.fixture
def strategy_config():
    return {
        "exchange": "binance",
        "api_key": "test",
        "api_secret": "test",
        "symbols": ["BTC/USDT"],
        "min_spread": 0.001,
        "exchanges": [
            {
                "id": "binance",
                "api_key": "test1",
                "api_secret": "test1"
            },
            {
                "id": "kraken",
                "api_key": "test2",
                "api_secret": "test2"
            }
        ],
        "max_position_value": 100000
    }

@pytest.mark.asyncio
async def test_arbitrage_signal_generation(strategy_config):
    strategy = ArbitrageStrategy(strategy_config)
    
    # Mock exchanges
    strategy.exchanges = {
        "binance": AsyncMock(),
        "kraken": AsyncMock()
    }
    
    # Setup mock orderbook responses
    strategy.exchanges["binance"].fetch_order_book = AsyncMock(return_value={
        "bids": [[39900, 1.0], [39890, 2.0]],
        "asks": [[40000, 1.0], [40010, 2.0]]
    })
    
    strategy.exchanges["kraken"].fetch_order_book = AsyncMock(return_value={
        "bids": [[40100, 1.0], [40090, 2.0]],
        "asks": [[40200, 1.0], [40210, 2.0]]
    })
    
    market_data = {
        "symbol": "BTC/USDT",
        "timestamp": "2024-01-01T00:00:00Z"
    }
    
    signal = await strategy._generate_signal(market_data)
    
    assert signal is not None
    assert signal["type"] == "arbitrage"
    assert signal["buy_exchange"] == "binance"
    assert signal["sell_exchange"] == "kraken"
    assert signal["buy_price"] == 40000
    assert signal["sell_price"] == 40100
