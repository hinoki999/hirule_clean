import pytest
import numpy as np
from src.analysis.pattern_recognition import PatternRecognizer
from src.core.types import MarketData

@pytest.fixture
def pattern_recognizer():
    return PatternRecognizer(window_size=20)

@pytest.fixture
def market_data():
    # Create sample market data
    return MarketData(
        timestamp=1000.0,
        price_history=list(np.linspace(100, 120, 20)),  # Upward trend
        volume_history=list(np.ones(20) * 1000)
    )

def test_trend_reversal_identification(pattern_recognizer, market_data):
    # Modify data to show potential reversal
    market_data.price_history[-5:] = [120, 119, 118, 117, 116]  # Price dropping
    patterns = pattern_recognizer.identify_patterns(market_data)
    
    reversal_patterns = [p for p in patterns if p.type == 'trend_reversal']
    assert len(reversal_patterns) > 0
    assert reversal_patterns[0].confidence > 0

def test_breakout_identification(pattern_recognizer, market_data):
    # Modify data to show breakout
    market_data.price_history[-1] = 130  # Price breaks above range
    market_data.volume_history[-1] = 2000  # Volume spike
    
    patterns = pattern_recognizer.identify_patterns(market_data)
    breakout_patterns = [p for p in patterns if p.type == 'breakout']
    
    assert len(breakout_patterns) > 0
    assert breakout_patterns[0].confidence > 0
    assert breakout_patterns[0].resistance_level < 130

def test_consolidation_identification(pattern_recognizer, market_data):
    # Modify data to show consolidation
    market_data.price_history[-5:] = [110, 109.8, 110.2, 109.9, 110.1]  # Tight range
    
    patterns = pattern_recognizer.identify_patterns(market_data)
    consolidation_patterns = [p for p in patterns if p.type == 'consolidation']
    
    assert len(consolidation_patterns) > 0
    assert consolidation_patterns[0].confidence > 0

def test_rsi_calculation(pattern_recognizer):
    # Test RSI with known values
    prices = np.array([10, 12, 11, 13, 10, 14, 12, 15])
    market_data = MarketData(
        timestamp=1000.0,
        price_history=list(prices),
        volume_history=list(np.ones(8) * 1000)
    )
    
    indicators = pattern_recognizer._calculate_indicators(market_data)
    assert 'rsi' in indicators
    assert 0 <= indicators['rsi'] <= 100

def test_volume_change_calculation(pattern_recognizer):
    # Test volume change with volume spike
    market_data = MarketData(
        timestamp=1000.0,
        price_history=list(np.ones(20) * 100),
        volume_history=list(np.ones(20) * 1000)
    )
    market_data.volume_history[-1] = 2000  # Double volume
    
    indicators = pattern_recognizer._calculate_indicators(market_data)
    assert indicators['volume_change'] > 0.9  # Should be close to 1.0 (100% increase)

def test_pattern_confidence_levels(pattern_recognizer, market_data):
    # Test that confidence levels are reasonable
    patterns = pattern_recognizer.identify_patterns(market_data)
    for pattern in patterns:
        assert 0 <= pattern.confidence <= 1.0

def test_multiple_pattern_detection(pattern_recognizer):
    # Test detection of multiple patterns simultaneously
    prices = list(np.linspace(100, 120, 19)) + [130]  # Breakout at the end
    volumes = list(np.ones(19) * 1000) + [2000]  # Volume spike at breakout
    
    market_data = MarketData(
        timestamp=1000.0,
        price_history=prices,
        volume_history=volumes
    )
    
    patterns = pattern_recognizer.identify_patterns(market_data)
    pattern_types = {p.type for p in patterns}
    
    # Should detect both breakout and trend patterns
    assert len(pattern_types) > 1