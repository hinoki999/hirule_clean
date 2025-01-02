from dataclasses import dataclass
from typing import Dict, Optional
from decimal import Decimal
import numpy as np
from datetime import datetime, timedelta

@dataclass
class ThresholdConfig:
    ###"""Configuration for adaptive thresholds###"""
    base_cost_threshold: float = 0.001  # Base cost threshold (10 bps)
    max_cost_threshold: float = 0.01    # Maximum cost threshold (100 bps)
    vol_scaling_factor: float = 2.0     # Volatility scaling factor
    size_scaling_factor: float = 1.5    # Trade size scaling factor
    min_samples: int = 50               # Minimum samples for adaptation
    vol_window: int = 20                # Volatility calculation window
    decay_factor: float = 0.94          # Exponential decay factor for historical data

class AdaptiveThresholds:
    def __init__(self, config: Optional[ThresholdConfig] = None):
        self.config = config or ThresholdConfig()
        self.historical_vols: Dict[str, list] = {}
        self.historical_costs: Dict[str, list] = {}
        self.scaling_adjustments: Dict[str, Dict[str, float]] = {}
        self.prediction_errors: Dict[str, list] = {}
        self.last_update = datetime.now()

    def update_market_data(self, symbol: str, current_vol: float, trade_cost: float, timestamp: Optional[datetime] = None):
        timestamp = timestamp or datetime.now()

        if symbol not in self.historical_vols:
            self.historical_vols[symbol] = []
            self.historical_costs[symbol] = []

        self.historical_vols[symbol].append(current_vol)
        self.historical_costs[symbol].append(trade_cost)

        if len(self.historical_vols[symbol]) > self.config.vol_window:
            self.historical_vols[symbol] = self.historical_vols[symbol][-self.config.vol_window:]
            self.historical_costs[symbol] = self.historical_costs[symbol][-self.config.vol_window:]

        self.last_update = timestamp

    def update_prediction_accuracy(self, symbol: str, predicted_cost: float, actual_cost: float, timestamp: Optional[datetime] = None):
        if symbol not in self.prediction_errors:
            self.prediction_errors[symbol] = []
            self.scaling_adjustments[symbol] = {
                'vol': 1.0,
                'size': 1.0
            }

        rel_error = (actual_cost - predicted_cost) / actual_cost if actual_cost != 0 else 0
        self.prediction_errors[symbol].append(rel_error)

        if len(self.prediction_errors[symbol]) > self.config.min_samples:
            self.prediction_errors[symbol] = self.prediction_errors[symbol][-self.config.min_samples:]

        self._adjust_scaling_factors(symbol)

    def _adjust_scaling_factors(self, symbol: str):
        if len(self.prediction_errors[symbol]) < 10:
            return

        recent_errors = self.prediction_errors[symbol][-10:]
        avg_error = np.mean(recent_errors)
        error_std = np.std(recent_errors)

        if abs(avg_error) > 0.1:
            adjustment = 0.2 if avg_error > 0 else -0.1
            self.scaling_adjustments[symbol]['vol'] *= (1 + adjustment)

        if error_std > 0.15:
            self.scaling_adjustments[symbol]['size'] *= 1.15
        elif error_std < 0.05:
            self.scaling_adjustments[symbol]['size'] = max(1.0, self.scaling_adjustments[symbol]['size'] * 0.9)

        self.scaling_adjustments[symbol]['vol'] = np.clip(
            self.scaling_adjustments[symbol]['vol'], 0.5, 2.5)
        self.scaling_adjustments[symbol]['size'] = np.clip(
            self.scaling_adjustments[symbol]['size'], 0.5, 3.0)

    def calculate_adaptive_threshold(self, symbol: str, trade_size: Decimal, base_price: float, current_vol: Optional[float] = None) -> float:
        if not self.historical_vols.get(symbol):
            return self.config.base_cost_threshold

        hist_vol = np.std(self.historical_vols[symbol])
        current_vol = current_vol or hist_vol

        scaling = self.scaling_adjustments.get(symbol, {'vol': 1.0, 'size': 1.0})
        vol_scale = scaling['vol']
        size_scale = scaling['size']

        vol_ratio = current_vol / hist_vol if hist_vol > 0 else 1.0
        vol_adjustment = np.clip(
            vol_ratio * self.config.vol_scaling_factor * vol_scale, 0.5, 2.5)

        trade_value = float(trade_size) * base_price
        norm_size = trade_value / 1_000_000
        size_adjustment = min(
            1.0 + np.log1p(norm_size) * self.config.size_scaling_factor * size_scale, 3.0)

        base_adjustment = 1.0
        if symbol in self.prediction_errors and len(self.prediction_errors[symbol]) > 0:
            recent_bias = np.mean(self.prediction_errors[symbol][-5:])
            base_adjustment = 1.0 + (np.clip(recent_bias, -0.2, 0.4))

        adaptive_threshold = (self.config.base_cost_threshold *
                            vol_adjustment *
                            size_adjustment *
                            base_adjustment)

        return float(np.clip(adaptive_threshold,
                           self.config.base_cost_threshold,
                           self.config.max_cost_threshold))

    def get_market_stress_level(self, symbol: str) -> float:
        if not self.historical_vols.get(symbol):
            return 0.0

        recent_vol = np.mean(self.historical_vols[symbol][-5:])
        long_vol = np.mean(self.historical_vols[symbol])

        stress = min(1.0, recent_vol / long_vol if long_vol > 0 else 0.0)
        return float(stress)

    def should_adjust_thresholds(self, symbol: str) -> bool:
        if symbol not in self.historical_vols:
            return False

        if len(self.historical_vols[symbol]) < self.config.min_samples:
            return False

        stress = self.get_market_stress_level(symbol)
        return stress > 0.5

    def get_threshold_confidence(self, symbol: str) -> float:
        if symbol not in self.historical_vols:
            return 0.0

        data_confidence = min(1.0, len(self.historical_vols[symbol]) / self.config.min_samples)
        market_stability = 1.0 - self.get_market_stress_level(symbol)

        return float(data_confidence * market_stability)


