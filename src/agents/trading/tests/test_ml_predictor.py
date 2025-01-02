import pytest
from decimal import Decimal
import numpy as np
from datetime import datetime, timedelta
from src.agents.trading.ml_predictor import MLCostPredictor
from src.agents.trading.advanced_risk import AdvancedRiskManager

@pytest.fixture
def predictor_setup():
    ###"""Create predictor and risk manager with sample data###"""
    predictor = MLCostPredictor(lookback_window=50)
    risk_manager = AdvancedRiskManager(lookback_period=50)

    # Generate price data
    np.random.seed(42)
    timestamps = [datetime.now() + timedelta(minutes=i) for i in range(100)]

    returns = np.random.normal(0.0001, 0.02, 100)
    prices = 50000 * np.exp(np.cumsum(returns))

    # Feed data
    for i in range(len(timestamps)):
        risk_manager.update_price_data("BTC/USD", prices[i], timestamps[i])

    return predictor, risk_manager

def test_initial_prediction(predictor_setup):
    ###"""Test initial cost prediction without training###"""
    predictor, risk_manager = predictor_setup

    trade_size = Decimal("1.0")
    cost = predictor.predict_cost(trade_size, "BTC/USD", risk_manager)

    assert cost > 0, "Cost should be positive"
    assert cost < float(trade_size) * 50000 * 0.01, "Cost should be reasonable"

def test_model_training(predictor_setup):
    ###"""Test model training with sample data###"""
    predictor, risk_manager = predictor_setup

    # Record some sample trades
    for i in range(20):
        trade_size = Decimal(str(np.random.uniform(0.1, 2.0)))
        cost = float(trade_size) * 50000 * 0.001 * (1 + np.random.uniform(0, 0.5))
        predictor.record_trade_cost(trade_size, "BTC/USD", cost, risk_manager)

    # Train model
    predictor.train_model()
    assert predictor.is_trained

    # Test prediction
    trade_size = Decimal("1.0")
    cost = predictor.predict_cost(trade_size, "BTC/USD", risk_manager)
    assert cost > 0
    assert predictor.get_model_confidence() > 0

def test_feature_extraction(predictor_setup):
    ###"""Test feature extraction###"""
    predictor, risk_manager = predictor_setup

    trade_size = Decimal("1.0")
    features = predictor._extract_features(
        trade_size, "BTC/USD", risk_manager, datetime.now())

    assert features.trade_size == float(trade_size)
    assert features.trade_notional > 0
    assert 0 <= features.time_of_day <= 24
    assert isinstance(features.is_weekend, bool)

def test_cost_reasonableness(predictor_setup):
    ###"""Test that predictions are reasonable###"""
    predictor, risk_manager = predictor_setup

    # Train with reasonable costs
    for i in range(20):
        trade_size = Decimal(str(np.random.uniform(0.1, 2.0)))
        # Cost between 5-15 bps
        cost = float(trade_size) * 50000 * np.random.uniform(0.0005, 0.0015)
        predictor.record_trade_cost(trade_size, "BTC/USD", cost, risk_manager)

    predictor.train_model()

    # Test various trade sizes
    sizes = [Decimal("0.1"), Decimal("1.0"), Decimal("10.0")]
    for size in sizes:
        cost = predictor.predict_cost(size, "BTC/USD", risk_manager)
        cost_bps = cost / (float(size) * 50000)
        assert 0.00001 <= cost_bps <= 0.01, f"Cost {cost_bps} should be between 0.1-100 bps"


