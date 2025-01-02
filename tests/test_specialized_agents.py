import pytest
import asyncio
from datetime import datetime
from src.message_system.core.message_bus import MessageBus, MessageType, AgentMessage
from src.message_system.agents.specialized_agents import (
    MarketDataAgent,
    StrategyAgent,
    CoordinatorAgent,
    LearningAgent
)

@pytest.mark.asyncio
async def test_market_data_agent():
    message_bus = MessageBus()
    market_agent = MarketDataAgent("market_agent", message_bus)
    
    # Test market data processing
    test_data = {
        "symbol": "BTC-USD",
        "price": 50000.0,
        "timestamp": str(datetime.now())
    }
    
    message = AgentMessage(
        msg_type=MessageType.MARKET_DATA,
        sender_id="test",
        timestamp=datetime.now(),
        data=test_data
    )
    
    await market_agent.receive_message(message)
    assert "BTC-USD" in market_agent.latest_prices
    assert market_agent.latest_prices["BTC-USD"] == 50000.0

@pytest.mark.asyncio
async def test_strategy_agent():
    message_bus = MessageBus()
    strategy_agent = StrategyAgent("strategy_agent", message_bus)
    
    # Add test strategy
    strategy_agent.active_strategies["BTC-USD"] = {
        "type": "simple_momentum",
        "parameters": {"threshold": 0.01}
    }
    
    # Test strategy processing
    test_data = {
        "symbol": "BTC-USD",
        "price": 50000.0,
        "timestamp": str(datetime.now())
    }
    
    message = AgentMessage(
        msg_type=MessageType.MARKET_DATA,
        sender_id="test",
        timestamp=datetime.now(),
        data=test_data
    )
    
    await strategy_agent.receive_message(message)
