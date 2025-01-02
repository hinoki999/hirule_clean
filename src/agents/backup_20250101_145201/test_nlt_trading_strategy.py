import pytest
import logging
from unittest.mock import AsyncMock, MagicMock, patch
from src.agents.trading.strategies.nlt_trading_strategy import NLTTradingStrategy

# Configure logging for tests
logging.basicConfig(level=logging.DEBUG)

@pytest.fixture
def strategy_config():
    return {
        "treasury_address": "0x742d35Cc6634C0532925a3b844Bc454e4438f44e",
        "min_profit": 0.002,
        "max_slippage": 0.003,
        "treasury_threshold": 1000000,
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
        ]
    }

@pytest.fixture
def market_data():
    return {
        "symbol": "NLT/USDT",
        "timestamp": "2024-01-01T00:00:00Z",
        "exchanges": {
            "binance": {"bid": 1.0, "ask": 1.01},
            "kraken": {"bid": 1.02, "ask": 1.03}
        }
    }

@pytest.mark.asyncio
async def test_conservative_mode(strategy_config, market_data):
    with patch("src.agents.trading.strategies.nlt_trading_strategy.MarketMakingStrategy") as MockMarketMaker, \
         patch("src.agents.trading.strategies.nlt_trading_strategy.ArbitrageStrategy") as MockArbitrage:
        
        mock_market_maker = AsyncMock()
        mock_arbitrage = AsyncMock()
        MockMarketMaker.return_value = mock_market_maker
        MockArbitrage.return_value = mock_arbitrage
        
        strategy = NLTTradingStrategy(strategy_config)
        strategy.message_bus = AsyncMock()
        strategy.message_bus.request.return_value = {"balance": 500000}
        
        mock_arbitrage._generate_signal.return_value = {
            "expected_profit": 0.005,  # 0.5% profit, exceeds 2x min_profit (0.004)
            "buy_exchange": "binance",
            "sell_exchange": "kraken",
            "size": 1000
        }
        
        mock_market_maker._generate_signal.return_value = {
            "side": "buy",
            "confidence": 0.9,
            "price": 1.01,
            "size": 1000
        }
        
        signal = await strategy._generate_signal(market_data)
        assert signal is not None, "Signal should not be None"
        assert signal["type"] == "arbitrage", f"Expected arbitrage signal but got {signal['type']}"
        assert signal["priority"] == "high"
        assert "data" in signal
        assert signal["data"]["expected_profit"] == 0.005

@pytest.mark.asyncio
async def test_normal_mode(strategy_config, market_data):
    with patch("src.agents.trading.strategies.nlt_trading_strategy.MarketMakingStrategy") as MockMarketMaker, \
         patch("src.agents.trading.strategies.nlt_trading_strategy.ArbitrageStrategy") as MockArbitrage:
        
        mock_market_maker = AsyncMock()
        mock_arbitrage = AsyncMock()
        MockMarketMaker.return_value = mock_market_maker
        MockArbitrage.return_value = mock_arbitrage
        
        strategy = NLTTradingStrategy(strategy_config)
        strategy.message_bus = AsyncMock()
        strategy.message_bus.request.return_value = {"balance": 1500000}
        
        mock_market_maker._generate_signal.return_value = {
            "side": "sell",
            "confidence": 0.7,
            "price": 1.015,
            "size": 1000
        }
        
        mock_arbitrage._generate_signal.return_value = None
        
        signal = await strategy._generate_signal(market_data)
        assert signal is not None
        assert signal["type"] == "market_making"
        assert signal["priority"] == "low"
        assert signal["data"]["confidence"] > 0.6

@pytest.mark.asyncio
async def test_conservative_mode_no_arbitrage(strategy_config, market_data):
    """Test conservative mode when arbitrage profit is below threshold"""
    with patch("src.agents.trading.strategies.nlt_trading_strategy.MarketMakingStrategy") as MockMarketMaker, \
         patch("src.agents.trading.strategies.nlt_trading_strategy.ArbitrageStrategy") as MockArbitrage:
        
        mock_market_maker = AsyncMock()
        mock_arbitrage = AsyncMock()
        MockMarketMaker.return_value = mock_market_maker
        MockArbitrage.return_value = mock_arbitrage
        
        strategy = NLTTradingStrategy(strategy_config)
        strategy.message_bus = AsyncMock()
        strategy.message_bus.request.return_value = {"balance": 500000}
        
        # Mock arbitrage with insufficient profit
        mock_arbitrage._generate_signal.return_value = {
            "expected_profit": 0.003,  # Below 2x min_profit threshold
            "buy_exchange": "binance",
            "sell_exchange": "kraken",
            "size": 1000
        }
        
        # Mock high-confidence market making
        mock_market_maker._generate_signal.return_value = {
            "side": "buy",
            "confidence": 0.9,
            "price": 1.01,
            "size": 1000
        }
        
        signal = await strategy._generate_signal(market_data)
        assert signal is not None
        assert signal["type"] == "market_making"
        assert signal["priority"] == "medium"
        assert signal["data"]["confidence"] > 0.8
