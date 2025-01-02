import pytest
import asyncio
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock
from src.agents.trading.positions.models import Position
from src.agents.trading.positions.price_feed import PriceFeed, PriceUpdate
from src.agents.trading.positions.position_tracker import PositionTracker

@pytest.fixture
def price_feed():
    return PriceFeed()

@pytest.fixture
def tracker_config():
    return {
        "update_interval": 0.1,
        "price_feed_timeout": 5,
        "min_profit_threshold": 0.02,
        "max_loss_threshold": 0.05
    }

@pytest.fixture
def risk_monitor():
    return MagicMock()

@pytest.mark.asyncio
async def test_price_subscription(tracker_config, risk_monitor, price_feed):
    """Test price feed subscription and updates."""
    tracker = PositionTracker(tracker_config, risk_monitor, price_feed)
    
    # Add a position
    position = Position(
        asset="BTC/USD",
        size=1.0,
        entry_price=50000.0,
        current_price=50000.0,
        timestamp=datetime.now()
    )
    
    await tracker.add_position(position)
    
    # Simulate price update
    price_update = PriceUpdate(
        asset="BTC/USD",
        price=51000.0,
        bid=50990.0,
        ask=51010.0
    )
    
    await price_feed.publish_update(price_update)
    
    # Check that position was updated
    assert tracker.positions["BTC/USD"].current_price == 51000.0
    assert tracker.position_pnl["BTC/USD"] == pytest.approx(2.0)  # 2% profit

@pytest.mark.asyncio
async def test_pnl_calculation(tracker_config, risk_monitor, price_feed):
    """Test P&L calculations with price updates."""
    tracker = PositionTracker(tracker_config, risk_monitor, price_feed)
    
    # Add position
    position = Position(
        asset="ETH/USD",
        size=10.0,
        entry_price=2000.0,
        current_price=2000.0,
        timestamp=datetime.now()
    )
    
    await tracker.add_position(position)
    
    # Simulate price updates
    updates = [
        PriceUpdate(asset="ETH/USD", price=2100.0),  # +5%
        PriceUpdate(asset="ETH/USD", price=1900.0),  # -5%
        PriceUpdate(asset="ETH/USD", price=2200.0)   # +10%
    ]
    
    for update in updates:
        await price_feed.publish_update(update)
        await asyncio.sleep(0.1)  # Give time for updates to process
    
    # Check final P&L
    assert tracker.position_pnl["ETH/USD"] == pytest.approx(10.0)  # 10% profit

@pytest.mark.asyncio
async def test_position_summary(tracker_config, risk_monitor, price_feed):
    """Test position summary with multiple positions."""
    tracker = PositionTracker(tracker_config, risk_monitor, price_feed)
    
    # Add multiple positions
    positions = [
        Position(
            asset="BTC/USD",
            size=1.0,
            entry_price=50000.0,
            current_price=50000.0,
            timestamp=datetime.now()
        ),
        Position(
            asset="ETH/USD",
            size=10.0,
            entry_price=2000.0,
            current_price=2000.0,
            timestamp=datetime.now()
        )
    ]
    
    for position in positions:
        await tracker.add_position(position)
    
    # Update prices
    updates = [
        PriceUpdate(asset="BTC/USD", price=55000.0),  # +10%
        PriceUpdate(asset="ETH/USD", price=2200.0)    # +10%
    ]
    
    for update in updates:
        await price_feed.publish_update(update)
    
    # Get summary
    summary = tracker.get_position_summary()
    
    assert summary["total_positions"] == 2
    assert summary["average_pnl"] == pytest.approx(10.0)  # Both positions +10%
    assert len(summary["positions"]) == 2
