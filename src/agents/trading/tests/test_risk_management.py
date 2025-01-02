import pytest
from decimal import Decimal
from src.agents.trading.risk_management import RiskManager, RiskLimits

@pytest.fixture
def risk_manager():
    limits = RiskLimits.from_parameters(
        max_position_size=Decimal("1.0"),
        max_notional=Decimal("100000"),
        max_drawdown=0.1
    )
    return RiskManager(limits)

def test_position_limits(risk_manager):
    """Test position limits enforcement"""
    symbol = "BTC/USD"
    size = Decimal("0.5")
    price = 50000.0
    
    # Add within limits
    risk_manager.add_position(symbol, size, price)
    assert symbol in risk_manager.positions
