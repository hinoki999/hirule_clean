import pytest
from unittest.mock import MagicMock, patch
from ....core.message_bus import MessageBus
from ..nlt_momentum_strategy import NLTMomentumStrategy

@pytest.fixture
async def momentum_strategy():
    config = {
        "lookback_period": 5,
        "min_trade_size": "0.1",
        "max_position_size": "1000.0",
        "risk_per_trade": "0.02",
    }
    strategy = NLTMomentumStrategy(config)
    
    # Mock message bus
    strategy.message_bus = MagicMock(spec=MessageBus)
    
    return strategy

@pytest.mark.asyncio
async def test_market_data_handling(momentum_strategy):
    """Test market data message handling"""
    market_data = {
        "symbol": "NLT/USDT",
        "last_price": "100.0",
        "volume": "1000"
    }
    
    # Test message handling
    await momentum_strategy._handle_market_data(market_data)
    
    # Verify message bus interactions
    momentum_strategy.message_bus.publish.assert_called_with(
        "trade_signal",
        pytest.approx({
            "symbol": "NLT/USDT",
            "action": "buy",
            "confidence": pytest.approx(0.8, rel=0.1)
        })
    )
