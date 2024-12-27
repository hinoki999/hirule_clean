import pytest
import pytest_asyncio
import asyncio
from unittest.mock import Mock, patch
from src.agents.master_coordinator import MasterCoordinator, CoordinatorStatus
from src.agents.base import BaseAgent, AgentCapability

# Mock Agent for testing
class MockAgent(BaseAgent):
    def __init__(self, agent_id: str = "mock_agent"):
        super().__init__(agent_id=agent_id, capabilities=[AgentCapability.SEMANTIC])
        self.process_task_called = False
        self.status = "RUNNING"

    async def setup(self):
        await super().setup()
        
    async def cleanup(self):
        pass

    async def process_message(self, message: dict):
        return {"status": "success"}

    async def process_task(self, task: dict):
        self.process_task_called = True
        return True

    async def get_status(self):
        return {"status": self.status}

# Fixtures
@pytest_asyncio.fixture
async def coordinator():
    """Create and setup a coordinator for testing"""
    coord = MasterCoordinator()
    await coord.setup()
    yield coord
    await coord.cleanup()

@pytest_asyncio.fixture
async def mock_agent():
    """Create a mock agent for testing"""
    agent = MockAgent()
    await agent.setup()
    yield agent
    await agent.cleanup()

# Test Cases
@pytest.mark.asyncio
async def test_coordinator_initialization(coordinator):
    """Test coordinator initializes correctly"""
    assert coordinator.status == CoordinatorStatus.RUNNING
    assert isinstance(coordinator.task_queue, asyncio.Queue)
    assert coordinator.agent_id == "master_coordinator"
    assert AgentCapability.COORDINATION in coordinator.capabilities

@pytest.mark.asyncio
async def test_agent_registration(coordinator, mock_agent):
    """Test agent registration process"""
    # Test successful registration
    success = await coordinator.register_agent(mock_agent)
    assert success is True
    assert mock_agent.agent_id in coordinator.registered_agents

    # Test duplicate registration
    success = await coordinator.register_agent(mock_agent)
    assert success is False

@pytest.mark.asyncio
async def test_agent_deregistration(coordinator, mock_agent):
    """Test agent deregistration process"""
    # Register agent first
    await coordinator.register_agent(mock_agent)
    
    # Test successful deregistration
    success = await coordinator.deregister_agent(mock_agent.agent_id)
    assert success is True
    assert mock_agent.agent_id not in coordinator.registered_agents

    # Test deregistering non-existent agent
    success = await coordinator.deregister_agent("non_existent_agent")
    assert success is False

@pytest.mark.asyncio
async def test_task_submission(coordinator):
    """Test task submission process"""
    task_data = {"type": "semantic", "content": "test task"}
    task_id = await coordinator.submit_task(task_data)
    
    assert task_id is not None
    assert coordinator.task_queue.qsize() == 1

@pytest.mark.asyncio
async def test_task_processing(coordinator, mock_agent):
    """Test task processing"""
    # Setup coordinator with mock agent
    coordinator.coordinator_agents["semantic"] = mock_agent
    
    # Submit a task
    task_data = {"type": "semantic", "content": "test task"}
    task_id = await coordinator.submit_task(task_data)
    
    # Process the task
    await coordinator.process_tasks()
    
    # Verify task was processed
    assert mock_agent.process_task_called

@pytest.mark.asyncio
async def test_coordinator_status(coordinator, mock_agent):
    """Test status reporting"""
    await coordinator.register_agent(mock_agent)
    await coordinator.submit_task({"type": "test"})
    
    status = await coordinator.get_status()
    assert status["status"] == "RUNNING"
    assert status["registered_agents"] == 1
    assert status["pending_tasks"] == 1

@pytest.mark.asyncio
async def test_health_check(coordinator, mock_agent):
    """Test health check functionality"""
    await coordinator.register_agent(mock_agent)
    
    # Simulate unhealthy agent
    mock_agent.status = "STOPPED"
    
    # Force health check
    await coordinator._check_agent_health()
    
    # Verify unhealthy agent was deregistered
    assert mock_agent.agent_id not in coordinator.registered_agents

@pytest.mark.asyncio
async def test_message_processing(coordinator):
    """Test message processing"""
    # Test valid message
    message = {
        "type": "get_status",
        "data": {}
    }
    response = await coordinator.process_message(message)
    assert response["status"] == "success"
    
    # Test invalid message
    message = {
        "type": "invalid_type",
        "data": {}
    }
    response = await coordinator.process_message(message)
    assert response["status"] == "error"

@pytest.mark.asyncio
async def test_coordinator_start_stop(coordinator):
    """Test coordinator start and stop"""
    # Test start
    success = await coordinator.start()
    assert success is True
    assert coordinator.status == CoordinatorStatus.RUNNING
    
    # Test stop
    await coordinator.stop()
    assert coordinator.status == CoordinatorStatus.STOPPED

@pytest.mark.asyncio
async def test_error_handling(coordinator):
    """Test error handling in task processing"""
    # Create a task that will cause an error
    task_data = {"type": "unknown", "content": "test task"}
    task_id = await coordinator.submit_task(task_data)
    
    # Process the task
    await coordinator.process_tasks()
    
    # Verify task queue is empty (task was processed despite error)
    assert coordinator.task_queue.empty()

# Helper function to simulate tasks
async def submit_multiple_tasks(coordinator, count):
    """Helper function to submit multiple tasks"""
    task_ids = []
    for i in range(count):
        task_data = {"type": "semantic", "content": f"test task {i}"}
        task_id = await coordinator.submit_task(task_data)
        task_ids.append(task_id)
    return task_ids

@pytest.mark.asyncio
async def test_multiple_task_processing(coordinator, mock_agent):
    """Test processing multiple tasks"""
    coordinator.coordinator_agents["semantic"] = mock_agent
    task_ids = await submit_multiple_tasks(coordinator, 3)
    
    # Process tasks
    await coordinator.process_tasks()
    
    # Verify all tasks were processed
    assert coordinator.task_queue.empty()