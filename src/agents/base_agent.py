from typing import Dict
from src.core.message_bus import MessageBus
from src.core.capabilities import Capability

class BaseAgent:
    """Base class for all agents"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.message_bus = MessageBus()
        self.capabilities = {}
    
    def register_capability(self, capability: Capability):
        """Register a capability with this agent"""
        self.capabilities[capability.name] = capability
