import pytest
import asyncio
from datetime import datetime, timedelta
from src.agents.trading.positions.models import Position
from src.agents.trading.positions.pnl_monitor import PnLMonitor

@pytest.fixture
def monitor_config():
    return {
        'alert_thresholds': {
            'profit_target': 2.0,   # 2% profit target
            'stop_loss': 1.0,       # 1% stop loss
            'max_drawdown': 1.5     # 1.5% max drawdown
        },
        'alert_cooldown': 1  # 1 second for testing
    }

@pytest.fixture
def position():
    return Position(
        asset="BTC/USD",
        size=1.0,
        entry_price=50000.0,
        current_price=50000.0,
        timestamp=datetime.now() - timedelta(hours=1)
    )

@pytest.mark.asyncio
async def test_profit_target_alert(monitor_config, position):
    """Test profit target alert generation."""
    monitor = PnLMonitor(monitor_config)
    
    # Update with price above profit target
    alerts = await monitor.update_position(position, 51100.0)  # 2.2% profit
    
    assert len(alerts) == 1
    assert alerts[0].alert_type == 'profit_target'
    assert alerts[0].severity == 'info'

@pytest.mark.asyncio
async def test_stop_loss_alert(monitor_config, position):
    """Test stop loss alert generation."""
    monitor = PnLMonitor(monitor_config)
    
    # Update with price below stop loss
    alerts = await monitor.update_position(position, 49400.0)  # -1.2% loss
    
    assert len(alerts) == 1
    assert alerts[0].alert_type == 'stop_loss'
    assert alerts[0].severity == 'warning'

@pytest.mark.asyncio
async def test_drawdown_alert(monitor_config, position):
    """Test drawdown alert generation."""
    monitor = PnLMonitor(monitor_config)
    
    # First push price up
    await monitor.update_position(position, 51000.0)
    
    # Then drop it to trigger drawdown
    alerts = await monitor.update_position(position, 50200.0)
    
    assert len(alerts) == 1
    assert alerts[0].alert_type == 'drawdown'
    assert alerts[0].severity == 'critical'

@pytest.mark.asyncio
async def test_alert_cooldown(monitor_config, position):
    """Test alert cooldown functionality."""
    monitor = PnLMonitor(monitor_config)
    
    # Generate first alert
    alerts1 = await monitor.update_position(position, 49400.0)
    assert len(alerts1) == 1
    
    # Immediate second update should not generate alert
    alerts2 = await monitor.update_position(position, 49400.0)
    assert len(alerts2) == 0
    
    # Wait for cooldown
    await asyncio.sleep(1.1)
    
    # Should generate alert again
    alerts3 = await monitor.update_position(position, 49400.0)
    assert len(alerts3) == 1

@pytest.mark.asyncio
async def test_performance_summary(monitor_config, position):
    """Test performance summary calculation."""
    monitor = PnLMonitor(monitor_config)
    
    # Create price sequence
    prices = [50000.0, 51000.0, 50500.0, 50800.0]
    
    for price in prices:
        await monitor.update_position(position, price)
    
    summary = monitor.get_performance_summary(position.asset)
    
    assert summary['current_pnl'] == 800.0  # Based on final price
    assert summary['peak_pnl'] == 1000.0    # Based on highest price
    assert 'current_drawdown' in summary
    assert 'last_updated' in summary
