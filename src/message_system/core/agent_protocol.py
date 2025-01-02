from typing import Dict, List, Any, Optional
from datetime import datetime

class AgentCommunicationProtocol:
    def __init__(self):
        self.subscriptions: Dict[str, List[callable]] = {}
        self.message_history: List[Dict] = []
        
    async def publish(self, message: Dict):
        """Publish message to all subscribers"""
        msg_type = message.get("type")
        if msg_type in self.subscriptions:
            for callback in self.subscriptions[msg_type]:
                await callback(message)
        self.message_history.append(message)
        
    def subscribe(self, msg_type: str, callback: callable):
        """Subscribe to specific message types"""
        if msg_type not in self.subscriptions:
            self.subscriptions[msg_type] = []
        self.subscriptions[msg_type].append(callback)
        
    def get_history(self, msg_type: Optional[str] = None) -> List[Dict]:
        """Get message history, optionally filtered by type"""
        if msg_type is None:
            return self.message_history
        return [msg for msg in self.message_history if msg.get("type") == msg_type]
