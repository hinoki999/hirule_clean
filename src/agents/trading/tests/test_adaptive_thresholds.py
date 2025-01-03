import pytest
from decimal import Decimal
import numpy as np
from datetime import datetime, timedelta
from src.agents.trading.adaptive_thresholds import AdaptiveThresholds, ThresholdConfig

@pytest.fixture
def setup_thresholds():
    ###"""Create adaptive thresholds with test configuration###"""
    config = ThresholdConfig(
        base_cost_threshold=0.001,
        max_cost_threshold=0.01,
        vol_scaling_factor=2.0,
        size_scaling_factor=1.5,
        min_samples=20,
        vol_window=20
    )
    return AdaptiveThresholds(config)

def test_initial_threshold(setup_thresholds):
    ###"""Test initial threshold calculation###"""
    thresholds = setup_thresholds

    threshold = thresholds.calculate_adaptive_threshold(
        symbol="BTC/USD",
        trade_size=Decimal("1.0"),
        base_price=50000.0
    )

    assert threshold == 0.001, "Should return base threshold without data"

def test_volatility_scaling(setup_thresholds):
    ###"""Test threshold scaling with volatility###"""
    thresholds = setup_thresholds

    # Add some historical data
    for _ in range(25):
        thresholds.update_market_data(
            symbol="BTC/USD",
            current_vol=0.02,
            trade_cost=0.001
        )

    # Test with higher volatility
    threshold = thresholds.calculate_adaptive_threshold(
        symbol="BTC/USD",
        trade_size=Decimal("1.0"),
        base_price=50000.0,
        current_vol=0.04  # 2x historical
    )

    assert threshold > 0.001, "Should increase threshold with higher volatility"
    assert threshold <= 0.01, "Should not exceed maximum threshold"

def test_size_scaling(setup_thresholds):
    ###"""Test threshold scaling with trade size###"""
    thresholds = setup_thresholds

    # Add historical data
    for _ in range(25):
        thresholds.update_market_data(
            symbol="BTC/USD",
            current_vol=0.02,
            trade_cost=0.001
        )

    # Test with different sizes
    small_trade = thresholds.calculate_adaptive_threshold(
        symbol="BTC/USD",
        trade_size=Decimal("0.1"),
        base_price=50000.0
    )

    large_trade = thresholds.calculate_adaptive_threshold(
        symbol="BTC/USD",
        trade_size=Decimal("10.0"),
        base_price=50000.0
    )

    assert large_trade > small_trade, "Should increase threshold for larger trades"

def test_market_stress(setup_thresholds):
    ###"""Test market stress detection###"""
    thresholds = setup_thresholds

    # Add calm market data
    for _ in range(15):
        thresholds.update_market_data(
            symbol="BTC/USD",
            current_vol=0.02,
            trade_cost=0.001
        )

    # Add stressed market data
    for _ in range(5):
        thresholds.update_market_data(
            symbol="BTC/USD",
            current_vol=0.06,
            trade_cost=0.002
        )

    stress = thresholds.get_market_stress_level("BTC/USD")
    assert stress > 0.5, "Should detect increased market stress"
    assert thresholds.should_adjust_thresholds("BTC/USD"), "Should recommend threshold adjustment"
def test_dynamic_scaling_adjustment(setup_thresholds):
    ###"""Test dynamic adjustment of scaling factors###"""
    thresholds = setup_thresholds

    # Initial state with some history
    for _ in range(20):
        thresholds.update_market_data(
            symbol="BTC/USD",
            current_vol=0.02,
            trade_cost=0.001
        )

    initial_threshold = thresholds.calculate_adaptive_threshold(
        symbol="BTC/USD",
        trade_size=Decimal("1.0"),
        base_price=50000.0
    )

    # Simulate consistent underprediction
    for _ in range(10):
        thresholds.update_prediction_accuracy(
            symbol="BTC/USD",
            predicted_cost=0.001,
            actual_cost=0.0015  # 50% higher
        )

    adjusted_threshold = thresholds.calculate_adaptive_threshold(
        symbol="BTC/USD",
        trade_size=Decimal("1.0"),
        base_price=50000.0
    )

    assert adjusted_threshold > initial_threshold, "Should increase threshold after consistent underprediction"

def test_scaling_bounds(setup_thresholds):
    ###"""Test that scaling factors stay within bounds###"""
    thresholds = setup_thresholds

    # Add market data
    for _ in range(20):
        thresholds.update_market_data(
            symbol="BTC/USD",
            current_vol=0.02,
            trade_cost=0.001
        )

    # Try to push scaling factors to extremes
    for _ in range(20):
        thresholds.update_prediction_accuracy(
            symbol="BTC/USD",
            predicted_cost=0.0001,
            actual_cost=0.01  # Large underprediction
        )

    # Check threshold remains within config bounds
    threshold = thresholds.calculate_adaptive_threshold(
        symbol="BTC/USD",
        trade_size=Decimal("1.0"),
        base_price=50000.0
    )

    assert threshold <= thresholds.config.max_cost_threshold, "Should not exceed maximum threshold"
    assert threshold >= thresholds.config.base_cost_threshold, "Should not fall below base threshold"

def test_error_tracking(setup_thresholds):
    ###"""Test prediction error tracking and analysis###"""
    thresholds = setup_thresholds

    # Add some prediction history
    for i in range(15):
        error = 0.0002 if i < 10 else 0.0004  # Sudden increase in errors
        thresholds.update_prediction_accuracy(
            symbol="BTC/USD",
            predicted_cost=0.001,
            actual_cost=0.001 + error
        )

    # Check that scaling factors were adjusted
    symbol = "BTC/USD"
    assert thresholds.scaling_adjustments[symbol]['vol'] > 1.0, "Should increase vol scaling after error pattern"


