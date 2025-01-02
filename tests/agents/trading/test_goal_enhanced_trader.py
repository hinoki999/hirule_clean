import pytest
from datetime import datetime
import numpy as np
from src.agents.trading.goal_enhanced_trader import GoalEnhancedTrader
from src.core.types import MarketData
from src.goals.base import GoalStatus

@pytest.fixture
def trader():
    config = {
        'market': 'BTC/USD',
        'timeframe': '1h',
        'pattern_window': 20
    }
    return GoalEnhancedTrader('test_trader', config)

@pytest.fixture
def market_data():
    return MarketData(
        timestamp=1000.0,
        price_history=list(np.linspace(100, 120, 20)),
        volume_history=list(np.ones(20) * 1000)
    )

@pytest.mark.asyncio
async def test_initialization(trader):
    await trader.initialize()
    active_goals = trader.goal_manager.get_active_goals()
    
    # Should have initial risk and analysis goals
    assert len(active_goals) == 2
    goal_types = {goal.type for goal in active_goals}
    assert 'risk_assessment' in goal_types
    assert 'market_analysis' in goal_types

@pytest.mark.asyncio
async def test_market_data_processing(trader, market_data):
    await trader.initialize()
    await trader.process_market_data(market_data)
    
    # Check if patterns were stored
    patterns = await trader.recall(f'patterns_{market_data.timestamp}')
    assert patterns is not None
    
    # Check context update
    context = await trader.load_context()
    assert context['current_price'] == market_data.price_history[-1]
    assert context['current_time'] == market_data.timestamp

@pytest.mark.asyncio
async def test_goal_completion(trader, market_data):
    await trader.initialize()
    
    # Create strong reversal pattern
    market_data.price_history[-5:] = [120, 118, 116, 114, 112]
    await trader.process_market_data(market_data)
    
    # Check if analysis goal was completed
    analysis_goals = [
        goal for goal in trader.goal_manager.goals.values()
        if goal.type == 'market_analysis'
    ]
    assert any(goal.status == GoalStatus.COMPLETED for goal in analysis_goals)

@pytest.mark.asyncio
async def test_position_management(trader):
    await trader.initialize()
    
    # Simulate opening a position
    position = {
        'id': 'test_position',
        'market': 'BTC/USD',
        'direction': 'BUY',
        'entry_price': 100.0,
        'current_price': 100.0
    }
    trader.active_positions['test_position'] = position
    
    # Create position management goal
    management_goal = trader.goal_manager.goals[
        list(trader.goal_manager.goals.keys())[0]
    ]
    management_goal.parameters.update({
        'position_id': 'test_position',
        'stop_loss': 0.02,
        'take_profit': 0.05
    })
    
    # Test stop loss
    market_data = MarketData(
        timestamp=1000.0,
        price_history=[97.0],  # 3% loss
        volume_history=[1000]
    )
    await trader.process_market_data(market_data)
    
    # Position should be closed
    assert 'test_position' not in trader.active_positions
    
    # Goal should be completed
    assert management_goal.status == GoalStatus.COMPLETED
    assert management_goal.result['reason'] == 'stop_loss'

@pytest.mark.asyncio
async def test_trade_signal_generation(trader, market_data):
    await trader.initialize()
    
    # Create clear buy signal
    market_data.price_history[-5:] = [100, 98, 96, 94, 92]  # Strong downtrend
    await trader.process_market_data(market_data)
    
    signal = await trader.generate_trade_signal()
    assert signal.type in ['BUY', 'SELL', 'HOLD']
    assert 0 <= signal.confidence <= 1.0

@pytest.mark.asyncio
async def test_memory_persistence(trader, market_data):
    await trader.initialize()
    await trader.process_market_data(market_data)
    
    # Store some test data in memory
    test_data = {'key': 'value'}
    await trader.remember('test_key', test_data)
    
    # Verify data persistence
    retrieved_data = await trader.recall('test_key')
    assert retrieved_data == test_data

@pytest.mark.asyncio
async def test_trade_history_updates(trader):
    await trader.initialize()
    
    # Create test trade
    trade = {
        'position_id': 'test_trade',
        'market': 'BTC/USD',
        'direction': 'BUY',
        'entry_price': 100.0,
        'exit_price': 105.0,
        'pnl': 0.05,
        'reason': 'take_profit',
        'timestamp': datetime.now().timestamp()
    }
    
    # Update trade history
    await trader.update_trade_history(trade)
    
    # Verify trade was recorded
    assert len(trader.trade_history) == 1
    assert trader.trade_history[0] == trade
    
    # Verify trade was stored in memory
    stored_history = await trader.recall('trade_history')
    assert len(stored_history) == 1
    assert stored_history[0] == trade

@pytest.mark.asyncio
async def test_risk_management(trader):
    await trader.initialize()
    
    # Get risk assessment goal
    risk_goals = [
        goal for goal in trader.goal_manager.goals.values()
        if goal.type == 'risk_assessment'
    ]
    risk_goal = risk_goals[0]
    
    # Verify risk parameters
    assert risk_goal.parameters['max_position_size'] <= 0.2  # Max 20%
    assert risk_goal.parameters['max_daily_loss'] <= 0.05   # Max 5%
    
    # Test position size constraints
    position_size = risk_goal.parameters['max_position_size']
    assert position_size > 0 and position_size <= 0.2

@pytest.mark.asyncio
async def test_pattern_analysis_workflow(trader, market_data):
    await trader.initialize()
    
    # Create a sequence of market movements
    timestamps = np.linspace(1000, 1010, 10)
    price_sequences = [
        [100, 102, 104, 106, 108, 110, 112, 114, 116, 118],  # Uptrend
        [118, 116, 114, 112, 110, 108, 106, 104, 102, 100],  # Downtrend
        [100, 100, 101, 99, 100, 101, 99, 100, 101, 99]      # Consolidation
    ]
    
    for prices in price_sequences:
        for i, price in enumerate(prices):
            data = MarketData(
                timestamp=timestamps[i],
                price_history=list(prices[:i+1]) + [0] * (20-i-1),
                volume_history=[1000] * 20
            )
            await trader.process_market_data(data)
            
            # Verify pattern detection
            stored_patterns = await trader.recall(f'patterns_{timestamps[i]}')
            if stored_patterns:
                assert all(0 <= pattern.confidence <= 1.0 for pattern in stored_patterns)
                assert all(hasattr(pattern, 'type') for pattern in stored_patterns)

@pytest.mark.asyncio
async def test_goal_dependencies(trader):
    await trader.initialize()
    
    # Create a chain of dependent goals
    analysis_goal = TradingGoals.create_market_analysis_goal(
        market='BTC/USD',
        timeframe='1h'
    )
    await trader.goal_manager.add_goal(analysis_goal)
    
    entry_goal = TradingGoals.create_position_entry_goal(
        market='BTC/USD',
        direction='BUY',
        analysis_goal_id=analysis_goal.id
    )
    await trader.goal_manager.add_goal(entry_goal)
    
    # Entry goal should not be active until analysis is complete
    active_goals = trader.goal_manager.get_active_goals()
    assert entry_goal.id not in [g.id for g in active_goals]
    
    # Complete analysis goal
    await trader.goal_manager.update_goal_progress(
        analysis_goal.id,
        1.0,
        {'patterns': []}
    )
    
    # Now entry goal should be active
    active_goals = trader.goal_manager.get_active_goals()
    assert entry_goal.id in [g.id for g in active_goals]