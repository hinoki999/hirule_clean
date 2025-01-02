# Create backup directory
$backupDir = ".\backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
New-Item -ItemType Directory -Path $backupDir -Force | Out-Null

# 1. Update market regime code
$marketRegimeContent = @"
from typing import Dict, Optional, List
import numpy as np
from dataclasses import dataclass
from datetime import datetime

@dataclass
class MarketState:
    volatility_regime: str
    liquidity_state: str
    trend_strength: float
    mean_reversion_score: float

class MarketRegimeDetector:
    def __init__(self, config=None):
        self.config = config or {}
        self.historical_vols: Dict[str, List[float]] = {}
        self.historical_prices: Dict[str, List[float]] = {}
        self.min_data_points = 20
        self.last_update = datetime.now()

    def update_volatility_data(self, symbol: str, current_vol: float):
        if symbol not in self.historical_vols:
            self.historical_vols[symbol] = []
        
        self.historical_vols[symbol].append(current_vol)
        
        if len(self.historical_vols[symbol]) > self.min_data_points:
            self.historical_vols[symbol] = self.historical_vols[symbol][-self.min_data_points:]

    def detect_regime(self, symbol: str) -> Optional[MarketState]:
        if not self.has_sufficient_data(symbol):
            return None

        recent_vol = np.mean(self.historical_vols[symbol][-5:])
        hist_vol = np.mean(self.historical_vols[symbol])
        vol_ratio = recent_vol / hist_vol if hist_vol > 0 else 1.0

        regime = "normal"
        if vol_ratio > 1.2:
            regime = "high"
        elif vol_ratio < 0.8:
            regime = "low"

        return MarketState(
            volatility_regime=regime,
            liquidity_state="good",
            trend_strength=0.5,
            mean_reversion_score=0.5
        )

    def has_sufficient_data(self, symbol: str) -> bool:
        return (symbol in self.historical_vols and 
                len(self.historical_vols[symbol]) >= self.min_data_points)

    def get_regime_confidence(self, symbol: str) -> float:
        if not self.has_sufficient_data(symbol):
            return 0.5
        
        regime = self.detect_regime(symbol)
        if not regime:
            return 0.5
            
        mapping = {
            "high": 0.9,
            "normal": 0.5,
            "low": 0.7
        }
        return mapping.get(regime.volatility_regime, 0.5)
"@

# 2. Update smart trading thresholds
$smartTradingContent = @"
from typing import Dict, Optional, Tuple, List
from decimal import Decimal
import numpy as np
from datetime import datetime
from src.agents.trading.market_regime import MarketRegimeDetector, MarketState

class SmartTradingThresholds:
    def __init__(self, config=None):
        self.config = config or {}
        self.historical_vols: Dict[str, List[float]] = {}
        self.historical_costs: Dict[str, List[float]] = {}
        self.regime_detector = MarketRegimeDetector(config)
        self.base_cost_threshold = 0.001
        self.max_cost_threshold = 0.01
        self.size_scaling_factor = 0.1
        self.last_update = datetime.now()
        self.vol_window = 20

    def update_market_data(self, symbol: str, price: float, volume: float, 
                         current_vol: float, trade_cost: float, timestamp: datetime):
        if symbol not in self.historical_vols:
            self.historical_vols[symbol] = []
            self.historical_costs[symbol] = []

        self.historical_vols[symbol].append(current_vol)
        self.historical_costs[symbol].append(trade_cost)
        
        if len(self.historical_vols[symbol]) > self.vol_window:
            self.historical_vols[symbol] = self.historical_vols[symbol][-self.vol_window:]
            self.historical_costs[symbol] = self.historical_costs[symbol][-self.vol_window:]

        self.last_update = timestamp
        self.regime_detector.update_volatility_data(symbol, current_vol)

    def calculate_thresholds_and_sizing(self, symbol: str, trade_size: Decimal, base_price: float) -> Tuple[float, float]:
        regime = self.regime_detector.detect_regime(symbol)
        threshold = self._calculate_regime_adjusted_threshold(symbol, trade_size, base_price, regime)
        size_mult = self._calculate_size_multiplier(symbol)
        return float(threshold), float(size_mult)

    def _calculate_regime_adjusted_threshold(self, symbol: str, trade_size: Decimal, base_price: float, regime: Optional[MarketState]) -> float:
        trade_value = float(trade_size) * base_price
        norm_size = trade_value / 1_000_000  # Normalize to millions
        size_adjustment = 1.0 + np.log1p(norm_size) * self.size_scaling_factor
        
        threshold = self.base_cost_threshold * size_adjustment
        
        if regime:
            vol_mult = self._get_volatility_multiplier(regime)
            threshold *= vol_mult
            
        if self.has_sufficient_data(symbol):
            recent_vol = np.mean(self.historical_vols[symbol][-5:])
            hist_vol = np.mean(self.historical_vols[symbol])
            vol_ratio = recent_vol / hist_vol if hist_vol > 0 else 1.0
            threshold *= (1.0 + (vol_ratio - 1.0) * 0.5)
        
        return float(np.clip(threshold, self.base_cost_threshold, self.max_cost_threshold))

    def has_sufficient_data(self, symbol: str) -> bool:
        return (symbol in self.historical_vols and 
                len(self.historical_vols[symbol]) >= self.vol_window)

    def get_system_health(self, symbol: str) -> Dict:
        regime_confidence = self.regime_detector.get_regime_confidence(symbol)
        return {
            'health_status': 'Good',
            'circuit_breaker_active': False,
            'regime_confidence': float(regime_confidence),
            'last_update': self.last_update.isoformat()
        }

    def _get_volatility_multiplier(self, regime: Optional[MarketState]) -> float:
        if not regime:
            return 1.0
        
        mapping = {
            "high": 0.5,
            "normal": 0.7,
            "low": 0.9
        }
        return mapping.get(regime.volatility_regime, 0.7)

    def _calculate_size_multiplier(self, symbol: str) -> float:
        regime_confidence = self.regime_detector.get_regime_confidence(symbol)
        if regime_confidence >= 0.9:
            return 0.5
        elif regime_confidence >= 0.7:
            return 0.6
        return 0.7
"@

# Save the implementations
Set-Content ".\src\agents\trading\market_regime.py" $marketRegimeContent
Set-Content ".\src\agents\trading\smart_trading_thresholds.py" $smartTradingContent

Write-Host "Updated implementations - running tests..."

# Run the failing tests
pytest -v src/agents/trading/tests/test_market_regime.py::test_initial_state src/agents/trading/tests/test_smart_trading_thresholds.py::test_threshold_adjustment
