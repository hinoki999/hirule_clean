<<<<<<< ours
# tests/test_agents/test_basic_initialization.py
import pytest
import pytest_asyncio
import asyncio
from src.agents.master_coordinator import MasterCoordinator, CoordinatorStatus
from tests.test_agents.test_helpers import AgentTestHarness

@pytest_asyncio.fixture
async def test_env():
    #"""Basic test environment setup#"""
    coordinator = MasterCoordinator()
    harness = AgentTestHarness(coordinator)

    # Setup
    await coordinator.setup()
    assert coordinator.status == CoordinatorStatus.RUNNING

    yield {
        "coordinator": coordinator,
        "harness": harness
    }

    # Ensure proper cleanup
    try:
        await coordinator.cleanup()
        # Allow a brief moment for tasks to clean up
        await asyncio.sleep(0.1)
    except Exception as e:
        print(f"Cleanup error: {str(e)}")

@pytest.mark.asyncio
async def test_coordinator_initialization(test_env):
    #"""Verify basic coordinator initialization#"""
    coordinator = test_env["coordinator"]
    harness = test_env["harness"]

    # Test basic initialization
    status = await coordinator.get_status()
    harness.record_event({
        "type": "initialization_check",
        "status": status
    })

    assert status["status"] == "RUNNING"

    # Verify initial state
    assert len(coordinator.registered_agents) == 0
    assert coordinator.task_queue.empty()

    # Verify health check task is running
    assert hasattr(coordinator, '_health_check_task')
    assert not coordinator._health_check_task.done()


||||||| base
=======
# tests/test_agents/test_basic_initialization.py
import pytest
import pytest_asyncio
import asyncio
from src.agents.master_coordinator import MasterCoordinator, CoordinatorStatus
from tests.test_agents.test_helpers import AgentTestHarness

@pytest_asyncio.fixture
async def test_env():
    """Basic test environment setup"""
    coordinator = MasterCoordinator()
    harness = AgentTestHarness(coordinator)
    
    # Setup
    await coordinator.setup()
    assert coordinator.status == CoordinatorStatus.RUNNING
    
    yield {
        "coordinator": coordinator,
        "harness": harness
    }
    
    # Ensure proper cleanup
    try:
        await coordinator.cleanup()
        # Allow a brief moment for tasks to clean up
        await asyncio.sleep(0.1)
    except Exception as e:
        print(f"Cleanup error: {str(e)}")

@pytest.mark.asyncio
async def test_coordinator_initialization(test_env):
    """Verify basic coordinator initialization"""
    coordinator = test_env["coordinator"]
    harness = test_env["harness"]
    
    # Test basic initialization
    status = await coordinator.get_status()
    harness.record_event({
        "type": "initialization_check",
        "status": status
    })
    
    assert status["status"] == "RUNNING"
    
    # Verify initial state
    assert len(coordinator.registered_agents) == 0
    assert coordinator.task_queue.empty()
    
    # Verify health check task is running
    assert hasattr(coordinator, '_health_check_task')
    assert not coordinator._health_check_task.done()
>>>>>>> theirs
