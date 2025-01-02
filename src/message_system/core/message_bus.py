from enum import Enum
from dataclasses import dataclass
from typing import Dict, Any, List, Optional
from datetime import datetime

class MessageType(Enum):
    MARKET_DATA = "market_data"
    TRADE_SIGNAL = "trade_signal"
    ORDER_REQUEST = "order_request"
    ORDER_UPDATE = "order_update"
    RISK_UPDATE = "risk_update"
    STRATEGY_UPDATE = "strategy_update"
    LEARNING_UPDATE = "learning_update"
    PERFORMANCE_METRIC = "performance_metric"

@dataclass
class AgentMessage:
    msg_type: MessageType
    sender_id: str
    timestamp: datetime
    data: Dict[str, Any]
    priority: int = 0
    conversation_id: Optional[str] = None
    in_reply_to: Optional[str] = None

class MessageBus:
    def __init__(self):
        self.subscribers: Dict[MessageType, List[callable]] = {}
        self.message_history: List[AgentMessage] = []
        
    async def publish(self, message: AgentMessage):
        """Publish message to all subscribers"""
        if message.msg_type in self.subscribers:
            for callback in self.subscribers[message.msg_type]:
                await callback(message)
        self.message_history.append(message)
        
    def subscribe(self, msg_type: MessageType, callback: callable):
        """Subscribe to specific message types"""
        if msg_type not in self.subscribers:
            self.subscribers[msg_type] = []
        self.subscribers[msg_type].append(callback)
        
    def get_message_history(self, msg_type: Optional[MessageType] = None) -> List[AgentMessage]:
        """Get message history, optionally filtered by type"""
        if msg_type is None:
            return self.message_history
        return [msg for msg in self.message_history if msg.msg_type == msg_type]
