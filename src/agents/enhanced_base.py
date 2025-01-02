from typing import Dict, Any, Optional
from .base import BaseAgent
from ..memory.manager import MemoryManager

class EnhancedBaseAgent(BaseAgent):
    def __init__(self, agent_id: str, config: Dict[str, Any]):
        super().__init__(agent_id, config)
        self.memory_manager = MemoryManager()
        self.context = {}

    async def remember(self, key: str, value: Any) -> None:
        """Store information in agent's memory"""
        await self.memory_manager.store(self.agent_id, key, value)

    async def recall(self, key: str) -> Optional[Any]:
        """Retrieve information from agent's memory"""
        return await self.memory_manager.retrieve(self.agent_id, key)

    async def forget(self, key: str) -> None:
        """Remove information from agent's memory"""
        await self.memory_manager.delete(self.agent_id, key)

    async def update_context(self, context_updates: Dict[str, Any]) -> None:
        """Update agent's current context"""
        self.context.update(context_updates)
        await self.remember('current_context', self.context)

    async def load_context(self) -> Dict[str, Any]:
        """Load agent's saved context"""
        context = await self.recall('current_context')
        if context:
            self.context = context
        return self.context