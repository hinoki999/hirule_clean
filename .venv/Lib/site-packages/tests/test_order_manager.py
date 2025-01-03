import pytest
import asyncio
from datetime import datetime
from src.agents.trading.positions.order_manager import (
    OrderManager, Order, OrderType, OrderSide, OrderStatus
)

@pytest.fixture
def order_config():
    return {
        "stops": {
            "stop_loss_percent": 0.02,
            "take_profit_percent": 0.03
        }
    }

@pytest.mark.asyncio
async def test_related_order_cancellation(order_config):
    """Test cancellation of related orders."""
    manager = OrderManager(order_config)
    
    # Create and fill market order
    order = await manager.create_market_order(
        asset="BTC/USD",
        side=OrderSide.BUY,
        size=1.0,
        attach_stops=True
    )
    order.status = OrderStatus.OPEN
    
    # Process fill to generate stop orders
    await manager.process_fill(order.id, 50000.0)
    
    # Verify we have both stop orders
    active_orders = manager.get_active_orders("BTC/USD")
    assert len(active_orders) == 2
    
    # Find stop loss order
    stop_loss = next(o for o in active_orders if o.order_type == OrderType.STOP_LOSS)
    take_profit = next(o for o in active_orders if o.order_type == OrderType.TAKE_PROFIT)
    
    # Verify orders are linked
    assert take_profit.id in stop_loss.related_orders
    assert stop_loss.id in take_profit.related_orders
    
    # Cancel stop loss
    success = await manager.cancel_order(stop_loss.id)
    assert success
    
    # Verify both orders are cancelled
    assert stop_loss.status == OrderStatus.CANCELLED
    assert take_profit.status == OrderStatus.CANCELLED
    
    # Verify no active orders remain
    assert len(manager.get_active_orders("BTC/USD")) == 0
