<<<<<<< ours
# tests/test_agents/mock_agent.py
from src.agents.base import BaseAgent, AgentCapability

class MockAgent(BaseAgent):
    def __init__(self, agent_id: str = "mock_agent"):
        super().__init__(agent_id=agent_id, capabilities=[AgentCapability.SEMANTIC])
        self.process_task_called = False
        self.status = "RUNNING"
        self.processed_tasks = []
        print(f"Initialized MockAgent {agent_id} with capabilities: {self.capabilities}")

async def process_task(self, task: dict):
    self.process_task_called = True
    self.processed_tasks.append(task)
    return True

    async def setup(self):
        #"""Setup the mock agent#"""
        await super().setup()
        self.status = "RUNNING"

    async def cleanup(self):
        #"""Cleanup the mock agent#"""
        self.status = "STOPPED"

    async def process_message(self, message: dict):
        #"""Process a test message#"""
        return {"status": "success", "message": "processed"}

    async def process_task(self, task: dict):
        #"""Process a test task#"""
        self.process_task_called = True
        self.processed_tasks.append(task)
        return True

    async def get_status(self):
        #"""Get mock agent status#"""
        return {"status": self.status}


||||||| base
=======
# tests/test_agents/mock_agent.py
from src.agents.base import BaseAgent, AgentCapability

class MockAgent(BaseAgent):
    def __init__(self, agent_id: str = "mock_agent"):
        super().__init__(agent_id=agent_id, capabilities=[AgentCapability.SEMANTIC])
        self.process_task_called = False
        self.status = "RUNNING"
        self.processed_tasks = []
        print(f"Initialized MockAgent {agent_id} with capabilities: {self.capabilities}")

    async def setup(self):
        """Setup the mock agent"""
        await super().setup()
        self.status = "RUNNING"
        
    async def cleanup(self):
        """Cleanup the mock agent"""
        self.status = "STOPPED"

    async def process_message(self, message: dict):
        """Process a test message"""
        return {"status": "success", "message": "processed"}

    async def process_task(self, task: dict):
        """Process a test task"""
        self.process_task_called = True
        self.processed_tasks.append(task)
        return True

    async def get_status(self):
        """Get mock agent status"""
        return {"status": self.status}
>>>>>>> theirs
