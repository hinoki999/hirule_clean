"""
Memory System Integration for NLT Trading System
"""
from typing import Dict, Any
import json
import logging
from .mock_redis import MockRedis, MockRedisFactory

logger = logging.getLogger(__name__)

class MemorySystem:
    def __init__(self, config: Dict):
        self.config = config
        self.redis_client = None
        self.namespace = config.get('namespace', 'nlt_trading')

    async def initialize(self):
        """Initialize Redis connection"""
        try:
            self.redis_client = MockRedisFactory.from_url()
            logger.info("Memory system initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize memory system: {str(e)}")
            raise

    async def store(self, key: str, value: Any):
        """Store data in memory system"""
        try:
            full_key = f"{self.namespace}:{key}"
            await self.redis_client.set(full_key, json.dumps(value))
            logger.debug(f"Stored data at {full_key}: {value}")
        except Exception as e:
            logger.error(f"Failed to store data: {str(e)}")
            raise

    async def retrieve(self, key: str) -> Any:
        """Retrieve data from memory system"""
        try:
            full_key = f"{self.namespace}:{key}"
            data = await self.redis_client.get(full_key)
            if data:
                return json.loads(data)
            return None
        except Exception as e:
            logger.error(f"Failed to retrieve data: {str(e)}")
            raise
