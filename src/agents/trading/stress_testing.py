from dataclasses import dataclass
from typing import Dict, List, Optional, Callable
from decimal import Decimal
import numpy as np
from datetime import datetime, timedelta
from .advanced_risk import AdvancedRiskManager

@dataclass
class StressScenario:
    ###"""Definition of a stress testing scenario###"""
    name: str
    price_shocks: Dict[str, float]  # Symbol -> price change %
    volatility_multiplier: float = 1.0
    correlation_adjustment: float = 1.0
    liquidity_factor: float = 1.0
    description: str = ""

class StressTester:
    ###"""Stress testing framework for risk analysis###"""

    def __init__(self, risk_manager: AdvancedRiskManager):
        self.risk_manager = risk_manager
        self.historical_scenarios: Dict[str, StressScenario] = {}
        self._initialize_historical_scenarios()

    def _initialize_historical_scenarios(self):
        ###"""Initialize predefined historical stress scenarios###"""
        self.historical_scenarios = {
            "crypto_crash_2022": StressScenario(
                name="Crypto Crash 2022",
                price_shocks={"BTC/USD": -0.65, "ETH/USD": -0.70},
                volatility_multiplier=3.0,
                correlation_adjustment=1.2,
                liquidity_factor=0.5,
                description="Simulation of 2022 crypto market crash conditions"
            ),
            "extreme_volatility": StressScenario(
                name="Extreme Volatility",
                price_shocks={"BTC/USD": -0.30, "ETH/USD": -0.35},
                volatility_multiplier=5.0,
                correlation_adjustment=1.5,
                liquidity_factor=0.3,
                description="Extreme market volatility scenario"
            ),
            "correlation_breakdown": StressScenario(
                name="Correlation Breakdown",
                price_shocks={"BTC/USD": -0.20, "ETH/USD": 0.15},
                volatility_multiplier=2.0,
                correlation_adjustment=0.2,
                liquidity_factor=0.7,
                description="Scenario where typical correlations break down"
            )
        }

    def run_historical_scenario(self,
                              scenario_name: str,
                              positions: Dict[str, Decimal]) -> Dict[str, float]:
        ###"""Run a predefined historical stress scenario###"""
        if scenario_name not in self.historical_scenarios:
            raise ValueError(f"Unknown scenario: {scenario_name}")

        scenario = self.historical_scenarios[scenario_name]
        return self._run_scenario(scenario, positions)

    def create_custom_scenario(self,
                             name: str,
                             price_shocks: Dict[str, float],
                             **kwargs) -> StressScenario:
        ###"""Create and store a custom stress scenario###"""
        scenario = StressScenario(name=name, price_shocks=price_shocks, **kwargs)
        self.historical_scenarios[name] = scenario
        return scenario

    def _run_scenario(self,
                     scenario: StressScenario,
                     positions: Dict[str, Decimal]) -> Dict[str, float]:
        ###"""Execute a stress scenario and calculate impact###"""
        # Calculate base portfolio metrics
        base_var = self.risk_manager.calculate_portfolio_var(positions)

        # Apply price shocks
        shocked_positions = {}
        total_pnl = 0.0

        for symbol, position in positions.items():
            if symbol in scenario.price_shocks:
                shock = scenario.price_shocks[symbol]
                # Calculate PnL from price shock
                price = float(self.risk_manager.price_history[symbol][-1])
                new_price = price * (1 + shock)
                position_value = float(position * Decimal(str(price)))
                new_value = float(position * Decimal(str(new_price)))
                total_pnl += new_value - position_value

                # Update position for VaR calculation
                shocked_positions[symbol] = position

        # Adjust volatility and correlation in risk manager
        original_lookback = self.risk_manager.lookback_period
        self.risk_manager.lookback_period = min(20, original_lookback)  # Use shorter lookback for stress

        # Calculate stressed VaR
        stressed_var = self.risk_manager.calculate_portfolio_var(shocked_positions)
        stressed_var *= scenario.volatility_multiplier

        # Restore original lookback
        self.risk_manager.lookback_period = original_lookback

        return {
            "scenario_name": scenario.name,
            "total_pnl": total_pnl,
            "base_var": base_var,
            "stressed_var": stressed_var,
            "var_increase": (stressed_var - base_var) / base_var if base_var > 0 else float('inf'),
            "liquidity_impact": (1 - scenario.liquidity_factor) * abs(total_pnl)
        }

    def monte_carlo_stress_test(self,
                              positions: Dict[str, Decimal],
                              n_scenarios: int = 1000,
                              confidence_level: float = 0.99) -> Dict[str, float]:
        ###"""Run Monte Carlo stress testing###"""
        portfolio_values = []
        base_value = 0.0

        # Calculate base portfolio value
        for symbol, position in positions.items():
            price = float(self.risk_manager.price_history[symbol][-1])
            base_value += float(position * Decimal(str(price)))

        # Generate random scenarios
        for _ in range(n_scenarios):
            # Random shocks between -50% and +30%
            shocks = {symbol: np.random.uniform(-0.5, 0.3) for symbol in positions.keys()}

            # Calculate portfolio value under scenario
            scenario_value = 0.0
            for symbol, position in positions.items():
                price = float(self.risk_manager.price_history[symbol][-1])
                new_price = price * (1 + shocks[symbol])
                scenario_value += float(position * Decimal(str(new_price)))

            portfolio_values.append(scenario_value)

        # Calculate stress metrics
        sorted_values = np.sort(portfolio_values)
        worst_index = int((1 - confidence_level) * n_scenarios)

        return {
            "worst_loss": base_value - sorted_values[0],
            "var_99": base_value - sorted_values[worst_index],
            "expected_shortfall": base_value - np.mean(sorted_values[:worst_index]),
            "max_drawdown": (base_value - np.min(sorted_values)) / base_value
        }


