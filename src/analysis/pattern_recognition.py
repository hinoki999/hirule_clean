from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import numpy as np
from ..core.types import MarketData

@dataclass
class Pattern:
    type: str
    confidence: float
    timestamp: float
    indicators: Dict[str, float]
    support_level: Optional[float] = None
    resistance_level: Optional[float] = None

class PatternRecognizer:
    def __init__(self, window_size: int = 20):
        self.window_size = window_size
        self.patterns = {
            'trend_reversal': self._identify_trend_reversal,
            'breakout': self._identify_breakout,
            'consolidation': self._identify_consolidation
        }

    def identify_patterns(self, data: MarketData) -> List[Pattern]:
        """Identify all possible patterns in the market data"""
        patterns = []
        for pattern_type, pattern_func in self.patterns.items():
            if pattern := pattern_func(data):
                patterns.append(pattern)
        return patterns

    def _calculate_indicators(self, data: MarketData) -> Dict[str, float]:
        """Calculate technical indicators for pattern recognition"""
        prices = np.array(data.price_history[-self.window_size:])
        returns = np.diff(prices) / prices[:-1]
        
        return {
            'volatility': float(np.std(returns)),
            'momentum': float(prices[-1] - prices[0]) / float(prices[0]),
            'rsi': self._calculate_rsi(prices),
            'volume_change': self._calculate_volume_change(data)
        }

    def _identify_trend_reversal(self, data: MarketData) -> Optional[Pattern]:
        """Identify potential trend reversal patterns"""
        indicators = self._calculate_indicators(data)
        
        # Check for reversal conditions
        is_reversal = (
            (indicators['rsi'] > 70 and indicators['momentum'] < 0) or
            (indicators['rsi'] < 30 and indicators['momentum'] > 0)
        )
        
        if is_reversal:
            confidence = min(abs(indicators['momentum']) * 2, 1.0)
            return Pattern(
                type='trend_reversal',
                confidence=confidence,
                timestamp=data.timestamp,
                indicators=indicators
            )
        return None

    def _identify_breakout(self, data: MarketData) -> Optional[Pattern]:
        """Identify breakout patterns"""
        indicators = self._calculate_indicators(data)
        prices = np.array(data.price_history[-self.window_size:])
        
        # Calculate support and resistance
        resistance = float(np.max(prices[:-1]))
        support = float(np.min(prices[:-1]))
        current_price = float(prices[-1])
        
        # Check for breakout conditions
        is_breakout = (
            (current_price > resistance and indicators['volume_change'] > 0.5) or
            (current_price < support and indicators['volume_change'] > 0.5)
        )
        
        if is_breakout:
            confidence = min(indicators['volume_change'], 1.0)
            return Pattern(
                type='breakout',
                confidence=confidence,
                timestamp=data.timestamp,
                indicators=indicators,
                support_level=support,
                resistance_level=resistance
            )
        return None

    def _identify_consolidation(self, data: MarketData) -> Optional[Pattern]:
        """Identify consolidation patterns"""
        indicators = self._calculate_indicators(data)
        
        # Check for consolidation conditions
        is_consolidation = (
            indicators['volatility'] < 0.02 and
            abs(indicators['momentum']) < 0.01
        )
        
        if is_consolidation:
            confidence = 1.0 - indicators['volatility'] * 10
            return Pattern(
                type='consolidation',
                confidence=confidence,
                timestamp=data.timestamp,
                indicators=indicators
            )
        return None

    def _calculate_rsi(self, prices: np.ndarray, period: int = 14) -> float:
        """Calculate Relative Strength Index"""
        deltas = np.diff(prices)
        gain = np.where(deltas > 0, deltas, 0)
        loss = np.where(deltas < 0, -deltas, 0)
        
        avg_gain = np.mean(gain)
        avg_loss = np.mean(loss)
        
        if avg_loss == 0:
            return 100.0
        
        rs = avg_gain / avg_loss
        return float(100 - (100 / (1 + rs)))

    def _calculate_volume_change(self, data: MarketData) -> float:
        """Calculate volume change ratio"""
        if not data.volume_history or len(data.volume_history) < 2:
            return 0.0
            
        current_volume = data.volume_history[-1]
        prev_volume = np.mean(data.volume_history[-self.window_size:-1])
        
        if prev_volume == 0:
            return 0.0
            
        return float((current_volume - prev_volume) / prev_volume)