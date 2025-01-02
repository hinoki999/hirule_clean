# tests/integration/test_coordinator_integration.py
import pytest
import pytest_asyncio
from src.agents.master_coordinator import MasterCoordinator
from src.agents.semantic_agent import SemanticAgent
from tests.test_agents.test_helpers import AgentTestHarness, submit_test_tasks

@pytest_asyncio.fixture
async def integrated_system():
    #"""Setup a complete integrated system#"""
    coord = MasterCoordinator()
    semantic_agent = SemanticAgent()
    harness = AgentTestHarness(coord)

    await coord.setup()
    await semantic_agent.setup()
    await coord.register_agent(semantic_agent)

    yield {
        "coordinator": coord,
        "semantic_agent": semantic_agent,
        "harness": harness
    }

    await coord.cleanup()
    await semantic_agent.cleanup()

@pytest.mark.asyncio
async def test_full_task_lifecycle(integrated_system):
    #"""Test complete task lifecycle#"""
    coordinator = integrated_system["coordinator"]
    semantic_agent = integrated_system["semantic_agent"]
    harness = integrated_system["harness"]

    # Submit a task
    task = {
        "type": "semantic",
        "content": "test task",
        "priority": 1
    }

    task_id = await coordinator.submit_task(task)
    assert task_id is not None

    # Process the task
    await coordinator.process_tasks()

    # Verify results
    status = await coordinator.get_status()
    assert status["pending_tasks"] == 0
    assert len(harness.errors) == 0


