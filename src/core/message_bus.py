"""
Message Bus Implementation using Mock Redis
"""
from typing import Dict, List, Callable
import json
import asyncio
import logging

logger = logging.getLogger(__name__)

class MessageBus:
    def __init__(self, config: Dict):
        self.config = config
        self.redis_client = None
        self.subscribers: Dict[str, List[Callable]] = {}
        self.running = False
        
    async def initialize(self):
        """Initialize Redis connection"""
        try:
            from .mock_redis import MockRedis
            self.redis_client = MockRedis()
            self.running = True
            logger.info("Message bus initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize message bus: {str(e)}")
            raise
            
    async def publish(self, topic: str, message: Dict):
        """Publish message to topic"""
        try:
            message_str = json.dumps(message)
            logger.debug(f"Publishing to {topic}: {message_str}")
            
            # Direct delivery to subscribed handlers
            if topic in self.subscribers:
                for callback in self.subscribers[topic]:
                    try:
                        await callback(topic, message)
                        logger.debug(f"Successfully delivered message to subscriber")
                    except Exception as e:
                        logger.error(f"Error in subscriber callback: {str(e)}")
            
            # Also publish through Redis
            await self.redis_client.publish(topic, message_str)
            
        except Exception as e:
            logger.error(f"Failed to publish message: {str(e)}")
            raise
            
    async def subscribe(self, topics: List[str], callback: Callable):
        """Subscribe to topics"""
        try:
            for topic in topics:
                logger.debug(f"Subscribing to {topic}")
                if topic not in self.subscribers:
                    self.subscribers[topic] = []
                self.subscribers[topic].append(callback)
                
                # Set up Redis subscription
                pubsub = self.redis_client.pubsub()
                await pubsub.subscribe(topic)
                
            logger.debug(f"Current subscribers: {self.subscribers}")
            
        except Exception as e:
            logger.error(f"Failed to subscribe: {str(e)}")
            raise
