import pytest
from src.agents.enhanced_base import EnhancedBaseAgent

@pytest.fixture
def agent():
    return EnhancedBaseAgent('test_agent', {'config': 'test'})

@pytest.mark.asyncio
async def test_memory_operations(agent):
    # Test storing and retrieving
    await agent.remember('test_key', 'test_value')
    value = await agent.recall('test_key')
    assert value == 'test_value'

    # Test updating
    await agent.remember('test_key', 'updated_value')
    value = await agent.recall('test_key')
    assert value == 'updated_value'

    # Test deleting
    await agent.forget('test_key')
    value = await agent.recall('test_key')
    assert value is None

@pytest.mark.asyncio
async def test_context_management(agent):
    # Test context updates
    test_context = {'market': 'BTC/USD', 'timeframe': '1h'}
    await agent.update_context(test_context)
    
    # Test context persistence
    loaded_context = await agent.load_context()
    assert loaded_context == test_context