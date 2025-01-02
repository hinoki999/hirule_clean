import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
import numpy as np
from src.agents.risk.risk_manager import RiskManager, RiskManagerError, Position

@pytest.fixture
def risk_config():
    return {
        "max_position_size": 1000000,  # 1M tokens
        "max_total_exposure": 5000000,  # 5M tokens worth
        "risk_per_trade": 0.02,        # 2% risk per trade
        "max_drawdown": 0.15,          # 15% max drawdown
        "var_limit": 500000,           # $500k VaR limit
        "position_timeout": 24          # 24 hour timeout
    }

@pytest.fixture
def trade_proposal():
    return {
        "asset": "NLT/USDT",
        "size": 100000,
        "entry_price": 1.05,
        "stop_loss": 1.00,
        "take_profit": 1.15
    }

@pytest.mark.asyncio
async def test_initialization(risk_config):
    manager = RiskManager(risk_config)
    assert manager.config == risk_config
    assert manager.positions == {}
    assert manager.metrics is not None

@pytest.mark.asyncio
async def test_invalid_config():
    invalid_config = {
        "max_position_size": 1000000,
        "risk_per_trade": 0.2  # Invalid: 20% risk per trade
    }
    
    with pytest.raises(RiskManagerError):
        RiskManager(invalid_config)

@pytest.mark.asyncio
async def test_position_size_calculation(risk_config):
    manager = RiskManager(risk_config)
    
    # Mock portfolio value
    manager._get_portfolio_value = MagicMock(return_value=1000000)
    manager._get_remaining_exposure = MagicMock(return_value=float('inf'))
    
    size = manager.calculate_position_size(
        asset="NLT/USDT",
        entry_price=1.05,
        stop_loss=1.00
    )
    
    assert size > 0
    assert size <= risk_config["max_position_size"]

@pytest.mark.asyncio
async def test_risk_limits_check(risk_config, trade_proposal):
    manager = RiskManager(risk_config)
    
    # Mock risk metrics calculation
    mock_metrics = MagicMock()
    mock_metrics.var_95 = 400000  # Below VaR limit
    mock_metrics.max_drawdown = 0.1  # Below max drawdown
    
    manager._calculate_risk_metrics = AsyncMock(return_value=mock_metrics)
    manager._get_remaining_exposure = MagicMock(return_value=1000000)
    manager.calculate_position_size = MagicMock(return_value=100000)
    
    result = await manager.check_risk_limits(trade_proposal)
    
    assert result["approved"] == True
    assert result["adjusted_size"] > 0
    assert "risk_metrics" in result

@pytest.mark.asyncio
async def test_position_update(risk_config):
    manager = RiskManager(risk_config)
    
    # Add a test position
    position = Position(
        asset="NLT/USDT",
        size=100000,
        entry_price=1.05,
        current_price=1.05,
        timestamp=datetime.now(),
        stop_loss=1.00,
        take_profit=1.15
    )
    
    manager.positions["NLT/USDT"] = position
    
    # Test stop loss trigger
    await manager.update_position("NLT/USDT", 0.99)
    
    # Test take profit trigger
    await manager.update_position("NLT/USDT", 1.16)
    
    # Test normal update
    await manager.update_position("NLT/USDT", 1.07)
    assert manager.positions["NLT/USDT"].current_price == 1.07

@pytest.mark.asyncio
async def test_risk_metrics_calculation(risk_config, trade_proposal):
    manager = RiskManager(risk_config)
    
    # Add some historical price data
    manager.historical_prices["NLT/USDT"] = [1.0, 1.02, 1.01, 1.03, 1.02]
    
    # Add some positions
    position = Position(
        asset="NLT/USDT",
        size=100000,
        entry_price=1.0,
        current_price=1.02,
        timestamp=datetime.now()
    )
    manager.positions["NLT/USDT"] = position
    
    metrics = await manager._calculate_risk_metrics(trade_proposal)
    
    assert metrics.var_95 >= 0
    assert 0 <= metrics.max_drawdown <= 1
    assert metrics.current_exposure > 0
