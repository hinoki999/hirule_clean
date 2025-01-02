from dataclasses import dataclass
from typing import Dict, Optional, Tuple
from decimal import Decimal
import numpy as np
from datetime import datetime
from .market_regime import MarketRegimeDetector, MarketState

@dataclass
class SmartThresholdConfig:
    base_cost_threshold: float = 0.001
    max_cost_threshold: float = 0.01
    vol_scaling_factor: float = 2.0
    size_scaling_factor: float = 1.5
    min_samples: int = 20
    vol_window: int = 20
    max_position_multiplier: float = 2.0
    min_position_multiplier: float = 0.2
    circuit_breaker_threshold: float = 0.7

class SmartTradingThresholds:
    def __init__(self, config: Optional[SmartThresholdConfig] = None):
        self.config = config or SmartThresholdConfig()
        self.regime_detector = MarketRegimeDetector(lookback_window=self.config.vol_window)
        self.historical_vols: Dict[str, list] = {}
        self.historical_costs: Dict[str, list] = {}
        self.last_update = datetime.now()
        self.circuit_breakers: Dict[str, bool] = {}
        self.initial_thresholds: Dict[str, float] = {}
        self.normal_regime_multipliers: Dict[str, float] = {}
        self.base_multipliers: Dict[str, float] = {}

    def update_market_data(self, symbol: str, price: float, volume: float,
                          current_vol: float, trade_cost: float,
                          timestamp: Optional[datetime] = None) -> None:
        timestamp = timestamp or datetime.now()

        self.regime_detector.update_market_data(symbol, price, volume)

        if symbol not in self.historical_vols:
            self.historical_vols[symbol] = []
            self.historical_costs[symbol] = []
            self.initial_thresholds[symbol] = self.config.base_cost_threshold
            self.normal_regime_multipliers[symbol] = 0.8
            self.base_multipliers[symbol] = 0.8

        self.historical_vols[symbol].append(current_vol)
        self.historical_costs[symbol].append(trade_cost)

        if len(self.historical_vols[symbol]) > self.config.vol_window:
            self.historical_vols[symbol] = self.historical_vols[symbol][-self.config.vol_window:]
            self.historical_costs[symbol] = self.historical_costs[symbol][-self.config.vol_window:]

        if len(self.historical_vols[symbol]) >= 5:
            recent_vol = np.mean(self.historical_vols[symbol][-5:])
            base_vol = np.mean(self.historical_vols[symbol])
            if base_vol > 0:
                vol_ratio = recent_vol / base_vol
                self.normal_regime_multipliers[symbol] = 0.8 * np.exp(-max(0, vol_ratio - 1.0))

        self.last_update = timestamp
        self._update_circuit_breaker(symbol)

    def _calculate_position_multiplier(self, symbol: str, regime: MarketState) -> float:
        if not regime or not self._has_sufficient_data(symbol):
            return 1.0

        if symbol not in self.historical_vols or len(self.historical_vols[symbol]) < 5:
            return 0.8  # Conservative default

        recent_vol = np.mean(self.historical_vols[symbol][-5:])
        base_vol = np.mean(self.historical_vols[symbol])
        vol_ratio = recent_vol / base_vol if base_vol > 0 else 1.0

        # Base multiplier with strong volatility response
        if regime.volatility_regime == "high" or vol_ratio > 1.5:
            multiplier = 0.4  # Strong reduction for high volatility
        elif regime.volatility_regime == "normal":
            multiplier = 0.7  # Conservative normal regime
        else:
            multiplier = 0.8  # Cap even low volatility

        # Apply exponential decay for volatility
        vol_scale = np.exp(-2 * max(0, vol_ratio - 1.0))  # Stronger decay
        multiplier *= vol_scale

        # Secondary adjustments
        if regime.liquidity_state == "scarce":
            multiplier *= 0.8

        # Strict cap based on volatility regime
        if regime.volatility_regime == "high":
            normal_mult = self.normal_regime_multipliers.get(symbol, 0.8)
            max_allowed = normal_mult * 0.6  # At least 40% reduction
            multiplier = min(multiplier, max_allowed)

        # Final scaling and bounds
        return float(np.clip(multiplier,
                           self.config.min_position_multiplier,
                           self.config.max_position_multiplier))

    def calculate_thresholds_and_sizing(self, symbol: str, trade_size: Decimal, base_price: float) -> Tuple[float, float]:
        if not self._has_sufficient_data(symbol):
    if not self._has_sufficient_data(symbol):
        return self.config.base_cost_threshold, 1.0
            return self.config.base_cost_threshold, 1.0

        if self._is_circuit_breaker_active(symbol):
            return self.config.max_cost_threshold, self.config.min_position_multiplier

        regime = self.regime_detector.detect_regime(symbol)
        threshold = self._calculate_regime_adjusted_threshold(symbol, trade_size, base_price, regime)
        size_mult = self._calculate_position_multiplier(symbol, regime)

        return threshold, size_mult

    # [Rest of the implementation remains the same as before]

        def _get_volatility_multiplier(self, regime: MarketState) -> float:
        if regime.volatility_regime == 'low':
            return 0.7
        elif regime.volatility_regime == 'high':
            return 1.8
        return 1.0


        def _has_sufficient_data(self, symbol: str) -> bool:
        return (symbol in self.historical_vols and
                len(self.historical_vols[symbol]) >= self.config.min_samples)


        def _update_circuit_breaker(self, symbol: str) -> None:
        if len(self.historical_vols[symbol]) < 5:
            self.circuit_breakers[symbol] = False
            return

        recent_vol = np.mean(self.historical_vols[symbol][-5:])
        avg_vol = np.mean(self.historical_vols[symbol])
        vol_ratio = recent_vol / avg_vol if avg_vol > 0 else 1.0

        market_stress = self.regime_detector.get_market_stress_level(symbol)

        self.circuit_breakers[symbol] = (
            market_stress > self.config.circuit_breaker_threshold or
            vol_ratio > 2.0
        )


        def _calculate_regime_adjusted_threshold(self, symbol: str,
                                          trade_size: Decimal,
                                          base_price: float,
                                          regime: MarketState) -> float:
        base_threshold = self.initial_thresholds.get(symbol, self.config.base_cost_threshold)

        if not self.historical_vols.get(symbol):
            return base_threshold

        recent_vol = np.mean(self.historical_vols[symbol][-5:])
        hist_vol = np.mean(self.historical_vols[symbol])
        vol_ratio = recent_vol / hist_vol if hist_vol > 0 else 1.0

        vol_adjustment = vol_ratio * self._get_volatility_multiplier(regime)

        trade_value = float(trade_size) * base_price
        norm_size = trade_value / 1_000_000
        size_adjustment = 1.0 + np.log1p(norm_size) * self.config.size_scaling_factor

        adaptive_threshold = (base_threshold *
                            vol_adjustment *
                            size_adjustment)

        return float(np.clip(adaptive_threshold,
                           self.config.base_cost_threshold,
                           self.config.max_cost_threshold))


