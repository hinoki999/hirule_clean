from typing import Dict, Any

class BaseAgent:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.message_bus = None
        self.capabilities = []
    
    async def setup(self):
        pass
