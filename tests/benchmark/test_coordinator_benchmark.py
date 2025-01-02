<<<<<<< ours
# tests/benchmark/test_coordinator_benchmark.py
import pytest
import pytest_asyncio
import time
from src.agents.master_coordinator import MasterCoordinator
from src.agents.base import BaseAgent, AgentCapability  # Updated import
from tests.test_agents.test_helpers import submit_test_tasks  # Updated import
from tests.test_agents.mock_agent import MockAgent

@pytest_asyncio.fixture
async def coordinator():
    #"""Create and setup a coordinator for testing#"""
    coord = MasterCoordinator()
    await coord.setup()
    yield coord
    await coord.cleanup()

@pytest_asyncio.fixture
async def mock_agent():
    #"""Create a mock agent for testing#"""
    agent = MockAgent()
    await agent.setup()
    yield agent
    await agent.cleanup()

@pytest.mark.benchmark
@pytest.mark.asyncio
async def test_coordinator_performance(coordinator, mock_agent):
    #"""Benchmark coordinator performance#"""
    start_time = time.time()

    # Setup
    await coordinator.register_agent(mock_agent)

    # Submit and process 100 tasks
    tasks = []
    for i in range(100):
        task = {
            "type": "test",
            "content": f"test_task_{i}",
            "priority": i % 3
        }
        task_id = await coordinator.submit_task(task)
        tasks.append(task_id)

    # Process tasks
    await coordinator.process_tasks()

    execution_time = time.time() - start_time

    # Assertions
    assert execution_time < 1.0  # Should complete in under 1 second
    assert coordinator.task_queue.empty()


||||||| base
=======
# tests/benchmark/test_coordinator_benchmark.py
import pytest
import pytest_asyncio
import time
from src.agents.master_coordinator import MasterCoordinator
from src.agents.base import BaseAgent, AgentCapability  # Updated import
from tests.test_agents.test_helpers import submit_test_tasks  # Updated import
from tests.test_agents.mock_agent import MockAgent

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

@pytest.mark.benchmark
@pytest.mark.asyncio
async def test_coordinator_performance(coordinator, mock_agent):
    """Benchmark coordinator performance"""
    start_time = time.time()
    
    # Setup
    await coordinator.register_agent(mock_agent)
    
    # Submit and process 100 tasks
    tasks = []
    for i in range(100):
        task = {
            "type": "test",
            "content": f"test_task_{i}",
            "priority": i % 3
        }
        task_id = await coordinator.submit_task(task)
        tasks.append(task_id)
    
    # Process tasks
    await coordinator.process_tasks()
    
    execution_time = time.time() - start_time
    
    # Assertions
    assert execution_time < 1.0  # Should complete in under 1 second
    assert coordinator.task_queue.empty()
>>>>>>> theirs
