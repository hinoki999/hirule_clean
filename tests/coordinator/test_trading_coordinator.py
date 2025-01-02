import pytest
from datetime import datetime
from unittest.mock import Mock, AsyncMock, patch
from src.coordinator.trading_coordinator import TradingCoordinator
from src.core.types import MarketData, TradeSignal
from src.goals.base import Goal, GoalStatus

@pytest.fixture
def config():
    return {
        'exchange': {
            'exchange_id': 'binance',
            'api_key': 'test_key',
            'api_secret': 'test_secret',
            'risk_limits': {
                'max_position_size': 0.1,
                'max_daily_loss': 0.05,
                'min_order_size': 0.001
            }
        },
        'markets': [
            {
                'market': 'BTC/USDT',
                'timeframe': '1h',
                'position_size': 0.1
            },
            {
                'market': 'ETH/USDT',
                'timeframe': '1h',
                'position_size': 0.1
            }
        ]
    }

@pytest.fixture
def mock_trader():
    trader = Mock()
    trader.initialize = AsyncMock()
    trader.process_market_data = AsyncMock()
    trader.generate_trade_signal = AsyncMock()
    trader.update_trade_history = AsyncMock()
    trader.goal_manager = Mock()
    trader.goal_manager.add_goal = AsyncMock()
    trader.goal_manager.get_active_goals = Mock(return_value=[])
    trader.load_context = AsyncMock(return_value={})
    trader.market_patterns = {}
    trader.trade_history = []
    return trader

@pytest.fixture
def mock_executor():
    executor = Mock()
    executor.execute_trade = AsyncMock()
    executor.update_order_status = AsyncMock()
    executor.close_position = AsyncMock()
    executor.position_cache = {}
    return executor

@pytest.fixture
def coordinator(config, mock_trader, mock_executor):
    with patch('src.coordinator.trading_coordinator.GoalEnhancedTrader', 
              return_value=mock_trader):
        with patch('src.coordinator.trading_coordinator.TradeExecutor', 
                  return_value=mock_executor):
            return TradingCoordinator(config)

@pytest.mark.asyncio
async def test_initialization(coordinator, mock_trader):
    await coordinator.initialize()
    
    # Verify each market has a trader initialized
    assert len(coordinator.traders) == 2
    assert 'BTC/USDT' in coordinator.traders
    assert 'ETH/USDT' in coordinator.traders
    
    # Verify traders were initialized
    assert mock_trader.initialize.call_count == 2

@pytest.mark.asyncio
async def test_market_update_processing(coordinator, mock_trader):
    market_data = MarketData(
        timestamp=1000.0,
        price_history=[100.0],
        volume_history=[1000.0]
    )
    
    # Set up mock signal
    mock_trader.generate_trade_signal.return_value = TradeSignal(
        type='BUY',
        confidence=0.8,
        timestamp=1000.0
    )
    
    await coordinator.process_market_update('BTC/USDT', market_data)
    
    # Verify market data was processed
    mock_trader.process_market_data.assert_called_once_with(market_data)
    mock_trader.generate_trade_signal.assert_called_once()

@pytest.mark.asyncio
async def test_trading_signal_processing(coordinator, mock_executor):
    # Setup mock trade result
    mock_executor.execute_trade.return_value = {
        'order': {'id': 'test_order'},
        'market': 'BTC/USDT',
        'signal': TradeSignal(type='BUY', confidence=0.8, timestamp=1000.0)
    }
    
    signal = TradeSignal(type='BUY', confidence=0.8, timestamp=1000.0)
    
    await coordinator._process_trading_signal('BTC/USDT', signal)
    
    # Verify trade was executed
    mock_executor.execute_trade.assert_called_once()
    assert len(coordinator.active_trades) == 1

@pytest.mark.asyncio
async def test_position_updates(coordinator, mock_executor):
    # Add test trade
    coordinator.active_trades['test_order'] = {
        'order': {'id': 'test_order'},
        'market': 'BTC/USDT'
    }
    
    # Setup mock order status
    mock_executor.update_order_status.return_value = {
        'status': 'closed',
        'market': 'BTC/USDT'
    }
    
    await coordinator.update_positions()
    
    # Verify position was updated
    mock_executor.update_order_status.assert_called_once_with('test_order')
    assert len(coordinator.active_trades) == 0

@pytest.mark.asyncio
async def test_position_exit_checking(coordinator, mock_executor):
    # Setup test position
    position_id = 'test_position'
    mock_executor.position_cache[position_id] = {
        'signal': TradeSignal(type='BUY', confidence=0.8, timestamp=1000.0),
        'current_price': 52000.0,
        'entry_price': 50000.0
    }
    
    # Setup test goal
    test_goal = Goal(
        id='test_goal',
        type='position_management',
        parameters={
            'position_id': position_id,
            'take_profit': 0.03  # 3% take profit
        },
        status=GoalStatus.IN_PROGRESS,
        priority=1,
        dependencies=[],
        created_at=datetime.now()
    )
    
    coordinator.traders['BTC/USDT'].goal_manager.get_active_goals.return_value = [test_goal]
    
    await coordinator.check_position_exits()
    
    # Verify position was closed due to take profit
    mock_executor.close_position.assert_called_once_with(
        position_id,
        reason='goal_triggered'
    )

@pytest.mark.asyncio
async def test_portfolio_status(coordinator):
    # Setup some test data
    coordinator.active_trades['test_order'] = {
        'order': {'id': 'test_order'},
        'market': 'BTC/USDT'
    }
    coordinator.executor.position_cache['test_position'] = {
        'market': 'BTC/USDT'
    }
    
    # Get portfolio status
    status = await coordinator.get_portfolio_status()
    
    # Verify status structure
    assert 'active_trades' in status
    assert 'positions' in status
    assert 'markets' in status
    assert status['active_trades'] == 1
    assert status['positions'] == 1
    assert 'BTC/USDT' in status['markets']
    assert 'ETH/USDT' in status['markets']

@pytest.mark.asyncio
async def test_market_analysis(coordinator, mock_trader):
    # Setup mock context
    mock_trader.load_context.return_value = {
        'current_price': 50000.0,
        'current_patterns': ['pattern1', 'pattern2']
    }
    
    # Get market analysis
    analysis = await coordinator.get_market_analysis('BTC/USDT')
    
    # Verify analysis structure
    assert analysis is not None
    assert 'current_price' in analysis
    assert 'current_patterns' in analysis
    assert 'active_goals' in analysis
    assert 'recent_trades' in analysis
    assert analysis['current_price'] == 50000.0
    assert len(analysis['current_patterns']) == 2

@pytest.mark.asyncio
async def test_handle_invalid_market(coordinator):
    # Test processing invalid market
    await coordinator.process_market_update('INVALID/MARKET', MarketData(
        timestamp=1000.0,
        price_history=[100.0],
        volume_history=[1000.0]
    ))
    
    # Test getting analysis for invalid market
    analysis = await coordinator.get_market_analysis('INVALID/MARKET')
    assert analysis is None

@pytest.mark.asyncio
async def test_position_management_workflow(coordinator, mock_executor):
    # Setup mock trade execution
    mock_executor.execute_trade.return_value = {
        'order': {'id': 'test_order'},
        'market': 'BTC/USDT',
        'signal': TradeSignal(type='BUY', confidence=0.8, timestamp=1000.0)
    }
    
    # Process a trade signal
    signal = TradeSignal(type='BUY', confidence=0.8, timestamp=1000.0)
    await coordinator._process_trading_signal('BTC/USDT', signal)
    
    # Verify position management goal was created
    assert coordinator.traders['BTC/USDT'].goal_manager.add_goal.called
    
    # Update positions
    mock_executor.update_order_status.return_value = {
        'status': 'closed',
        'market': 'BTC/USDT'
    }
    await coordinator.update_positions()
    
    # Verify position updates were processed
    assert len(coordinator.active_trades) == 0