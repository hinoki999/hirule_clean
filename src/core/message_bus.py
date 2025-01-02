from typing import Dict, Any, Callable, List
from asyncio import Queue

class MessageBus:
    """Core message bus for agent communication"""
    
    def __init__(self):
        self.subscribers: Dict[str, List[Callable]] = {}
        self.message_queue = Queue()
