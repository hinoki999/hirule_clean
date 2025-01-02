import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from src.agents.trading.strategies.nlt_trading_strategy import NLTTradingStrategy
from src.agents.risk.risk_manager import RiskMetrics

@pytest.fixture
def strategy_config():
    return {
        "treasury_address": "0x742d35Cc6634C0532925a3b844Bc454e4438f44e",
        "min_profit": 0.002,
        "max_slippage": 0.003,
        "treasury_threshold": 1000000,
        "max_position_size": 1000000,
        "max_total_exposure": 5000000,
        "risk_per_trade": 0.02,
        "max_drawdown": 0.15,
        "var_limit": 500000,
        "position_timeout": 24,
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
async def test_conservative_mode_with_risk_check(strategy_config, market_data):
    with patch("src.agents.trading.strategies.nlt_trading_strategy.MarketMakingStrategy") as MockMarketMaker, \
         patch("src.agents.trading.strategies.nlt_trading_strategy.ArbitrageStrategy") as MockArbitrage:
        
        mock_market_maker = AsyncMock()
        mock_arbitrage = AsyncMock()
        MockMarketMaker.return_value = mock_market_maker
        MockArbitrage.return_value = mock_arbitrage
        
        strategy = NLTTradingStrategy(strategy_config)
        strategy.message_bus = AsyncMock()
        strategy.message_bus.request.return_value = {"balance": 500000}
        
        # Mock risk manager response
        mock_risk_metrics = RiskMetrics()
        mock_risk_metrics.var_95 = 400000
        
        strategy.risk_manager.check_risk_limits = AsyncMock(return_value={
            "approved": True,
            "adjusted_size": 90000,  # Slightly reduced from original
            "risk_metrics": mock_risk_metrics,
            "message": "Trade approved with size adjustment"
        })
        
        # Mock sub-strategy signals
        mock_arbitrage._generate_signal.return_value = {
            "expected_profit": 0.005,
            "buy_exchange": "binance",
            "sell_exchange": "kraken",
            "size": 100000
        }
        
        mock_market_maker._generate_signal.return_value = {
            "side": "buy",
            "confidence": 0.9,
            "price": 1.01,
            "size": 100000
        }
        
        signal = await strategy._generate_signal(market_data)
        
        assert signal is not None
        assert signal["type"] == "arbitrage"
        assert signal["priority"] == "high"
        assert signal["size"] == 90000  # Verify risk-adjusted size
        assert "risk_metrics" in signal

@pytest.mark.asyncio
async def test_risk_rejection(strategy_config, market_data):
    with patch("src.agents.trading.strategies.nlt_trading_strategy.MarketMakingStrategy") as MockMarketMaker, \
         patch("src.agents.trading.strategies.nlt_trading_strategy.ArbitrageStrategy") as MockArbitrage:
        
        mock_market_maker = AsyncMock()
        mock_arbitrage = AsyncMock()
        MockMarketMaker.return_value = mock_market_maker
        MockArbitrage.return_value = mock_arbitrage
        
        strategy = NLTTradingStrategy(strategy_config)
        strategy.message_bus = AsyncMock()
        strategy.message_bus.request.return_value = {"balance": 1500000}
        
        # Mock risk manager to reject trade
        strategy.risk_manager.check_risk_limits = AsyncMock(return_value={
            "approved": False,
            "adjusted_size": 0,
            "risk_metrics": RiskMetrics(),
            "message": "VaR limit exceeded"
        })
        
        # Mock market making signal
        mock_market_maker._generate_signal.return_value = {
            "side": "buy",
            "confidence": 0.7,
            "price": 1.01,
            "size": 100000
        }
        
        mock_arbitrage._generate_signal.return_value = None
        
        signal = await strategy._generate_signal(market_data)
        assert signal is None  # Signal should be rejected

@pytest.mark.asyncio
async def test_signal_execution_with_position_tracking(strategy_config, market_data):
    strategy = NLTTradingStrategy(strategy_config)
    strategy.message_bus = AsyncMock()
    
    # Mock order execution
    strategy._create_order = AsyncMock(return_value={
        "status": "filled",
        "fill_price": 1.01,
        "timestamp": "2024-01-01T00:00:00Z"
    })
    
    # Test signal with risk metrics
    signal = {
        "type": "arbitrage",
        "asset": "NLT/USDT",
        "size": 90000,
        "risk_metrics": RiskMetrics(),
        "stop_loss": 0.99,
        "take_profit": 1.05
    }
    
    await strategy.execute_signal(signal)
    
    # Verify position tracking
    assert "NLT/USDT" in strategy.risk_manager.positions
    position = strategy.risk_manager.positions["NLT/USDT"]
    assert position.size == 90000
    assert position.entry_price == 1.01
    
    # Verify position update was published
    strategy.message_bus.publish.assert_called_once()
    call_args = strategy.message_bus.publish.call_args[0]
    assert call_args[0] == "position_update"
    assert call_args[1]["type"] == "new_position"
