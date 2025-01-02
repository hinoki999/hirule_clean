import pytest
from decimal import Decimal
from datetime import datetime, timedelta
import numpy as np
from src.agents.trading.advanced_risk import AdvancedRiskManager
from src.agents.trading.stress_testing import StressTester
from src.agents.trading.circuit_breakers import CircuitBreaker, CircuitBreakerConfig

@pytest.fixture
def risk_setup():
    ###"""Create a complete risk management setup###"""
    risk_manager = AdvancedRiskManager(lookback_period=50)

    # Generate price data
    np.random.seed(42)
    timestamps = [datetime.now() + timedelta(minutes=i) for i in range(100)]

    # Correlated price series
    returns1 = np.random.normal(0.0001, 0.02, 100)
    returns2 = returns1 * 0.9 + np.random.normal(0.0001, 0.02, 100) * 0.1

    prices1 = 50000 * np.exp(np.cumsum(returns1))
    prices2 = 3000 * np.exp(np.cumsum(returns2))

    # Feed data
    for i in range(len(timestamps)):
        risk_manager.update_price_data("BTC/USD", prices1[i], timestamps[i])
        risk_manager.update_price_data("ETH/USD", prices2[i], timestamps[i])

    stress_tester = StressTester(risk_manager)
    circuit_breaker = CircuitBreaker(
        risk_manager=risk_manager,
        stress_tester=stress_tester,
        config=CircuitBreakerConfig(
            max_drawdown=0.15,
            var_multiplier=2.0,
            correlation_threshold=0.8,
            volatility_threshold=0.5,
            position_concentration=0.3
        )
    )

    return risk_manager, stress_tester, circuit_breaker

def test_correlation_alert(risk_setup):
    ###"""Test correlation-based alerts###"""
    _, _, circuit_breaker = risk_setup

    # Create highly concentrated positions
    positions = {
        "BTC/USD": Decimal("1.0"),
        "ETH/USD": Decimal("20.0")  # Much larger ETH position
    }

    alerts = circuit_breaker.check_portfolio_risk(positions)
    correlation_alerts = [a for a in alerts if "correlation" in a.message.lower()]

    assert len(correlation_alerts) > 0, "Should detect high correlation"
    assert correlation_alerts[0].severity == "WARNING"

def test_concentration_alert(risk_setup):
    ###"""Test position concentration alerts###"""
    _, _, circuit_breaker = risk_setup

    # Create highly concentrated position
    positions = {
        "BTC/USD": Decimal("0.1"),
        "ETH/USD": Decimal("50.0")  # Very large ETH position
    }

    alerts = circuit_breaker.check_portfolio_risk(positions)
    concentration_alerts = [a for a in alerts if "concentration" in a.message.lower()]

    assert len(concentration_alerts) > 0, "Should detect concentration risk"
    assert "ETH/USD" in concentration_alerts[0].message

def test_portfolio_recommendations(risk_setup):
    ###"""Test portfolio adjustment recommendations###"""
    _, _, circuit_breaker = risk_setup

    positions = {
        "BTC/USD": Decimal("1.0"),
        "ETH/USD": Decimal("50.0")  # Excessive position
    }

    recommendations = circuit_breaker.get_portfolio_recommendations(positions)

    assert "ETH/USD" in recommendations
    assert recommendations["ETH/USD"] < 0, "Should recommend reducing ETH position"

def test_trading_suspension(risk_setup):
    ###"""Test trading suspension triggers###"""
    _, _, circuit_breaker = risk_setup

    # Create very risky portfolio
    positions = {
        "BTC/USD": Decimal("10.0"),  # Very large positions
        "ETH/USD": Decimal("100.0")
    }

    # Check risk and get suspension decision
    circuit_breaker.check_portfolio_risk(positions)
    should_suspend, reason = circuit_breaker.should_suspend_trading()

    assert should_suspend, "Should recommend trading suspension for risky portfolio"
    assert reason, "Should provide reason for suspension"


