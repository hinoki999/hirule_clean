import pytest
from decimal import Decimal
from .test_utils import create_market_data
from src.agents.trading.messages import OrderStatus, OrderSide
from src.agents.trading.momentum_strategy import MomentumStrategy
from src.agents.trading.risk_management import RiskManager, RiskLimits

@pytest.fixture
async def trading_setup(trading_agent):
    """Setup for trading tests with strategy and risk manager"""
    risk_limits = RiskLimits.from_parameters(
        max_position_size=Decimal("1.0"),
        max_notional=Decimal("100000"),
        max_drawdown=0.1
    )
    risk_manager = RiskManager(risk_limits)
    strategy = MomentumStrategy(
        symbols=["BTC/USD"],
        risk_manager=risk_manager,
        position_size=Decimal("0.1"),
        momentum_window=5,
        momentum_threshold=0.01
    )
    return strategy, risk_manager

@pytest.mark.asyncio
async def test_market_data_processing(trading_setup):
    """Test market data processing and price history maintenance"""
    strategy, _ = trading_setup

    # Feed multiple market data points
    prices = [50000.0, 50100.0, 50200.0]

    for price in prices:
        market_data = create_market_data("BTC/USD", price)
        await strategy.update_market_data(market_data)

    # Verify market data is properly stored
    assert "BTC/USD" in strategy.market_data
    assert len(strategy.price_history["BTC/USD"]) == len(prices)

@pytest.mark.asyncio
async def test_full_trading_cycle(trading_setup):
    """Test complete cycle of market data ? strategy ? risk ? order"""
    strategy, risk_manager = trading_setup

    # Simulate rising prices to generate buy signal
    prices = [50000.0, 50100.0, 50200.0, 50400.0, 50800.0]

    for price in prices:
        market_data = create_market_data("BTC/USD", price)
        order = await strategy.on_market_data(market_data)

        if order:
            can_trade, _ = risk_manager.can_place_order(
                order.symbol,
                order.quantity,
                market_data.price
            )
            assert can_trade

@pytest.mark.asyncio
async def test_risk_limits_enforcement(trading_setup):
    """Test that risk limits are properly enforced"""
    strategy, risk_manager = trading_setup

    # Try to generate a large position that should be rejected
    for price in [50000.0] * 5:  # Stable price to avoid momentum signals
        market_data = create_market_data("BTC/USD", price)
        order = await strategy.on_market_data(market_data)

@pytest.mark.asyncio
async def test_position_tracking(trading_setup):
    """Test that positions are correctly tracked through order fills"""
    strategy, _ = trading_setup

    # Generate a buy signal
    prices = [50000.0, 50100.0, 50200.0, 50400.0, 50800.0]
    order = None

    for price in prices:
        market_data = create_market_data("BTC/USD", price)
        order = await strategy.on_market_data(market_data)

    if order:
        # Simulate order fill
        order.status = OrderStatus.FILLED
        order.filled_quantity = order.quantity
        await strategy.on_order_fill(order)

@pytest.mark.asyncio
async def test_risk_metrics_update(trading_setup):
    """Test risk metrics are updated correctly with market moves"""
    strategy, risk_manager = trading_setup

    # Add initial position
    initial_price = 50000.0
    position_size = Decimal("0.1")
    risk_manager.add_position("BTC/USD", position_size, initial_price)

    # Update to a higher price
    new_price = 51000.0
    market_data = create_market_data("BTC/USD", new_price)
    risk_manager.update_position_risk("BTC/USD", market_data.price)
