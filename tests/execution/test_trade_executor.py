import pytest
from datetime import datetime
from unittest.mock import Mock, AsyncMock
from src.execution.trade_executor import TradeExecutor
from src.core.types import TradeSignal

@pytest.fixture
def mock_exchange():
    exchange = Mock()
    # Set up async methods
    exchange.fetch_ticker = AsyncMock()
    exchange.create_market_buy_order = AsyncMock()
    exchange.create_market_sell_order = AsyncMock()
    exchange.fetch_order = AsyncMock()
    exchange.fetch_balance = AsyncMock()
    return exchange

@pytest.fixture
def executor(mock_exchange):
    config = {
        'exchange_id': 'binance',
        'api_key': 'test_key',
        'api_secret': 'test_secret',
        'risk_limits': {
            'max_position_size': 0.1,
            'max_daily_loss': 0.05,
            'min_order_size': 0.001
        }
    }
    executor = TradeExecutor(config)
    executor.exchange = mock_exchange
    return executor

@pytest.mark.asyncio
async def test_execute_buy_trade(executor, mock_exchange):
    # Setup mock responses
    mock_exchange.fetch_ticker.return_value = {'last': 50000.0}
    mock_exchange.fetch_balance.return_value = {
        'free': {'USDT': 100000.0}
    }
    mock_exchange.create_market_buy_order.return_value = {
        'id': 'test_order',
        'status': 'open'
    }

    # Create trade signal
    signal = TradeSignal(
        type='BUY',
        confidence=0.8,
        timestamp=datetime.now().timestamp()
    )

    # Execute trade
    result = await executor.execute_trade(signal, 'BTC/USDT', 0.1)

    # Verify results
    assert result is not None
    assert result['status'] == 'open'
    assert result['signal'].type == 'BUY'
    assert 'risk_metrics' in result

@pytest.mark.asyncio
async def test_risk_limits(executor, mock_exchange):
    # Setup mock responses
    mock_exchange.fetch_ticker.return_value = {'last': 50000.0}
    mock_exchange.fetch_balance.return_value = {
        'free': {'USDT': 10000.0}
    }

    # Create trade signal
    signal = TradeSignal(
        type='BUY',
        confidence=0.8,
        timestamp=datetime.now().timestamp()
    )

    # Test with position size exceeding limits
    result = await executor.execute_trade(signal, 'BTC/USDT', 0.5)  # 50% of balance
    assert result is None

@pytest.mark.asyncio
async def test_close_position(executor, mock_exchange):
    # Setup mock responses
    mock_exchange.fetch_ticker.return_value = {'last': 52000.0}
    mock_exchange.create_market_sell_order.return_value = {
        'id': 'close_order',
        'status': 'closed'
    }

    # Create test position
    position_id = 'test_position'
    executor.position_cache[position_id] = {
        'signal': TradeSignal(type='BUY', confidence=0.8, 
                            timestamp=datetime.now().timestamp()),
        'market': 'BTC/USDT',
        'size': 1.0,
        'entry_price': 50000.0,
        'timestamp': datetime.now().timestamp()
    }

    # Close position
    result = await executor.close_position(position_id)

    # Verify results
    assert result is not None
    assert result['pnl'] > 0  # Should be profitable due to price increase
    assert position_id not in executor.position_cache

@pytest.mark.asyncio
async def test_update_order_status(executor, mock_exchange):
    # Setup mock responses
    mock_exchange.fetch_order.return_value = {
        'id': 'test_order',
        'status': 'closed',
        'filled': 1.0,
        'remaining': 0.0
    }

    # Create test order
    order_id = 'test_order'
    executor.active_orders[order_id] = {
        'order': {'id': order_id},
        'signal': TradeSignal(type='BUY', confidence=0.8, 
                            timestamp=datetime.now().timestamp()),
        'market': 'BTC/USDT',
        'size': 1.0,
        'status': 'open'
    }

    # Update order status
    result = await executor.update_order_status(order_id)

    # Verify results
    assert result is not None
    assert result['status'] == 'closed'
    assert order_id not in executor.active_orders
    assert order_id in executor.position_cache

@pytest.mark.asyncio
async def test_calculate_position_size(executor, mock_exchange):
    # Setup mock responses
    mock_exchange.fetch_balance.return_value = {
        'free': {'USDT': 100000.0}
    }
    
    size = await executor._calculate_position_size(0.1, 50000.0)
    
    # Verify calculated size
    assert size > 0
    assert size <= (100000.0 * 0.1) / 50000.0  # Should not exceed max position size

@pytest.mark.asyncio
async def test_daily_pnl_calculation(executor):
    # Add some test positions with PnL
    executor.position_cache = {
        'pos1': {
            'timestamp': datetime.now().timestamp(),
            'pnl': 1000.0
        },
        'pos2': {
            'timestamp': datetime.now().timestamp(),
            'pnl': -500.0
        }
    }

    daily_pnl = executor._calculate_daily_pnl()
    assert daily_pnl == 500.0  # Net PnL should be 1000 - 500

@pytest.mark.asyncio
async def test_risk_metrics_calculation(executor, mock_exchange):
    # Setup mock responses
    mock_exchange.fetch_balance.return_value = {
        'free': {'USDT': 100000.0}
    }

    metrics = await executor._calculate_risk_metrics(1.0, 50000.0)

    assert 'position_size_ratio' in metrics
    assert 'daily_pnl_ratio' in metrics
    assert 'liquidation_price' in metrics  # Even if not implemented yet
    assert metrics['position_size_ratio'] == 50000.0 / 100000.0  # 0.5 or 50%