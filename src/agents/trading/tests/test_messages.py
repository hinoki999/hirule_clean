from datetime import datetime
from decimal import Decimal
import pytest
from src.agents.trading.messages import (
    MarketData, Order, OrderType, OrderSide, 
    OrderStatus, TradingMessageTypes
)

def test_market_data_creation():
    """Test market data creation and validation"""
    timestamp = datetime.now().timestamp()
    market_data = MarketData(
        symbol="BTC/USD",
        price=Decimal("50000.0"),  # Changed from last_price to price
        timestamp=timestamp,
        bid=Decimal("49999.0"),
        ask=Decimal("50001.0"),
        volume=Decimal("1.5")
    )
    assert market_data.symbol == "BTC/USD"
    assert market_data.price == Decimal("50000.0")
def test_message_types():
    """Test trading message types are correctly defined"""
    assert TradingMessageTypes.MARKET_DATA.value == "MARKET_DATA"
    assert TradingMessageTypes.ORDER.value == "ORDER"
    assert TradingMessageTypes.TRADE.value == "TRADE"
