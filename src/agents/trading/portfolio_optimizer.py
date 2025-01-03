from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from decimal import Decimal, ROUND_HALF_UP
import numpy as np
from datetime import datetime
from .advanced_risk import AdvancedRiskManager
from .stress_testing import StressTester
from .circuit_breakers import CircuitBreaker

@dataclass
class OptimizationConstraints:
    ###"""Constraints for portfolio optimization###"""
    min_position: Dict[str, float]  # Minimum position sizes
    max_position: Dict[str, float]  # Maximum position sizes
    max_total_risk: float  # Maximum portfolio VaR
    min_sharpe_ratio: float  # Minimum Sharpe ratio
    max_correlation: float  # Maximum pairwise correlation
    risk_free_rate: float = 0.02  # Annual risk-free rate

@dataclass
class OptimizationResult:
    ###"""Results from portfolio optimization###"""
    optimal_positions: Dict[str, Decimal]
    expected_return: float
    expected_risk: float
    sharpe_ratio: float
    risk_contribution: Dict[str, float]
    turnover: float  # Portfolio turnover to reach optimal allocation

class PortfolioOptimizer:
    ###"""Portfolio optimization with risk management###"""

    def __init__(self,
                 risk_manager: AdvancedRiskManager,
                 stress_tester: StressTester,
                 circuit_breaker: CircuitBreaker):
        ###"""Initialize the portfolio optimizer###"""
        self.risk_manager = risk_manager
        self.stress_tester = stress_tester
        self.circuit_breaker = circuit_breaker

    def calculate_expected_returns(self, lookback_days: int = 30) -> Dict[str, float]:
        ###"""Calculate expected returns using historical data###"""
        expected_returns = {}

        for symbol in self.risk_manager.price_history.keys():
            prices = list(self.risk_manager.price_history[symbol])
            if len(prices) >= 2:
                # Calculate log returns
                returns = np.log(np.array(prices[1:]) / np.array(prices[:-1]))
                # Annualize returns
                expected_returns[symbol] = float(np.mean(returns) * 252)
            else:
                expected_returns[symbol] = 0.0

        return expected_returns

    def get_rebalancing_trades(self,
                             current_positions: Dict[str, Decimal],
                             optimal_positions: Dict[str, Decimal],
                             min_trade_size: float = 0.01) -> Dict[str, Decimal]:
        ###"""Calculate required trades to reach optimal allocation###"""
        trades = {}

        for symbol in current_positions.keys():
            current_size = Decimal(str(current_positions[symbol]))
            target_size = Decimal(str(optimal_positions[symbol]))

            # Use quantize for precise decimal arithmetic
            trade_size = (target_size - current_size).quantize(Decimal('0.00000001'), rounding=ROUND_HALF_UP)

            if abs(trade_size) >= Decimal(str(min_trade_size)):
                trades[symbol] = trade_size

        return trades

    def optimize_portfolio(self,
                         current_positions: Dict[str, Decimal],
                         constraints: OptimizationConstraints,
                         optimization_goal: str = 'sharpe') -> OptimizationResult:
        ###"""Optimize portfolio allocation using risk metrics###"""
        symbols = list(current_positions.keys())
        n_assets = len(symbols)

        # Get expected returns
        expected_returns = self.calculate_expected_returns()

        # Get covariance matrix
        returns_data = []
        for symbol in symbols:
            returns = list(self.risk_manager.returns_history[symbol])
            returns_data.append(returns)

        returns_matrix = np.array(returns_data).T
        cov_matrix = np.cov(returns_matrix.T) * 252  # Annualized

        def objective(weights):
            portfolio_return = np.sum(weights * np.array([expected_returns[s] for s in symbols]))
            portfolio_vol = np.sqrt(weights.T @ cov_matrix @ weights)

            if optimization_goal == 'sharpe':
                return -(portfolio_return - constraints.risk_free_rate) / portfolio_vol
            elif optimization_goal == 'min_variance':
                return portfolio_vol
            else:
                return -portfolio_return

        constraints_list = [
            {'type': 'eq', 'fun': lambda x: np.sum(x) - 1.0},
        ]

        bounds = []
        for symbol in symbols:
            min_pos = constraints.min_position.get(symbol, 0.0)
            max_pos = constraints.max_position.get(symbol, 1.0)
            bounds.append((min_pos, max_pos))

        from scipy.optimize import minimize

        initial_weights = np.array([1.0/n_assets] * n_assets)

        result = minimize(
            objective,
            initial_weights,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints_list
        )

        if not result.success:
            raise ValueError("Portfolio optimization failed to converge")

        optimal_weights = result.x
        optimal_positions = {
            symbol: Decimal(str(weight)).quantize(Decimal('0.00000001'), rounding=ROUND_HALF_UP)
            for symbol, weight in zip(symbols, optimal_weights)
        }

        portfolio_return = np.sum(optimal_weights * np.array([expected_returns[s] for s in symbols]))
        portfolio_risk = np.sqrt(optimal_weights.T @ cov_matrix @ optimal_weights)
        sharpe_ratio = (portfolio_return - constraints.risk_free_rate) / portfolio_risk

        # Calculate and normalize risk contribution
        risk_contribution = {}
        total_risk = 0.0

        for i, symbol in enumerate(symbols):
            marginal_risk = (cov_matrix @ optimal_weights)[i]
            component_risk = optimal_weights[i] * marginal_risk
            risk_contribution[symbol] = float(component_risk)
            total_risk += component_risk

        # Normalize risk contributions to sum to 1
        if total_risk > 0:
            risk_contribution = {
                symbol: contrib / total_risk
                for symbol, contrib in risk_contribution.items()
            }

        current_weights = np.array([float(current_positions[s]) for s in symbols])
        current_weights = current_weights / np.sum(current_weights)
        turnover = np.sum(np.abs(optimal_weights - current_weights))

        return OptimizationResult(
            optimal_positions=optimal_positions,
            expected_return=float(portfolio_return),
            expected_risk=float(portfolio_risk),
            sharpe_ratio=float(sharpe_ratio),
            risk_contribution=risk_contribution,
            turnover=float(turnover)
        )

    def calculate_transition_cost(self, trades: Dict[str, Decimal]) -> float:
        ###"""Estimate the cost of transitioning the portfolio###"""
        total_cost = 0.0

        for symbol, size in trades.items():
            # Assume simple linear price impact model
            price = float(self.risk_manager.price_history[symbol][-1])
            trade_value = abs(float(size) * price)

            # Estimate trading costs (spread + impact)
            spread_cost = trade_value * 0.001  # 10bps spread
            impact_cost = trade_value * trade_value * 1e-7  # Quadratic impact

            total_cost += spread_cost + impact_cost

        return total_cost



