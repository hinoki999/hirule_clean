from typing import Dict, Any, Optional, List
from datetime import datetime
from ..core.message_bus import MessageType, AgentMessage, MessageBus

class BaseAgent:
    def __init__(self, agent_id: str, message_bus: MessageBus):
        self.agent_id = agent_id
        self.message_bus = message_bus
        self.state: Dict[str, Any] = {}
        self.learning_metrics: Dict[str, float] = {}
        
    async def send_message(self, msg_type: MessageType, data: Dict):
        """Send a message to other agents"""
        message = AgentMessage(
            msg_type=msg_type,
            sender_id=self.agent_id,
            timestamp=datetime.now(),
            data=data
        )
        await self.message_bus.publish(message)
        
    async def receive_message(self, message: AgentMessage):
        """Handle incoming messages"""
        # Implement specific message handling logic in subclasses
        pass
        
    async def update_state(self, new_state: Dict):
        """Update agent's internal state"""
        self.state.update(new_state)
        
    async def learn_from_interaction(self, message: AgentMessage):
        """Learn from interaction with other agents"""
        # Implement learning logic in subclasses
        pass
        
    def get_state(self) -> Dict[str, Any]:
        """Get agent's current state"""
        return self.state.copy()
        
    def get_metrics(self) -> Dict[str, float]:
        """Get agent's current learning metrics"""
        return self.learning_metrics.copy()
