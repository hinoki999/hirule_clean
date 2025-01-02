import pytest
from decimal import Decimal
from datetime import datetime, timedelta
import numpy as np
from src.agents.trading.rebalancing import PortfolioRebalancer, RebalancingTrigger
from src.agents.trading.portfolio_optimizer import OptimizationConstraints
from src.agents.trading.advanced_risk import AdvancedRiskManager
from src.agents.trading.stress_testing import StressTester
from src.agents.trading.circuit_breakers import CircuitBreaker, CircuitBreakerConfig
from src.agents.trading.portfolio_optimizer import PortfolioOptimizer

@pytest.fixture
def risk_manager():
    ###"""Create and populate a risk manager with sample data###"""
    manager = AdvancedRiskManager(lookback_period=50)

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
        manager.update_price_data("BTC/USD", prices1[i], timestamps[i])
        manager.update_price_data("ETH/USD", prices2[i], timestamps[i])

    return manager

@pytest.fixture
def optimization_setup(risk_manager):
    ###"""Create a complete setup for portfolio optimization testing###"""
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

@pytest.fixture
def rebalancer(optimization_setup):
    ###"""Create a rebalancer with test configuration###"""
    optimizer, _ = optimization_setup
    trigger_config = RebalancingTrigger(
        time_threshold=timedelta(days=1),
        drift_threshold=0.05,
        var_increase_threshold=0.20,
        cost_threshold=0.001
    )
    return PortfolioRebalancer(optimizer, trigger_config)

def test_drift_trigger(rebalancer):
    ###"""Test position drift trigger###"""
    current_positions = {
        "BTC/USD": Decimal("1.0"),
        "ETH/USD": Decimal("10.0")
    }

    # Set target weights significantly different from current
    rebalancer.target_weights = {
        "BTC/USD": 0.7,
        "ETH/USD": 0.3
    }

    constraints = OptimizationConstraints(
        min_position={"BTC/USD": 0.0, "ETH/USD": 0.0},
        max_position={"BTC/USD": 1.0, "ETH/USD": 1.0},
        max_total_risk=0.3,
        min_sharpe_ratio=0.5,
        max_correlation=0.7
    )

    need_rebalance, reason = rebalancer.check_rebalancing_triggers(
        current_positions, constraints)

    assert need_rebalance, "Should trigger rebalancing due to position drift"
    assert "drift" in reason.lower()

def test_cost_aware_optimization(rebalancer):
    ###"""Test cost-aware trade optimization###"""
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

    trades = rebalancer.get_optimal_trades(current_positions, constraints)

    # Verify trades respect cost threshold
    total_value = sum(float(pos * Decimal(str(
        rebalancer.optimizer.risk_manager.price_history[sym][-1])))
        for sym, pos in current_positions.items())

    cost = rebalancer.optimizer.calculate_transition_cost(trades)
    assert cost / total_value <= rebalancer.trigger_config.cost_threshold

def test_time_based_trigger(rebalancer):
    ###"""Test time-based rebalancing trigger###"""
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

    # Set last rebalance to more than threshold ago
    rebalancer.last_rebalance = datetime.now() - timedelta(days=2)

    need_rebalance, reason = rebalancer.check_rebalancing_triggers(
        current_positions, constraints)

    assert need_rebalance, "Should trigger rebalancing due to time threshold"
    assert "time" in reason.lower()


