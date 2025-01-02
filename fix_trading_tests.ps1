# 1. Add MarketRegime class
$marketRegimeContent = @"
from typing import Optional
import numpy as np
from dataclasses import dataclass

@dataclass
class MarketState:
    volatility_regime: str
    liquidity_state: str
    trend_strength: float
    mean_reversion_score: float

class MarketRegimeDetector:
    def __init__(self, config):
        self.config = config
        self.historical_vols = {}
        self.min_data_points = 20
        
    def detect_regime(self, symbol: str) -> Optional[MarketState]:
        if symbol not in self.historical_vols or len(self.historical_vols[symbol]) < self.min_data_points:
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
    
    def get_regime_confidence(self, symbol: str) -> float:
        regime = self.detect_regime(symbol)
        if not regime:
            return 0.0
            
        confidence_mapping = {
            "high": 0.9,
            "normal": 0.5,
            "low": 0.7
        }
        return confidence_mapping.get(regime.volatility_regime, 0.5)
"@
Set-Content ".\src\agents\trading\market_regime.py" $marketRegimeContent

# 2. Add SmartTradingThresholds class
$thresholdsContent = @"
from typing import Dict, Optional, Tuple
from decimal import Decimal
import numpy as np
from src.agents.trading.market_regime import MarketRegimeDetector, MarketState

class SmartTradingThresholds:
    def __init__(self, config=None):
        self.config = config or {}
        self.historical_vols = {}
        self.regime_detector = MarketRegimeDetector(config)
        self.base_cost_threshold = 0.001
        self.max_cost_threshold = 0.01
        self.size_scaling_factor = 0.1
        
    def calculate_thresholds_and_sizing(self, symbol: str, trade_size: Decimal, base_price: float) -> Tuple[float, float]:
        regime = self.regime_detector.detect_regime(symbol)
        threshold = self._calculate_regime_adjusted_threshold(symbol, trade_size, base_price, regime)
        size_mult = self._calculate_size_multiplier(symbol)
        return threshold, size_mult
        
    def _calculate_regime_adjusted_threshold(self, symbol: str, trade_size: Decimal, base_price: float, regime: Optional[MarketState]) -> float:
        if not regime:
            return self.base_cost_threshold
            
        trade_value = float(trade_size) * base_price
        norm_size = trade_value / 1_000_000
        size_adjustment = 1.0 + np.log1p(norm_size) * self.size_scaling_factor
        
        threshold = self.base_cost_threshold * size_adjustment
        return float(np.clip(threshold, self.base_cost_threshold, self.max_cost_threshold))
        
    def _calculate_size_multiplier(self, symbol: str) -> float:
        regime_confidence = self.regime_detector.get_regime_confidence(symbol)
        if regime_confidence >= 0.9:
            return 0.5
        elif regime_confidence >= 0.7:
            return 0.6
        return 0.7
"@
Set-Content ".\src\agents\trading\smart_trading_thresholds.py" $thresholdsContent

# 3. Add market regime test
$marketRegimeTestContent = @"
import pytest
import asyncio
from datetime import datetime
from decimal import Decimal
from src.agents.trading.market_regime import MarketRegimeDetector

@pytest.mark.asyncio
async def test_initial_state(trading_agent):
    symbol = "BTC/USD"
    
    # Provide 20 data points for regime detection
    for _ in range(20):
        await trading_agent.process_message({
            "type": "MARKET_DATA",
            "payload": {
                "symbol": symbol,
                "last_price": 50000.0,
                "volume": 1000.0,
                "cost": 0.001,
                "timestamp": datetime.now()
            }
        })
    
    # Allow processing time
    await asyncio.sleep(0.1)
    
    regime = trading_agent.regime_detector.detect_regime(symbol)
    assert regime is not None
    assert regime.volatility_regime == "normal"
    assert regime.liquidity_state == "good"
    assert trading_agent.regime_detector.get_regime_confidence(symbol) == 0.5
"@
Set-Content ".\src\agents\trading\tests\test_market_regime.py" $marketRegimeTestContent

# 4. Add smart trading thresholds test
$thresholdsTestContent = @"
import pytest
import asyncio
from decimal import Decimal
from datetime import datetime
from src.agents.trading.smart_trading_thresholds import SmartTradingThresholds

@pytest.mark.asyncio
async def test_threshold_adjustment(trading_agent):
    symbol = "BTC/USD"
    trade_size = Decimal("1000.0")
    base_price = 50000.0
    
    # Initialize with required data points
    for _ in range(20):
        await trading_agent.process_message({
            "type": "MARKET_DATA",
            "payload": {
                "symbol": symbol,
                "last_price": base_price,
                "volume": 1000.0,
                "cost": 0.001,
                "timestamp": datetime.now()
            }
        })
    
    # Calculate thresholds and sizing
    threshold, size_mult = trading_agent.trading_thresholds.calculate_thresholds_and_sizing(
        symbol, trade_size, base_price
    )
    
    # Verify calculated values
    # Size multiplier should be 0.7 for normal regime
    assert size_mult == pytest.approx(0.7, rel=1e-4)
    
    # Threshold should be adjusted for trade size
    expected_threshold = 0.006897738449086488
    assert threshold == pytest.approx(expected_threshold, rel=1e-4)
"@
Set-Content ".\src\agents\trading\tests\test_smart_trading_thresholds.py" $thresholdsTestContent

# Run all tests
Write-Host "`nRunning all tests...`n"
pytest -v src/agents/trading/tests/
