import pytest
import asyncio
import logging
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock
from src.agents.trading.positions.models import Position
from src.agents.trading.positions.price_feed import PriceFeed, PriceUpdate
from src.agents.trading.positions.position_tracker import PositionTracker

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class MockPositionTracker(PositionTracker):
    def __init__(self, config: dict, risk_monitor, mock_price: float = None):
        mock_price_feed = PriceFeed()
        super().__init__(config, risk_monitor, mock_price_feed)
        self.mock_price = mock_price

    async def _handle_price_update(self, update: PriceUpdate) -> None:
        if self.mock_price is not None:
            update.price = self.mock_price
        await super()._handle_price_update(update)

@pytest.fixture
def config():
    return {
        "update_interval": 0.1,
        "price_feed_timeout": 5,
        "min_profit_threshold": 0.02,
        "max_loss_threshold": 0.05
    }

@pytest.fixture
def risk_monitor():
    return MagicMock()

@pytest.fixture
def position():
    return Position(
        asset="BTC/USD",
        size=1.0,
        entry_price=50000.0,
        current_price=50000.0,
        timestamp=datetime.now(),
        stop_loss=49000.0,
        take_profit=51000.0
    )

@pytest.mark.asyncio
async def test_tracker_lifecycle(config, risk_monitor):
    tracker = MockPositionTracker(config, risk_monitor)
    
    await tracker.add_position(Position(
        asset="BTC/USD",
        size=1.0,
        entry_price=50000.0,
        current_price=50000.0,
        timestamp=datetime.now()
    ))
    
    price_update = PriceUpdate(
        asset="BTC/USD",
        price=51000.0,
        timestamp=datetime.now()
    )
    await tracker.price_feed.publish_update(price_update)
    await asyncio.sleep(0.3)
    
    assert "BTC/USD" in tracker.positions
    assert tracker.positions["BTC/USD"].current_price == 51000.0

@pytest.mark.asyncio
async def test_stop_loss_trigger(config, risk_monitor):
    tracker = MockPositionTracker(config, risk_monitor, mock_price=49000.0)
    
    position = Position(
        asset="BTC/USD",
        size=1.0,
        entry_price=50000.0,
        current_price=49100.0,
        timestamp=datetime.now(),
        stop_loss=49200.0
    )
    
    await tracker.add_position(position)
    assert position.asset in tracker.positions
    
    price_update = PriceUpdate(
        asset=position.asset,
        price=49000.0,
        timestamp=datetime.now()
    )
    
    await tracker.price_feed.publish_update(price_update)
    await asyncio.sleep(0.3)  # Increased delay
    
    assert position.asset not in tracker.positions, "Position should be removed after stop loss trigger"

@pytest.mark.asyncio
async def test_take_profit_trigger(config, risk_monitor):
    tracker = MockPositionTracker(config, risk_monitor, mock_price=51500.0)
    
    position = Position(
        asset="BTC/USD",
        size=1.0,
        entry_price=50000.0,
        current_price=50800.0,
        timestamp=datetime.now(),
        stop_loss=49000.0,
        take_profit=51000.0
    )
    
    await tracker.add_position(position)
    assert position.asset in tracker.positions
    
    price_update = PriceUpdate(
        asset=position.asset,
        price=51500.0,
        timestamp=datetime.now()
    )
    
    await tracker.price_feed.publish_update(price_update)
    await asyncio.sleep(0.3)  # Increased delay
    
    assert position.asset not in tracker.positions, "Position should be removed after take profit trigger"
