"""
Tests for NLT Trading Agent
"""

import pytest
import asyncio
from typing import Dict
from ....core.config import Config
from ....core.messages import Message
from ..nlt_agent import NLTTradingAgent

@pytest.fixture
async def nlt_agent():
    """Create test instance of NLT trading agent"""
    config = Config({
        "risk": {
            "max_position_size": 0.1,
            "max_drawdown": 0.15
        },
        "ml": {
            "model_path": "models/nlt_predictor"
        }
    })
    
    agent = NLTTradingAgent(config)
    await agent.initialize()
    return agent

@pytest.mark.asyncio
async def test_market_data_handling(nlt_agent):
    """Test market data processing"""
    test_data = {
        "symbol": "NLT/USDT",
        "price": 1.234,
        "volume": 10000,
        "timestamp": 1641234567
    }
    
    message = Message(
        topic="market_data.nlt.trades",
        data=test_data
    )
    
    await nlt_agent.process_message(message)
    # Add assertions based on expected behavior

@pytest.mark.asyncio
async def test_risk_management(nlt_agent):
    """Test risk management integration"""
    signal = {
        "symbol": "NLT/USDT",
        "side": "buy",
        "quantity": 1000,
        "price": 1.234
    }
    
    # Test risk validation
    result = await nlt_agent.risk_manager.validate_trade(signal)
    assert "valid" in result
