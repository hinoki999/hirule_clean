import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, timedelta
from src.agents.risk.monitoring.risk_monitor import (
    RiskMonitor,
    RiskAlert,
    AlertType,
    AlertSeverity
)
from src.agents.risk.risk_manager import Position

@pytest.fixture
def monitor_config():
    return {
        "alert_thresholds": {
            "var_limit": 500000,
            "max_drawdown": 0.15,
            "position_loss_limit": 0.05,
            "exposure_limit": 5000000
        },
        "alert_cooldown": 300,  # 5 minutes
        "notification_endpoints": [
            "https://api.example.com/webhook",
            "mailto:risk@example.com"
        ]
    }

@pytest.fixture
def risk_metrics():
    return {
        "var_95": 600000,  # Above limit
        "max_drawdown": 0.12,  # Below limit
        "current_exposure": 4000000,
        "peak_exposure": 4500000,
        "sharpe_ratio": 1.5
    }

@pytest.fixture
def positions():
    return {
        "NLT/USDT": Position(
            asset="NLT/USDT",
            size=100000,
            entry_price=1.05,
            current_price=0.98,  # Losing position
            timestamp=datetime.now(),
            stop_loss=0.95,
            take_profit=1.15
        )
    }

@pytest.mark.asyncio
async def test_var_breach_alert(monitor_config, risk_metrics, positions):
    monitor = RiskMonitor(monitor_config)
    alerts = await monitor.check_risk_metrics(risk_metrics, positions)
    
    var_alerts = [a for a in alerts if a.alert_type == AlertType.VAR_BREACH]
    assert len(var_alerts) == 1
    alert = var_alerts[0]
    assert alert.severity == AlertSeverity.CRITICAL
    assert alert.current_value == risk_metrics["var_95"]
    assert alert.threshold == monitor_config["alert_thresholds"]["var_limit"]

@pytest.mark.asyncio
async def test_position_loss_alert(monitor_config, risk_metrics, positions):
    monitor = RiskMonitor(monitor_config)
    alerts = await monitor.check_risk_metrics(risk_metrics, positions)
    
    position_alerts = [a for a in alerts if a.alert_type == AlertType.POSITION_LOSS]
    assert len(position_alerts) == 1
    alert = position_alerts[0]
    assert alert.severity == AlertSeverity.WARNING
    assert alert.asset == "NLT/USDT"
    assert alert.current_value < -monitor_config["alert_thresholds"]["position_loss_limit"]

@pytest.mark.asyncio
async def test_alert_cooldown(monitor_config, risk_metrics, positions):
    monitor = RiskMonitor(monitor_config)
    
    # First check should generate alerts
    alerts1 = await monitor.check_risk_metrics(risk_metrics, positions)
    alert_types = {(a.alert_type, a.asset) for a in alerts1}
    assert len(alerts1) > 0
    
    # Immediate second check should respect cooldown
    alerts2 = await monitor.check_risk_metrics(risk_metrics, positions)
    assert len(alerts2) == 0, "Got alerts before cooldown expired"
    
    # Simulate cooldown period passed
    monitor.last_alert_times = {
        key: datetime.now() - timedelta(seconds=monitor_config["alert_cooldown"] + 1)
        for key in monitor.last_alert_times
    }
    
    # Should generate alerts again
    alerts3 = await monitor.check_risk_metrics(risk_metrics, positions)
    new_alert_types = {(a.alert_type, a.asset) for a in alerts3}
    assert alert_types == new_alert_types, "Alerts after cooldown don't match original alerts"

@pytest.mark.asyncio
async def test_alert_history_filtering(monitor_config, risk_metrics, positions):
    monitor = RiskMonitor(monitor_config)
    await monitor.check_risk_metrics(risk_metrics, positions)
    
    # Test filtering by type
    var_alerts = monitor.get_alert_history(alert_type=AlertType.VAR_BREACH)
    assert all(a.alert_type == AlertType.VAR_BREACH for a in var_alerts)
    
    # Test filtering by severity
    critical_alerts = monitor.get_alert_history(severity=AlertSeverity.CRITICAL)
    assert all(a.severity == AlertSeverity.CRITICAL for a in critical_alerts)
    
    # Test time filtering
    recent_alerts = monitor.get_alert_history(
        start_time=datetime.now() - timedelta(minutes=1)
    )
    assert len(recent_alerts) > 0
