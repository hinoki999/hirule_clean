import pytest
from decimal import Decimal
import numpy as np
from datetime import datetime, timedelta
from src.agents.trading.advanced_risk import AdvancedRiskManager
from src.agents.trading.stress_testing import StressTester
from src.agents.trading.circuit_breakers import CircuitBreaker, CircuitBreakerConfig
from src.agents.trading.portfolio_optimizer import (
    PortfolioOptimizer,
    OptimizationConstraints,
    OptimizationResult
)

@pytest.fixture
def optimization_setup():
    ###"""Create a complete setup for portfolio optimization testing###"""
    # Initialize risk manager with sample data
    risk_manager = AdvancedRiskManager(lookback_period=50)

    # Generate price data
    np.random.seed(42)
    timestamps = [datetime.now() + timedelta(minutes=i) for i in range(100)]

    # Generate price series with different characteristics
    returns1 = np.random.normal(0.0002, 0.02, 100)  # Higher return, higher vol
    returns2 = np.random.normal(0.0001, 0.01, 100)  # Lower return, lower vol

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
        config=CircuitBreakerConfig()
    )

    optimizer = PortfolioOptimizer(
        risk_manager=risk_manager,
        stress_tester=stress_tester,
        circuit_breaker=circuit_breaker
    )

    return optimizer, risk_manager

def test_portfolio_optimization(optimization_setup):
    ###"""Test basic portfolio optimization###"""
    optimizer, _ = optimization_setup

    current_positions = {
        "BTC/USD": Decimal("1.0"),
        "ETH/USD": Decimal("10.0")
    }

    constraints = OptimizationConstraints(
        min_position={"BTC/USD": 0.0, "ETH/USD": 0.0},
        max_position={"BTC/USD": 1.0, "ETH/USD": 1.0},
        max_total_risk=0.3,
        min_sharpe_ratio=0.5,
        max_correlation=0.7
    )

    result = optimizer.optimize_portfolio(current_positions, constraints)

    assert isinstance(result, OptimizationResult)
    assert sum(float(x) for x in result.optimal_positions.values()) == pytest.approx(1.0, rel=1e-5)
    assert result.sharpe_ratio > 0

def test_rebalancing_trades(optimization_setup):
    ###"""Test calculation of rebalancing trades###"""
    optimizer, _ = optimization_setup

    current_positions = {
        "BTC/USD": Decimal("1.0"),
        "ETH/USD": Decimal("10.0")
    }

    optimal_positions = {
        "BTC/USD": Decimal("0.8"),
        "ETH/USD": Decimal("12.0")
    }

    trades = optimizer.get_rebalancing_trades(
        current_positions,
        optimal_positions,
        min_trade_size=0.01
    )

    assert "BTC/USD" in trades
    assert "ETH/USD" in trades
    assert trades["BTC/USD"] == Decimal("-0.2")
    assert trades["ETH/USD"] == Decimal("2.0")

def test_transition_cost(optimization_setup):
    ###"""Test transition cost calculation###"""
    optimizer, _ = optimization_setup

    trades = {
        "BTC/USD": Decimal("-0.2"),
        "ETH/USD": Decimal("2.0")
    }

    cost = optimizer.calculate_transition_cost(trades)

    assert cost > 0
    assert isinstance(cost, float)

def test_risk_contribution(optimization_setup):
    ###"""Test risk contribution calculation###"""
    optimizer, _ = optimization_setup

    current_positions = {
        "BTC/USD": Decimal("1.0"),
        "ETH/USD": Decimal("10.0")
    }

    constraints = OptimizationConstraints(
        min_position={"BTC/USD": 0.0, "ETH/USD": 0.0},
        max_position={"BTC/USD": 1.0, "ETH/USD": 1.0},
        max_total_risk=0.3,
        min_sharpe_ratio=0.5,
        max_correlation=0.7
    )

    result = optimizer.optimize_portfolio(current_positions, constraints)

    assert len(result.risk_contribution) == len(current_positions)
    assert sum(result.risk_contribution.values()) == pytest.approx(1.0, rel=1e-5)


