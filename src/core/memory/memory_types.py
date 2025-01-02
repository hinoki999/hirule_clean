from enum import Enum
from typing import Dict, Any, Optional
from datetime import datetime

class MemoryType(Enum):
    """Types of memories that can be stored"""
    TRADE = "trade"
    MARKET_DATA = "market_data"
    STRATEGY = "strategy"
    RISK = "risk"
    SYSTEM = "system"

class Memory:
    """Base class for memory entries"""
    def __init__(self, 
                 memory_type: MemoryType,
                 content: Dict[str, Any],
                 importance: float = 0.0,
                 timestamp: Optional[datetime] = None):
        self.memory_type = memory_type
        self.content = content
        self.importance = importance
        self.timestamp = timestamp or datetime.utcnow()
        self.last_accessed = datetime.utcnow()
        self.access_count = 0
    
    def access(self):
        """Update access metadata when memory is retrieved"""
        self.last_accessed = datetime.utcnow()
        self.access_count += 1
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert memory to dictionary format"""
        return {
            'type': self.memory_type.value,
            'content': self.content,
            'importance': self.importance,
            'timestamp': self.timestamp.isoformat(),
            'last_accessed': self.last_accessed.isoformat(),
            'access_count': self.access_count
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Memory':
        """Create memory instance from dictionary"""
        return cls(
            memory_type=MemoryType(data['type']),
            content=data['content'],
            importance=data['importance'],
            timestamp=datetime.fromisoformat(data['timestamp'])
        )