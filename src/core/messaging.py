<<<<<<< ours
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


||||||| base
=======
from typing import Dict, Any, Callable, List, Optional
import asyncio
import uuid
from dataclasses import dataclass
from datetime import datetime

@dataclass
class Message:
    """Message structure for inter-agent communication."""
    id: str
    sender: str
    recipient: str
    message_type: str
    payload: Dict[str, Any]
    timestamp: float
    priority: int = 0
    reply_to: Optional[str] = None

class MessageBus:
    """Central message bus for agent communication."""
    
    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = {}
        self._queues: Dict[str, asyncio.Queue] = {}
        self._message_history: List[Message] = []
        self.max_history = 1000
    
    async def publish(self, message: Message):
        """Publish a message to subscribers."""
        # Store in history
        self._message_history.append(message)
        if len(self._message_history) > self.max_history:
            self._message_history.pop(0)
        
        # Notify subscribers
        message_type = message.message_type
        if message_type in self._subscribers:
            for callback in self._subscribers[message_type]:
                try:
                    await callback(message)
                except Exception as e:
                    print(f"Error in message handler: {str(e)}")
        
        # Add to recipient's queue
        if message.recipient in self._queues:
            await self._queues[message.recipient].put(message)
    
    def subscribe(self, message_type: str, callback: Callable):
        """Subscribe to a message type."""
        if message_type not in self._subscribers:
            self._subscribers[message_type] = []
        self._subscribers[message_type].append(callback)
    
    def unsubscribe(self, message_type: str, callback: Callable):
        """Unsubscribe from a message type."""
        if message_type in self._subscribers:
            self._subscribers[message_type].remove(callback)
    
    def register_agent(self, agent_id: str):
        """Register an agent with the message bus."""
        if agent_id not in self._queues:
            self._queues[agent_id] = asyncio.Queue()
    
    def unregister_agent(self, agent_id: str):
        """Unregister an agent from the message bus."""
        if agent_id in self._queues:
            del self._queues[agent_id]
    
    async def get_messages(self, agent_id: str) -> asyncio.Queue:
        """Get message queue for an agent."""
        if agent_id not in self._queues:
            self.register_agent(agent_id)
        return self._queues[agent_id]

    def create_message(self, sender: str, recipient: str, 
                      message_type: str, payload: Dict[str, Any], 
                      priority: int = 0, reply_to: Optional[str] = None) -> Message:
        """Create a new message."""
        return Message(
            id=str(uuid.uuid4()),
            sender=sender,
            recipient=recipient,
            message_type=message_type,
            payload=payload,
            timestamp=datetime.now().timestamp(),
            priority=priority,
            reply_to=reply_to
        )
>>>>>>> theirs
