import pytest
from datetime import datetime, timedelta
from src.agents.trading.positions.models import Position
from src.agents.trading.positions.metrics import MetricsCalculator

@pytest.fixture
def calculator():
    return MetricsCalculator()

@pytest.fixture
def position():
    return Position(
        asset="BTC/USD",
        size=1.0,
        entry_price=50000.0,
        current_price=50000.0,
        timestamp=datetime.now() - timedelta(hours=2),
        stop_loss=49000.0,
        take_profit=51000.0
    )

def test_basic_metrics(calculator, position):
    """Test basic metrics calculations."""
    metrics = calculator.calculate_metrics(position, 51000.0)
    
    assert metrics.asset == "BTC/USD"
    assert metrics.unrealized_pnl == 1000.0  # (51000 - 50000) * 1.0
    assert metrics.exposure == 51000.0  # 1.0 * 51000
    assert metrics.roi == pytest.approx(2.0)  # 2% increase
    assert metrics.holding_period >= 2.0  # At least 2 hours

def test_drawdown_calculation(calculator, position):
    """Test drawdown calculations with price movements."""
    # Price goes up
    calculator.calculate_metrics(position, 52000.0)
    
    # Then down
    metrics = calculator.calculate_metrics(position, 51000.0)
    
    assert metrics.high_price == 52000.0
    assert metrics.low_price == 50000.0  # Original price
    assert metrics.max_drawdown == pytest.approx(1.923, rel=0.01)  # (52000 - 51000) / 52000 * 100

def test_volatility_calculation(calculator, position):
    """Test volatility calculations."""
    prices = [50000.0, 51000.0, 50500.0, 51500.0, 51000.0]
    for price in prices:
        calculator.calculate_metrics(position, price)
    
    volatility = calculator.calculate_volatility(position.asset)
    assert volatility is not None
    assert volatility > 0

def test_metrics_history(calculator, position):
    """Test metrics history tracking."""
    prices = [50000.0, 51000.0, 52000.0]
    for price in prices:
        calculator.calculate_metrics(position, price)
    
    history = calculator.get_metrics_history(position.asset)
    assert len(history) == 3
    assert history[-1].current_price == 52000.0
