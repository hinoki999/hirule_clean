import pytest
from datetime import datetime
from src.agents.trading.messages import TradingMessageTypes
import asyncio

@pytest.mark.asyncio
async def test_initial_state(trading_agent):
    """Test the initial state of the market regime detector."""
    symbol = "BTC/USD"
    base_price = 50000.0
    volume = 1000.0
    trade_cost = 0.001

    required_data_points = trading_agent.trading_thresholds.config.vol_window

    # Provide sufficient market data
    for _ in range(required_data_points):
        await trading_agent.process_message({
            "type": TradingMessageTypes.MARKET_DATA.value,
            "payload": {
                "symbol": symbol,
                "last_price": base_price,
                "volume": volume,
                "cost": trade_cost,
                "timestamp": datetime.now().isoformat()
            }
        })

    await asyncio.sleep(0.1)

    regime_confidence = trading_agent.market_regime_detector.get_regime_confidence(symbol)
    assert regime_confidence == 0.5, f"Initial regime confidence should be 0.5, got {regime_confidence}"



