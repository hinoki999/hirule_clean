# tests/stress/test_coordinator_stress.py
# tests/stress/test_coordinator_stress.py
import pytest
import pytest_asyncio
import asyncio
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

@pytest.mark.stress
@pytest.mark.asyncio
async def test_coordinator_under_load(coordinator, mock_agent):
    #"""Test coordinator under heavy load#"""
    # Register multiple agents
    agents = [mock_agent for _ in range(10)]
    for agent in agents:
        await coordinator.register_agent(agent)

    # Submit many tasks
    task_count = 1000
    task_ids = await submit_test_tasks(coordinator, task_count)

    # Process tasks with timeout
    try:
        async with asyncio.timeout(30):  # 30 second timeout
            await coordinator.process_tasks()
    except asyncio.TimeoutError:
        pytest.fail("Task processing timed out")

    # Verify system stability
    status = await coordinator.get_status()
    assert status["status"] == "RUNNING"
    assert status["pending_tasks"] == 0


