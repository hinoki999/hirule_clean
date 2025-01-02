from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from .memory_store import MemoryStore
from .memory_types import Memory, MemoryType

class MemoryManager:
    """Manages memory operations and provides high-level memory functionality"""
    
    def __init__(self, store_path: str = "memory.db"):
        self.store = MemoryStore(store_path)
        self.importance_threshold = 0.5  # Minimum importance for long-term storage
        
    def add_trade_memory(self, trade_data: Dict[str, Any], importance: float = 0.0) -> int:
        """Add a trade-related memory"""
        memory = Memory(
            memory_type=MemoryType.TRADE,
            content=trade_data,
            importance=importance
        )
        return self.store.store(memory)
    
    def add_market_memory(self, market_data: Dict[str, Any], importance: float = 0.0) -> int:
        """Add a market data memory"""
        memory = Memory(
            memory_type=MemoryType.MARKET_DATA,
            content=market_data,
            importance=importance
        )
        return self.store.store(memory)
        
    def add_strategy_memory(self, strategy_data: Dict[str, Any], importance: float = 0.0) -> int:
        """Add a strategy-related memory"""
        memory = Memory(
            memory_type=MemoryType.STRATEGY,
            content=strategy_data,
            importance=importance
        )
        return self.store.store(memory)

    def add_risk_memory(self, risk_data: Dict[str, Any], importance: float = 0.0) -> int:
        """Add a risk-related memory"""
        memory = Memory(
            memory_type=MemoryType.RISK,
            content=risk_data,
            importance=importance
        )
        return self.store.store(memory)

    def get_recent_trades(self, hours: int = 24, min_importance: float = 0.0) -> List[Memory]:
        """Get trade memories from the last N hours"""
        start_time = datetime.utcnow() - timedelta(hours=hours)
        memories = self.store.retrieve(
            memory_type=MemoryType.TRADE,
            start_time=start_time
        )
        return [m for m in memories if m.importance >= min_importance]

    def get_market_context(self, hours: int = 1) -> List[Memory]:
        """Get recent market data memories for context"""
        start_time = datetime.utcnow() - timedelta(hours=hours)
        return self.store.retrieve(
            memory_type=MemoryType.MARKET_DATA,
            start_time=start_time
        )

    def get_strategy_history(self, days: int = 7) -> List[Memory]:
        """Get strategy-related memories from the past N days"""
        start_time = datetime.utcnow() - timedelta(days=days)
        return self.store.retrieve(
            memory_type=MemoryType.STRATEGY,
            start_time=start_time
        )

    def get_risk_events(self, hours: int = 24, min_importance: float = 0.7) -> List[Memory]:
        """Get significant risk-related memories"""
        start_time = datetime.utcnow() - timedelta(hours=hours)
        memories = self.store.retrieve(
            memory_type=MemoryType.RISK,
            start_time=start_time
        )
        return [m for m in memories if m.importance >= min_importance]

    def clear_old_memories(self, days: int = 30, except_types: List[MemoryType] = None):
        """Clear memories older than N days, optionally preserving specific types"""
        end_time = datetime.utcnow() - timedelta(days=days)
        
        if except_types:
            for memory_type in MemoryType:
                if memory_type not in except_types:
                    memories = self.store.retrieve(
                        memory_type=memory_type,
                        end_time=end_time
                    )
                    if memories:
                        self.store.clear(memory_type)
        else:
            memories = self.store.retrieve(end_time=end_time)
            if memories:
                self.store.clear()

    def summarize_recent_activity(self, hours: int = 24) -> Dict[str, Any]:
        """Summarize recent trading activity across all memory types"""
        start_time = datetime.utcnow() - timedelta(hours=hours)
        
        trades = self.get_recent_trades(hours=hours)
        market_data = self.get_market_context(hours=hours)
        risk_events = self.get_risk_events(hours=hours)
        
        return {
            'total_trades': len(trades),
            'high_importance_trades': len([t for t in trades if t.importance >= self.importance_threshold]),
            'market_data_points': len(market_data),
            'risk_events': len(risk_events),
            'timeframe': f'Last {hours} hours'
        }