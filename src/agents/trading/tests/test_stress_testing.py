import pytest
import numpy as np
from decimal import Decimal
from datetime import datetime, timedelta
from src.agents.trading.advanced_risk import AdvancedRiskManager
from src.agents.trading.stress_testing import StressTester, StressScenario

@pytest.fixture
def setup_risk_manager():
    ###"""Create and populate a risk manager with sample data###"""
    risk_manager = AdvancedRiskManager(lookback_period=50)

    # Generate sample price data
    np.random.seed(42)
    timestamps = [datetime.now() + timedelta(minutes=i) for i in range(100)]

    # BTC prices around 50000 with some volatility
    btc_returns = np.random.normal(0.0001, 0.02, 100)
    btc_prices = 50000 * np.exp(np.cumsum(btc_returns))

    # ETH prices around 3000 with correlation to BTC
    eth_returns = btc_returns * 0.7 + np.random.normal(0.0001, 0.02, 100) * 0.3
    eth_prices = 3000 * np.exp(np.cumsum(eth_returns))

    # Feed data to risk manager
    for i in range(len(timestamps)):
        risk_manager.update_price_data("BTC/USD", btc_prices[i], timestamps[i])
        risk_manager.update_price_data("ETH/USD", eth_prices[i], timestamps[i])

    return risk_manager

@pytest.fixture
def stress_tester(setup_risk_manager):
    ###"""Create a stress tester with the populated risk manager###"""
    return StressTester(setup_risk_manager)

def test_historical_scenario(stress_tester):
    ###"""Test running a historical stress scenario###"""
    positions = {
        "BTC/USD": Decimal("1.0"),
        "ETH/USD": Decimal("10.0")
    }

    results = stress_tester.run_historical_scenario("crypto_crash_2022", positions)

    assert results["total_pnl"] < 0, "Crash scenario should result in losses"
    assert results["stressed_var"] > results["base_var"], "Stressed VaR should be higher"
    assert results["var_increase"] > 0, "VaR should increase under stress"

def test_custom_scenario(stress_tester):
    ###"""Test creating and running a custom scenario###"""
    scenario = stress_tester.create_custom_scenario(
        name="custom_test",
        price_shocks={"BTC/USD": -0.1, "ETH/USD": -0.15},
        volatility_multiplier=2.0
    )

    positions = {
        "BTC/USD": Decimal("0.5"),
        "ETH/USD": Decimal("5.0")
    }

    results = stress_tester.run_historical_scenario("custom_test", positions)
    assert "total_pnl" in results
    assert results["scenario_name"] == "custom_test"

def test_monte_carlo_stress(stress_tester):
    ###"""Test Monte Carlo stress testing###"""
    positions = {
        "BTC/USD": Decimal("1.0"),
        "ETH/USD": Decimal("10.0")
    }

    results = stress_tester.monte_carlo_stress_test(positions, n_scenarios=1000)

    assert results["worst_loss"] > 0, "Should calculate worst-case loss"
    assert results["var_99"] > 0, "Should calculate 99% VaR"
    assert results["expected_shortfall"] >= results["var_99"], "Expected shortfall should be >= VaR"
    assert 0 <= results["max_drawdown"] <= 1, "Max drawdown should be between 0 and 1"

def test_correlation_breakdown_scenario(stress_tester):
    ###"""Test scenario where correlations break down###"""
    positions = {
        "BTC/USD": Decimal("1.0"),
        "ETH/USD": Decimal("10.0")
    }

    results = stress_tester.run_historical_scenario("correlation_breakdown", positions)
    assert "var_increase" in results
    assert results["var_increase"] > 0, "VaR should increase when correlations break down"


