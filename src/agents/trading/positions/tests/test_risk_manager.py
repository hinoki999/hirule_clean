import pytest
from datetime import datetime
from unittest.mock import MagicMock, AsyncMock
from src.agents.trading.positions.pnl_monitor import PnLMonitor
from src.agents.trading.positions.risk_manager import RiskManager

@pytest.fixture
def risk_config():
    return {
        'risk_limits': {
            'max_position_size': 100000.0,
            'max_portfolio_exposure': 500000.0,
            'max_drawdown': 10.0,
            'position_correlation_limit': 0.7,
            'volatility_threshold': 0.05
        },
        'position_size_config': {
            'account_risk': 0.02,
            'base_volatility': 0.02
        },
        'risk_weights': {
            'volatility': 0.6,
            'correlation': 0.4
        }
    }

@pytest.fixture
def mock_pnl_monitor():
    monitor = MagicMock(spec=PnLMonitor)
    monitor.get_performance_summary.return_value = {
        'current_pnl': 1000.0,
        'current_roi': 2.0,
        'peak_pnl': 1500.0
    }
    return monitor

@pytest.mark.asyncio
async def test_position_size_calculation(risk_config, mock_pnl_monitor):
    """Test position size calculation."""
    risk_manager = RiskManager(risk_config, mock_pnl_monitor)
    
    position_size = await risk_manager.calculate_position_size("BTC/USD", 1000000.0)
    
    assert position_size > 0
    assert position_size <= risk_config['risk_limits']['max_position_size']

@pytest.mark.asyncio
async def test_risk_profile_update(risk_config, mock_pnl_monitor):
    """Test risk profile updates."""
    risk_manager = RiskManager(risk_config, mock_pnl_monitor)
    
    profile = await risk_manager.update_risk_profile("BTC/USD")
    
    assert profile.asset == "BTC/USD"
    assert profile.risk_score >= 0
    assert profile.risk_score <= 1
    assert profile.position_limit <= risk_config['risk_limits']['max_portfolio_exposure']

@pytest.mark.asyncio
async def test_portfolio_risk_checks(risk_config, mock_pnl_monitor):
    """Test portfolio risk monitoring."""
    risk_manager = RiskManager(risk_config, mock_pnl_monitor)
    
    # Add a position to trigger risk checks
    await risk_manager.update_risk_profile("BTC/USD")
    risk_manager.portfolio_exposure = risk_config['risk_limits']['max_portfolio_exposure']
    
    alerts = await risk_manager.check_portfolio_risk()
    
    assert len(alerts) > 0
    assert any(alert['type'] == 'exposure_limit' for alert in alerts)

@pytest.mark.asyncio
async def test_correlation_adjustment(risk_config, mock_pnl_monitor):
    """Test correlation-based position sizing."""
    risk_manager = RiskManager(risk_config, mock_pnl_monitor)
    
    # Add correlated assets
    await risk_manager.update_risk_profile("BTC/USD")
    
    # Calculate size for correlated asset
    size = await risk_manager.calculate_position_size("ETH/USD", 1000000.0)
    
    assert size > 0
    assert size <= risk_config['risk_limits']['max_position_size']
