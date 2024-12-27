import asyncio
import unittest
from src.agents.master_coordinator import MasterCoordinator, CoordinatorStatus
from src.agents.base import BaseAgent, AgentCapability

class TestAgent(BaseAgent):
    """Test agent for testing coordinator functionality"""
    def __init__(self, agent_id: str):
        super().__init__(agent_id=agent_id, capabilities=[AgentCapability.SEMANTIC_ANALYSIS])

    async def process_task(self, task_data: dict) -> dict:
        """Implement required method"""
        return {"status": "success", "result": "test completed"}

class TestMasterCoordinator(unittest.TestCase):
    def setUp(self):
        self.coordinator = None
        self.test_agent = None

    async def async_setup(self):
        self.coordinator = MasterCoordinator()
        self.test_agent = TestAgent("test_agent_1")
        await self.coordinator.initialize()

    async def async_teardown(self):
        if self.coordinator:
            await self.coordinator.stop()

    async def async_test_initialization(self):
        """Test coordinator initialization"""
        self.assertEqual(self.coordinator.status, CoordinatorStatus.RUNNING)

    async def async_test_agent_registration(self):
        """Test agent registration functionality"""
        # Register test agent
        success = await self.coordinator.register_agent(self.test_agent)
        self.assertTrue(success)
        self.assertIn("test_agent_1", self.coordinator.registered_agents)

        # Try registering same agent again
        success = await self.coordinator.register_agent(self.test_agent)
        self.assertFalse(success)  # Should fail for duplicate registration

    async def async_test_task_submission(self):
        """Test task submission and processing"""
        # Submit a test task
        task_data = {
            "type": "semantic",
            "action": "analyze",
            "data": "Test data"
        }
        
        task_id = await self.coordinator.submit_task(task_data)
        self.assertIsNotNone(task_id)
        
        # Check task queue
        self.assertEqual(self.coordinator.task_queue.qsize(), 1)

    async def async_test_coordinator_status(self):
        """Test status reporting"""
        status = await self.coordinator.get_status()
        
        self.assertIn("status", status)
        self.assertIn("registered_agents", status)
        self.assertIn("pending_tasks", status)
        self.assertEqual(status["status"], "RUNNING")

    async def async_test_full_workflow(self):
        """Test a complete workflow"""
        # Register agent
        await self.coordinator.register_agent(self.test_agent)
        
        # Submit task
        task_data = {
            "type": "semantic",
            "action": "analyze",
            "data": "Test workflow"
        }
        task_id = await self.coordinator.submit_task(task_data)
        
        # Start processing
        await self.coordinator.start()
        
        # Give some time for processing
        await asyncio.sleep(1)
        
        # Check status
        status = await self.coordinator.get_status()
        self.assertEqual(status["status"], "RUNNING")

    def test_all(self):
        """Run all async tests"""
        async def run_all():
            await self.async_setup()
            try:
                await self.async_test_initialization()
                await self.async_test_agent_registration()
                await self.async_test_task_submission()
                await self.async_test_coordinator_status()
                await self.async_test_full_workflow()
            finally:
                await self.async_teardown()

        asyncio.run(run_all())

if __name__ == '__main__':
    unittest.main()