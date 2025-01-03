"""
Mock Redis implementation for testing
"""
from typing import Dict, Any, List, Callable
import asyncio
import json
import logging

logger = logging.getLogger(__name__)

class MockPubSub:
    def __init__(self, mock_redis):
        self.mock_redis = mock_redis
        self.channels: Dict[str, List[Callable]] = {}
        
    async def subscribe(self, *channels):
        """Subscribe to channels"""
        for channel in channels:
            if channel not in self.channels:
                self.channels[channel] = []
            logger.debug(f"Subscribed to channel: {channel}")
            
    async def get_message(self, timeout=None):
        """Wait for next message"""
        await asyncio.sleep(0.01)  # Small delay
        return None
        
class MockRedis:
    def __init__(self):
        self.data: Dict[str, str] = {}
        self._pubsub = MockPubSub(self)
        
    async def ping(self):
        """Mock ping"""
        return True
        
    async def set(self, key: str, value: str):
        """Mock set"""
        logger.debug(f"Setting key {key} to value {value}")
        self.data[key] = value
        return True
        
    async def get(self, key: str):
        """Mock get"""
        value = self.data.get(key)
        logger.debug(f"Getting key {key}: {value}")
        return value
        
    async def publish(self, channel: str, message: str):
        """Mock publish"""
        logger.debug(f"Publishing to channel {channel}: {message}")
        callbacks = self._pubsub.channels.get(channel, [])
        if callbacks:
            logger.debug(f"Found {len(callbacks)} callbacks for channel {channel}")
            try:
                decoded_message = {
                    'type': 'message',
                    'channel': channel,
                    'data': message
                }
                for callback in callbacks:
                    asyncio.create_task(callback(decoded_message))
            except Exception as e:
                logger.error(f"Error publishing message: {str(e)}")
        return len(callbacks)
        
    def pubsub(self):
        """Return pubsub interface"""
        return self._pubsub

class MockRedisFactory:
    @staticmethod
    def from_url(*args, **kwargs):
        """Create a new MockRedis instance"""
        return MockRedis()
