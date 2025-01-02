from decimal import Decimal
from dataclasses import dataclass
from typing import Dict

@dataclass
class TradingConfigParams:
    vol_window: int = 20
    trend_window: int = 14
    min_trend_strength: float = 0.05

class TradingConfig:
    def __init__(self):
        self.params = TradingConfigParams()
        self.thresholds = TradingThresholds()

@dataclass
class TradingThresholds:
    min_order_size: Decimal = Decimal("0.0001")
    max_order_size: Decimal = Decimal("1.0")
    min_price_increment: Decimal = Decimal("0.01")
    min_notional: Decimal = Decimal("10.0")
    trend_strength: float = 0.05
    momentum_period: int = 14
    volatility_window: int = 20
    config: TradingConfigParams = None

    def __post_init__(self):
        if self.config is None:
            self.config = TradingConfigParams(
                vol_window=self.volatility_window,
                trend_window=self.momentum_period,
                min_trend_strength=self.trend_strength
            )
