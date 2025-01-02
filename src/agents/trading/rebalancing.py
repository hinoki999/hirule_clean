from dataclasses import dataclass
from typing import Dict, Optional
from decimal import Decimal, ROUND_HALF_UP
import numpy as np
from datetime import datetime, timedelta

@dataclass
class RebalancingTrigger:
    ###"""Configuration for rebalancing triggers###"""
    time_threshold: timedelta = timedelta(days=1)  # Time-based rebalancing
    drift_threshold: float = 0.05  # Position drift trigger
    var_increase_threshold: float = 0.20  # Risk-based trigger
    cost_threshold: float = 0.001  # Maximum acceptable transaction cost

class PortfolioRebalancer:
    ###"""Dynamic portfolio rebalancing system###"""

    def __init__(self, optimizer, trigger_config: Optional[RebalancingTrigger] = None):
        self.optimizer = optimizer
        self.trigger_config = trigger_config or RebalancingTrigger()
        self.last_rebalance = datetime.now()
        self.target_weights = {}

    def check_rebalancing_triggers(self,
                                 current_positions: Dict[str, Decimal],
                                 constraints) -> tuple[bool, str]:
        ###"""Check if rebalancing is needed###"""
        now = datetime.now()

        # Time-based check
        if now - self.last_rebalance > self.trigger_config.time_threshold:
            return True, "Time threshold exceeded"

        # Calculate current weights
        total_value = sum(float(pos * Decimal(str(
            self.optimizer.risk_manager.price_history[sym][-1])))
            for sym, pos in current_positions.items())

        current_weights = {
            sym: float(pos * Decimal(str(
                self.optimizer.risk_manager.price_history[sym][-1]))) / total_value
            for sym, pos in current_positions.items()
        }

        # Check position drift
        if self.target_weights:
            max_drift = max(
                abs(current_weights.get(sym, 0) - self.target_weights.get(sym, 0))
                for sym in set(current_weights) | set(self.target_weights)
            )
            if max_drift > self.trigger_config.drift_threshold:
                return True, f"Position drift of {max_drift:.1%} exceeds threshold"

        # Risk-based check
        base_var = self.optimizer.risk_manager.calculate_portfolio_var(current_positions)
        stress_results = self.optimizer.stress_tester.monte_carlo_stress_test(current_positions)

        if stress_results["var_99"] > base_var * (1 + self.trigger_config.var_increase_threshold):
            return True, "Risk increase exceeds threshold"

        return False, ""

    def get_optimal_trades(self,
                          current_positions: Dict[str, Decimal],
                          constraints,
                          optimization_goal: str = 'sharpe') -> Dict[str, Decimal]:
        ###"""Get optimal trades considering transaction costs###"""
        # Get initial optimization result
        result = self.optimizer.optimize_portfolio(
            current_positions, constraints, optimization_goal)

        # Store target weights for drift monitoring
        total_value = sum(float(pos * Decimal(str(
            self.optimizer.risk_manager.price_history[sym][-1])))
            for sym, pos in result.optimal_positions.items())

        self.target_weights = {
            sym: float(pos * Decimal(str(
                self.optimizer.risk_manager.price_history[sym][-1]))) / total_value
            for sym, pos in result.optimal_positions.items()
        }

        # Calculate initial trades
        trades = self.optimizer.get_rebalancing_trades(
            current_positions, result.optimal_positions)

        # Check transaction costs
        cost = self.optimizer.calculate_transition_cost(trades)
        portfolio_value = sum(float(pos * Decimal(str(
            self.optimizer.risk_manager.price_history[sym][-1])))
            for sym, pos in current_positions.items())

        cost_ratio = cost / portfolio_value

        if cost_ratio > self.trigger_config.cost_threshold:
            # Scale down trades to meet cost threshold
            scale_factor = self.trigger_config.cost_threshold / cost_ratio
            reduced_trades = {}

            for symbol, trade_size in trades.items():
                # Apply square root scaling to better preserve priority of larger trades
                reduced_size = trade_size * Decimal(str(np.sqrt(scale_factor)))
                # Round to 8 decimal places
                reduced_size = reduced_size.quantize(Decimal('0.00000001'), rounding=ROUND_HALF_UP)
                if abs(reduced_size) >= Decimal('0.00000001'):  # Minimum trade size
                    reduced_trades[symbol] = reduced_size

            # Verify new costs
            new_cost = self.optimizer.calculate_transition_cost(reduced_trades)
            if new_cost / portfolio_value <= self.trigger_config.cost_threshold:
                return reduced_trades

            # If still too expensive, try sequential optimization
            final_trades = {}
            remaining_cost = self.trigger_config.cost_threshold * portfolio_value

            # Sort trades by importance (size relative to position)
            sorted_trades = sorted(
                trades.items(),
                key=lambda x: abs(float(x[1])) / float(current_positions[x[0]]),
                reverse=True
            )

            for symbol, trade_size in sorted_trades:
                test_trade = {symbol: trade_size}
                trade_cost = self.optimizer.calculate_transition_cost(test_trade)

                if trade_cost <= remaining_cost:
                    final_trades[symbol] = trade_size
                    remaining_cost -= trade_cost
                else:
                    # Scale down this trade to use remaining cost
                    scale = remaining_cost / trade_cost
                    scaled_size = trade_size * Decimal(str(scale))
                    scaled_size = scaled_size.quantize(Decimal('0.00000001'), rounding=ROUND_HALF_UP)
                    if abs(scaled_size) >= Decimal('0.00000001'):
                        final_trades[symbol] = scaled_size
                    break

            return final_trades

        return trades



