import pytest
import asyncio
from datetime import datetime
from src.agents.trading.positions.trading_system import TradingSystem
from src.agents.trading.positions.order_manager import OrderType, OrderSide, OrderStatus

@pytest.fixture
def system_config():
    return {
        "initial_balance": 100000.0,
        "pnl_config": {
            "alert_thresholds": {
                "profit_target": 0.02,
                "stop_loss": 0.01,
                "max_drawdown": 0.015
            },
            "alert_cooldown": 300
        },
        "order_config": {
            "stops": {
                "stop_loss_percent": 0.02,
                "take_profit_percent": 0.03
            }
        },
        "risk_config": {
            "risk_limits": {
                "max_position_size": 10000.0,
                "max_portfolio_exposure": 50000.0,
                "max_drawdown": 0.1,
                "position_correlation_limit": 0.7,
                "volatility_threshold": 0.05
            },
            "position_size_config": {
                "account_risk": 0.02,
                "base_volatility": 0.02
            },
            "risk_weights": {
                "volatility": 0.6,
                "correlation": 0.4
            }
        }
    }

@pytest.mark.asyncio
async def test_position_lifecycle(system_config):
    """Test complete position lifecycle."""
    system = TradingSystem(system_config)
    
    # Open position
    order = await system.open_position(
        asset="BTC/USD",
        side=OrderSide.BUY,
        price=50000.0
    )
    
    assert order is not None
    assert "BTC/USD" in system.active_positions
    
    # Update position
    alerts = await system.update_position("BTC/USD", 51000.0)
    summary = await system.get_position_summary("BTC/USD")
    
    assert summary["position"]["entry_price"] == 50000.0
    assert "performance" in summary and "current_pnl" in summary["performance"]
    assert summary["performance"]["current_pnl"] > 0
    
    # Close position
    close_order = await system.close_position("BTC/USD", 51000.0)
    
    assert close_order is not None
    assert "BTC/USD" not in system.active_positions

@pytest.mark.asyncio
async def test_risk_management(system_config):
    """Test risk management integration."""
    system = TradingSystem(system_config)
    
    # Open multiple positions to test exposure limits
    positions = [
        ("BTC/USD", 49000.0),  # Slightly smaller initial prices
        ("ETH/USD", 2900.0),
        ("SOL/USD", 98.0)
    ]
    
    opened_positions = 0
    for asset, price in positions:
        order = await system.open_position(
            asset=asset,
            side=OrderSide.BUY,
            price=price
        )
        if order:
            opened_positions += 1
            # Update with smaller price movement
            await system.update_position(asset, price * 1.005)  # 0.5% increase
    
    # Get portfolio summary
    summary = await system.get_portfolio_summary()
    
    assert summary["position_count"] == opened_positions
    assert summary["total_exposure"] <= system_config["risk_config"]["risk_limits"]["max_portfolio_exposure"]

@pytest.mark.asyncio
async def test_stop_loss_trigger(system_config):
    """Test automatic position closure on stop loss."""
    system = TradingSystem(system_config)
    
    # Open position
    order = await system.open_position(
        asset="BTC/USD",
        side=OrderSide.BUY,
        price=50000.0
    )
    
    assert order is not None
    assert "BTC/USD" in system.active_positions
    
    # Update with normal price movement first
    await system.update_position("BTC/USD", 50100.0)
    
    # Trigger stop loss
    price_drop = 50000.0 * (1 - system_config["order_config"]["stops"]["stop_loss_percent"] - 0.01)
    await system.update_position("BTC/USD", price_drop)
    
    # Position should be automatically closed
    assert "BTC/USD" not in system.active_positions
