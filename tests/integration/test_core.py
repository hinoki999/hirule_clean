"""
Integration Test Script for NLT Trading System Core Components
"""
import asyncio
import logging
from typing import Dict
import pytest

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

from src.core.memory_system import MemorySystem
from src.core.message_bus import MessageBus

# Test configuration
CONFIG = {
    'memory_system': {
        'host': 'localhost',
        'port': 6379,
        'db': 0,
        'namespace': 'nlt_test'
    },
    'message_bus': {
        'host': 'localhost',
        'port': 6379,
        'db': 1
    }
}

@pytest.mark.asyncio
async def test_memory_system():
    """Test memory system operations"""
    memory = MemorySystem(CONFIG['memory_system'])
    await memory.initialize()
    
    test_data = {'price': 100.0, 'volume': 1000}
    await memory.store('test_key', test_data)
    retrieved = await memory.retrieve('test_key')
    assert retrieved == test_data
    logger.info("Memory system test passed")

@pytest.mark.asyncio
async def test_message_bus():
    """Test message bus operations"""
    bus = MessageBus(CONFIG['message_bus'])
    await bus.initialize()
    
    received_messages = []
    message_received = asyncio.Event()
    
    async def test_handler(topic: str, data: Dict):
        logger.debug(f"Test handler received: {topic}, {data}")
        received_messages.append((topic, data))
        message_received.set()
    
    # Subscribe and publish
    await bus.subscribe(['test_topic'], test_handler)
    test_message = {'event': 'test', 'data': {'value': 123}}
    await bus.publish('test_topic', test_message)
    
    # Wait for message with timeout
    try:
        await asyncio.wait_for(message_received.wait(), timeout=2.0)
    except asyncio.TimeoutError:
        logger.error("Timeout waiting for message")
        raise
    
    # Verify message was received
    assert len(received_messages) > 0, "No messages received"
    assert received_messages[0][1] == test_message, f"Received wrong message: {received_messages[0][1]}"
    logger.info("Message bus test passed")

@pytest.mark.asyncio
async def test_market_data_flow():
    """Test market data handling end-to-end"""
    memory = MemorySystem(CONFIG['memory_system'])
    bus = MessageBus(CONFIG['message_bus'])
    
    await memory.initialize()
    await bus.initialize()
    
    message_received = asyncio.Event()
    
    async def market_data_handler(topic: str, data: Dict):
        logger.debug(f"Market data handler received: {topic}, {data}")
        await memory.store('latest_market_data', data)
        message_received.set()
    
    await bus.subscribe(['market_data'], market_data_handler)
    
    test_data = {
        'symbol': 'NLT/USDT',
        'price': 1.234,
        'volume': 10000,
        'timestamp': 1641234567
    }
    
    logger.debug("Publishing market data")
    await bus.publish('market_data', test_data)
    
    try:
        await asyncio.wait_for(message_received.wait(), timeout=2.0)
        logger.debug("Message received successfully")
    except asyncio.TimeoutError:
        logger.error("Timeout waiting for market data")
        raise
    
    # Add small delay to ensure storage completes
    await asyncio.sleep(0.1)
    
    stored_data = await memory.retrieve('latest_market_data')
    logger.debug(f"Retrieved stored data: {stored_data}")
    assert stored_data == test_data, f"Stored data {stored_data} doesn't match test data {test_data}"
    logger.info("Market data flow test passed")

if __name__ == "__main__":
    pytest.main([__file__, '-v'])
