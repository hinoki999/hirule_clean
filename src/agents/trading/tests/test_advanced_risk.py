import pytest
import numpy as np
from decimal import Decimal
from datetime import datetime, timedelta
from src.agents.trading.advanced_risk import AdvancedRiskManager, RiskMetrics

@pytest.fixture
def risk_manager():
    return AdvancedRiskManager(lookback_period=50)

@pytest.fixture
def sample_price_data():
    ###"""Generate sample price data with known volatility###"""
    np.random.seed(42)  # For reproducibility
    initial_price = 100.0
    returns = np.random.normal(0.0001, 0.02, 100)  # mu=0.0001, sigma=0.02
    prices = initial_price * np.exp(np.cumsum(returns))
    return prices

def test_var_calculation(risk_manager, sample_price_data):
    ###"""Test VaR calculation with known price movements###"""
    position_size = Decimal("1.0")

    # Feed historical prices
    for i, price in enumerate(sample_price_data):
        risk_manager.update_price_data(
            symbol="TEST",
            price=price,
            timestamp=datetime.now() + timedelta(minutes=i)
        )

    var_95 = risk_manager.calculate_var("TEST", position_size)
    assert var_95 > 0, "VaR should be positive for a long position"
    assert var_95 < float(position_size * Decimal(str(sample_price_data[-1]))), "VaR should be less than position value"

def test_expected_shortfall(risk_manager, sample_price_data):
    ###"""Test Expected Shortfall calculation###"""
    position_size = Decimal("1.0")

    # Feed historical prices
    for i, price in enumerate(sample_price_data):
        risk_manager.update_price_data(
            symbol="TEST",
            price=price,
            timestamp=datetime.now() + timedelta(minutes=i)
        )

    es = risk_manager.calculate_expected_shortfall("TEST", position_size)
    var_95 = risk_manager.calculate_var("TEST", position_size)
    assert es >= var_95, "Expected Shortfall should be greater than or equal to VaR"

def test_position_risk_metrics(risk_manager, sample_price_data):
    ###"""Test comprehensive risk metrics calculation###"""
    position_size = Decimal("1.0")

    # Feed historical prices
    for i, price in enumerate(sample_price_data):
        risk_manager.update_price_data(
            symbol="TEST",
            price=price,
            timestamp=datetime.now() + timedelta(minutes=i)
        )

    metrics = risk_manager.calculate_position_risk_metrics("TEST", position_size)

    assert isinstance(metrics, RiskMetrics)
    assert metrics.var_99 >= metrics.var_95, "99% VaR should be greater than 95% VaR"
    assert metrics.volatility > 0, "Volatility should be positive"
    assert metrics.expected_shortfall >= metrics.var_95, "Expected Shortfall should be greater than VaR"

def test_monte_carlo_var(sample_price_data):
    ###"""Test Monte Carlo VaR calculation###"""
    risk_manager = AdvancedRiskManager(lookback_period=50, use_monte_carlo=True)
    position_size = Decimal("1.0")

    # Feed historical prices
    for i, price in enumerate(sample_price_data):
        risk_manager.update_price_data(
            symbol="TEST",
            price=price,
            timestamp=datetime.now() + timedelta(minutes=i)
        )

    mc_var = risk_manager.calculate_var("TEST", position_size)

    # Switch to historical VaR and compare
    risk_manager.use_monte_carlo = False
    hist_var = risk_manager.calculate_var("TEST", position_size)

    # Monte Carlo and historical VaR should be reasonably close
    assert abs(mc_var - hist_var) / hist_var < 0.5, "Monte Carlo and historical VaR should be reasonably similar"

def test_correlation_matrix(risk_manager, sample_price_data):
    ###"""Test correlation matrix calculation###"""
    # Feed data for two symbols
    np.random.seed(42)

    # Create correlated price series
    returns1 = np.random.normal(0.0001, 0.02, 100)
    returns2 = returns1 * 0.7 + np.random.normal(0.0001, 0.02, 100) * 0.3

    prices1 = 100 * np.exp(np.cumsum(returns1))
    prices2 = 100 * np.exp(np.cumsum(returns2))

    # Feed prices
    for i in range(len(prices1)):
        timestamp = datetime.now() + timedelta(minutes=i)
        risk_manager.update_price_data("SYM1", prices1[i], timestamp)
        risk_manager.update_price_data("SYM2", prices2[i], timestamp)

    corr_matrix = risk_manager.calculate_correlation_matrix()
    assert corr_matrix.shape == (2, 2)
    assert np.abs(corr_matrix[0, 1]) > 0.5  # Should be strongly correlated

def test_portfolio_var(risk_manager, sample_price_data):
    ###"""Test portfolio VaR calculation###"""
    # Feed data for two symbols
    np.random.seed(42)

    # Create anti-correlated price series
    returns1 = np.random.normal(0.0001, 0.02, 100)
    returns2 = -returns1 * 0.7 + np.random.normal(0.0001, 0.02, 100) * 0.3

    prices1 = 100 * np.exp(np.cumsum(returns1))
    prices2 = 100 * np.exp(np.cumsum(returns2))

    # Feed prices
    for i in range(len(prices1)):
        timestamp = datetime.now() + timedelta(minutes=i)
        risk_manager.update_price_data("SYM1", prices1[i], timestamp)
        risk_manager.update_price_data("SYM2", prices2[i], timestamp)

    # Calculate individual and portfolio VaR
    positions = {
        "SYM1": Decimal("1.0"),
        "SYM2": Decimal("1.0")
    }

    var1 = risk_manager.calculate_var("SYM1", Decimal("1.0"))
    var2 = risk_manager.calculate_var("SYM2", Decimal("1.0"))
    portfolio_var = risk_manager.calculate_portfolio_var(positions)

    # Portfolio VaR should be less than sum of individual VaRs due to diversification
    assert portfolio_var < (var1 + var2), "Portfolio VaR should show diversification benefit"


