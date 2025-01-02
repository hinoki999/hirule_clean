from decimal import Decimal
from typing import Dict, Optional
import numpy as np
from enum import Enum

class MarketState(Enum):
    NORMAL = "NORMAL"
    HIGH_VOLATILITY = "HIGH_VOLATILITY"
    LOW_VOLATILITY = "LOW_VOLATILITY"
    TREND_UP = "TREND_UP"
    TREND_DOWN = "TREND_DOWN"
    UNKNOWN = "UNKNOWN"

class MarketRegimeDetector:
    def __init__(self, config):
        self.config = config
        self.price_history: Dict[str, list] = {}
        self.volatility_history: Dict[str, list] = {}
        self.regime_confidence: Dict[str, float] = {}
        self.current_state: Dict[str, MarketState] = {}

    def update(self, symbol: str, price: float, volume: float = 0):
        if symbol not in self.price_history:
            self.price_history[symbol] = []
            self.volatility_history[symbol] = []
            self.current_state[symbol] = MarketState.UNKNOWN
        
        self.price_history[symbol].append(price)
        if len(self.price_history[symbol]) > self.config.vol_window:
            self.price_history[symbol].pop(0)
            
        if len(self.price_history[symbol]) > 1:
            returns = np.diff(np.log(self.price_history[symbol]))
            vol = np.std(returns) * np.sqrt(252)
            self.volatility_history[symbol].append(vol)
            
        self._update_regime_confidence(symbol)

    def _update_regime_confidence(self, symbol: str):
        if len(self.volatility_history.get(symbol, [])) < 2:
            self.regime_confidence[symbol] = 0.5
            self.current_state[symbol] = MarketState.NORMAL
            return
            
        recent_vol = self.volatility_history[symbol][-1]
        historical_vol = np.mean(self.volatility_history[symbol][:-1])
        
        if recent_vol > historical_vol * 1.5:
            self.regime_confidence[symbol] = 0.2  # High vol regime
            self.current_state[symbol] = MarketState.HIGH_VOLATILITY
        elif recent_vol < historical_vol * 0.75:
            self.regime_confidence[symbol] = 0.8  # Low vol regime
            self.current_state[symbol] = MarketState.LOW_VOLATILITY
        else:
            self.regime_confidence[symbol] = 0.5  # Normal regime
            self.current_state[symbol] = MarketState.NORMAL

    def get_regime_confidence(self, symbol: str) -> float:
        return self.regime_confidence.get(symbol, 0.5)

    def get_market_state(self, symbol: str) -> MarketState:
        return self.current_state.get(symbol, MarketState.UNKNOWN)
