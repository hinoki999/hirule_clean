from typing import Dict
import numpy as np

class MarketRegimeDetector:
    def __init__(self, config: Dict):
        self.volatility_window = config.get("volatility_window", 20)
        self.volume_window = config.get("volume_window", 20)
        self.price_change_threshold = config.get("price_change_threshold", 0.02)
        self.volume_change_threshold = config.get("volume_change_threshold", 0.5)
        self.price_history = {}
        self.volume_history = {}
        
    def detect_regime(self, price: float, volume: float, symbol: str) -> str:
        """Detect current market regime based on price and volume data"""
        if symbol not in self.price_history:
            self.price_history[symbol] = []
            self.volume_history[symbol] = []
            
        self.price_history[symbol].append(price)
        self.volume_history[symbol].append(volume)
        
        # Keep only window size
        self.price_history[symbol] = self.price_history[symbol][-self.volatility_window:]
        self.volume_history[symbol] = self.volume_history[symbol][-self.volume_window:]
        
        # Need enough history
        if len(self.price_history[symbol]) < self.volatility_window:
            return "normal"
            
        # Calculate metrics
        volatility = self._calculate_volatility(symbol)
        volume_change = self._calculate_volume_change(symbol)
        trend = self._calculate_trend(symbol)
        
        # Determine regime
        if volatility > self.price_change_threshold:
            return "high_volatility"
        elif volume_change < -self.volume_change_threshold:
            return "low_volume"
        elif abs(trend) > self.price_change_threshold:
            return "trending"
        else:
            return "normal"
            
    def _calculate_volatility(self, symbol: str) -> float:
        prices = np.array(self.price_history[symbol])
        returns = np.diff(prices) / prices[:-1]
        return np.std(returns)
        
    def _calculate_volume_change(self, symbol: str) -> float:
        volumes = np.array(self.volume_history[symbol])
        if len(volumes) < 2:
            return 0
        return (volumes[-1] - volumes[0]) / volumes[0]
        
    def _calculate_trend(self, symbol: str) -> float:
        prices = np.array(self.price_history[symbol])
        return (prices[-1] - prices[0]) / prices[0]
