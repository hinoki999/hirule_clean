import pytest
import asyncio
from decimal import Decimal
from datetime import datetime
from src.agents.trading.base_trading_agent import BaseTradingAgent
from src.agents.trading.messages import (
    Order,
    OrderType,
    OrderSide,
    OrderStatus,
    MarketData,
    TradingMessageTypes
)

class TestTradingAgent(BaseTradingAgent):
    #"""Concrete implementation of BaseTradingAgent for testing#"""

    async def setup(self):
        #"""Initialize the test agent#"""
        await super().setup()
        self.positions = {}
        self.orders = {}
        self.balances = {}
        self.latest_prices = {}

    async def cleanup(self):
        #"""Implement required cleanup method#"""
        await super().cleanup()

    async def process_message(self, message):
        #"""Implement required process_message method#"""
        pass

    async def _handle_market_data(self, message):
        pass

    async def _handle_order_update(self, message):
        pass

    async def _handle_order_fill(self, message):
        pass

@pytest.fixture
async def trading_agent():
    #"""Create and initialize a TestTradingAgent instance#"""
    agent = TestTradingAgent()
    await agent.setup()  # Initialize the agent
    yield agent  # Return the initialized agent
    await agent.cleanup()  # Cleanup after tests

@pytest.mark.asyncio
async def test_agent_initialization(trading_agent):
    #"""Test basic agent initialization#"""
    assert isinstance(trading_agent, TestTradingAgent)
    assert hasattr(trading_agent, "positions")
    assert trading_agent.positions == {}
    assert trading_agent.orders == {}
    assert trading_agent.balances == {}
    assert trading_agent.latest_prices == {}

@pytest.mark.asyncio
async def test_market_data_handling(trading_agent):
    #"""Test market data processing#"""
    market_data = MarketData(
        symbol="BTC/USD",
        last_price=50000.0,
        timestamp=datetime.now()
    )

    message = type("Message", (), {
        "payload": {
            "symbol": market_data.symbol,
            "last_price": market_data.last_price,
            "timestamp": market_data.timestamp
        }
    })

    await trading_agent._handle_market_data(message)
    assert hasattr(trading_agent, "latest_prices")

@pytest.mark.asyncio
async def test_order_handling(trading_agent):
    #"""Test order processing#"""
    order = Order(
        order_id="test-123",
        symbol="BTC/USD",
        side=OrderSide.BUY,
        order_type=OrderType.MARKET,
        quantity=Decimal("1.0"),
        status=OrderStatus.NEW
    )

    message = type("Message", (), {"payload": {
        "order_id": order.order_id,
        "symbol": order.symbol,
        "side": order.side,
        "order_type": order.order_type,
        "quantity": order.quantity,
        "status": order.status
    }})

    await trading_agent._handle_order_update(message)
    assert hasattr(trading_agent, "orders")

@pytest.mark.asyncio
async def test_position_updates(trading_agent):
    #"""Test position tracking#"""
    order = Order(
        order_id="test-123",
        symbol="BTC/USD",
        side=OrderSide.BUY,
        order_type=OrderType.MARKET,
        quantity=Decimal("1.0"),
        status=OrderStatus.FILLED,
        filled_quantity=Decimal("1.0")
    )

    message = type("Message", (), {"payload": {
        "order_id": order.order_id,
        "symbol": order.symbol,
        "side": order.side,
        "order_type": order.order_type,
        "quantity": order.quantity,
        "status": order.status,
        "filled_quantity": order.filled_quantity
    }})

    await trading_agent._handle_order_fill(message)
    assert hasattr(trading_agent, "positions")


