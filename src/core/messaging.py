from typing import Dict, Any, Optional, Callable
import asyncio
import uuid
from datetime import datetime

class Message:
    ###"""Message class for agent communication###"""
    def __init__(self, sender: str, recipient: str, message_type: str, payload: Dict[str, Any]):
        self.id = str(uuid.uuid4())
        self.sender = sender
        self.recipient = recipient
        self.message_type = message_type
        self.payload = payload
        self.timestamp = datetime.now()

class MessageBus:
    ###"""Message bus for agent communication###"""
    def __init__(self):
        self._subscribers = {}
        self._message_queue = asyncio.Queue()

    async def subscribe(self, topic: str, callback: Callable):
        if topic not in self._subscribers:
            self._subscribers[topic] = []
        self._subscribers[topic].append(callback)

    async def publish(self, message: Message) -> bool:
        await self._message_queue.put(message)
        return True

    def create_message(self, sender: str, recipient: str, message_type: str, payload: Dict[str, Any]) -> Message:
        return Message(sender, recipient, message_type, payload)

    async def get_messages(self, subscriber_id: str, timeout: float = 0.1) -> Optional[Message]:
        try:
            return await asyncio.wait_for(self._message_queue.get(), timeout)
        except asyncio.TimeoutError:
            return None


