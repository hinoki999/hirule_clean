from datetime import datetime
from decimal import Decimal
from typing import Dict
from src.agents.trading.messages import MarketData

def create_market_data(symbol: str, price: float) -> MarketData:
    """Create test market data"""
    return MarketData(
        symbol=symbol,
        price=Decimal(str(price)),
        timestamp=datetime.now().timestamp(),
        bid=Decimal(str(price - 0.5)),
        ask=Decimal(str(price + 0.5)),
        volume=Decimal("1.0")
    )

def create_risk_limits() -> Dict:
    """Create test risk limits configuration"""
    return {
        "position_limits": {
            "BTC/USD": Decimal("1.0"),  # Max 1 BTC position
            "ETH/USD": Decimal("10.0")   # Max 10 ETH position
        },
        "notional_limits": {
            "BTC/USD": Decimal("50000"),  # Max $50k notional
            "ETH/USD": Decimal("20000")   # Max $20k notional
        },
        "risk_metrics": {
            "max_drawdown": Decimal("0.1"),      # 10% max drawdown
            "max_leverage": Decimal("2.0"),      # 2x max leverage
            "var_limit": Decimal("0.05"),        # 5% VaR limit
            "correlation_limit": Decimal("0.7")   # 0.7 correlation limit
        },
        "volatility_scaling": {
            "enabled": True,
            "target_vol": Decimal("0.2"),        # 20% target volatility
            "max_scale": Decimal("2.0")          # Maximum 2x scaling
        }
    }
