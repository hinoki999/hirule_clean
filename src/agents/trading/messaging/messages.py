from dataclasses import dataclass
from typing import Dict, Any, Optional
from datetime import datetime
import asyncio

@dataclass
class Message:
    id: str
    sender: str
    recipient: str
    message_type: str
    payload: Dict[str, Any]
    priority: int = 0
    timestamp: float = datetime.now().timestamp()

class MessageBus:
    def __init__(self):
        self.subscribers = {}
        self.message_queue = asyncio.Queue()
    
    def create_message(self, sender: str, recipient: str, message_type: str, 
                      payload: Dict[str, Any], priority: int = 0) -> Message:
        return Message(
            id=str(datetime.now().timestamp()),
            sender=sender,
            recipient=recipient,
            message_type=message_type,
            payload=payload,
            priority=priority
        )
    
    async def publish(self, message: Message) -> bool:
        # Basic implementation
        await self.message_queue.put(message)
        return True
    
    async def subscribe(self, topic: str, callback):
        self.subscribers[topic] = callback
    
    async def get_messages(self, subscriber_id: str) -> Optional[Message]:
        return await self.message_queue.get()

"""
Messaging package for Hirule trading system
"""
