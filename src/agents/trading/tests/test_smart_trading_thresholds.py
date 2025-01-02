import pytest
from decimal import Decimal
from datetime import datetime
from src.agents.trading.messages import TradingMessageTypes
import asyncio

@pytest.mark.asyncio
async def test_threshold_adjustment(trading_agent):
   """Test threshold adjustment based on market regime."""
   symbol = "BTC/USD"
   trade_size = Decimal("1000.0")
   base_price = 50000.0

   # Simulate sufficient market data to trigger regime detection
   for _ in range(trading_agent.trading_thresholds.config.vol_window):
       await trading_agent.process_message({
           "type": TradingMessageTypes.MARKET_DATA.value,
           "payload": {
               "symbol": symbol,
               "last_price": base_price,
               "volume": 1000.0,
               "cost": 0.001,
               "timestamp": datetime.now().isoformat()
           }
       })

   await asyncio.sleep(0.1)

   threshold, size_mult = trading_agent.smart_trading_thresholds.calculate_thresholds_and_sizing(symbol, trade_size, base_price)
   
   # Convert both to float for comparison
   threshold_float = float(threshold)
   expected_threshold_normal_vol = 0.0010558323628501356

   assert abs(threshold_float - expected_threshold_normal_vol) <= 1e-4, (
       f"Expected threshold_normal_vol ({expected_threshold_normal_vol}) to be approximately {threshold_float}")
