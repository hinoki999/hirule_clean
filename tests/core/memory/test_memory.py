import pytest
from datetime import datetime, timedelta
from src.core.memory import MemoryManager, MemoryType, Memory
import os

@pytest.fixture
def memory_manager():
    # Use temporary test database
    test_db = "test_memory.db"
    manager = MemoryManager(test_db)
    yield manager
    # Cleanup after tests
    if os.path.exists(test_db):
        os.remove(test_db)

def test_add_trade_memory(memory_manager):
    trade_data = {
        'pair': 'BTC/USD',
        'type': 'buy',
        'amount': 1.0,
        'price': 50000.0
    }
    memory_id = memory_manager.add_trade_memory(trade_data, importance=0.8)
    assert memory_id > 0
    
    # Verify retrieval
    memories = memory_manager.get_recent_trades(hours=1)
    assert len(memories) == 1
    assert memories[0].content == trade_data
    assert memories[0].importance == 0.8

def test_add_market_memory(memory_manager):
    market_data = {
        'pair': 'BTC/USD',
        'price': 50000.0,
        'volume': 100.0,
        'timestamp': datetime.utcnow().isoformat()
    }
    memory_id = memory_manager.add_market_memory(market_data)
    assert memory_id > 0
    
    # Verify retrieval
    memories = memory_manager.get_market_context(hours=1)
    assert len(memories) == 1
    assert memories[0].content == market_data

def test_risk_events(memory_manager):
    # Add some risk events
    risk_data = {
        'type': 'volatility_spike',
        'metric': 'VIX',
        'value': 35.0
    }
    memory_manager.add_risk_memory(risk_data, importance=0.9)
    
    # Add a less important risk event
    minor_risk = {
        'type': 'small_drawdown',
        'value': -0.5
    }
    memory_manager.add_risk_memory(minor_risk, importance=0.3)
    
    # Verify only high importance events are retrieved
    events = memory_manager.get_risk_events(hours=24, min_importance=0.7)
    assert len(events) == 1
    assert events[0].content['type'] == 'volatility_spike'

def test_clear_old_memories(memory_manager):
    # Add memories with old timestamps
    old_time = datetime.utcnow() - timedelta(days=31)
    old_trade = Memory(
        memory_type=MemoryType.TRADE,
        content={'old': 'trade'},
        importance=0.5,
        timestamp=old_time
    )
    memory_manager.store.store(old_trade)
    
    # Add recent memory
    memory_manager.add_trade_memory({'new': 'trade'})
    
    # Clear old memories
    memory_manager.clear_old_memories(days=30)
    
    # Verify only recent memory remains
    trades = memory_manager.get_recent_trades(hours=24*31)
    assert len(trades) == 1
    assert trades[0].content == {'new': 'trade'}

def test_summarize_recent_activity(memory_manager):
    # Add various types of memories
    memory_manager.add_trade_memory({'trade': 1}, importance=0.8)
    memory_manager.add_trade_memory({'trade': 2}, importance=0.4)
    memory_manager.add_market_memory({'market': 1})
    memory_manager.add_risk_memory({'risk': 1}, importance=0.9)
    
    summary = memory_manager.summarize_recent_activity(hours=24)
    
    assert summary['total_trades'] == 2
    assert summary['high_importance_trades'] == 1
    assert summary['market_data_points'] == 1
    assert summary['risk_events'] == 1