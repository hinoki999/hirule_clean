<<<<<<< ours
import asyncio
import logging
from src.agents.coordinator import MasterCoordinator
from src.agents.task_management import Task, TaskPriority
# Mock setup
async def test_task_assignment():
    logging.basicConfig(level=logging.INFO)

    # Initialize MasterCoordinator
    coordinator = MasterCoordinator(openai_api_key="your_openai_api_key")

    # Mock agent registry
    coordinator.agent_registry = {
        "agent_1": {"capabilities": ["capability_1"]},
        "agent_2": {"capabilities": ["capability_2"]},
    }

    # Register a task
    task_data = Task(
        task_id="task_001",
        priority=TaskPriority.HIGH,
        required_capability="capability_1",
        status="PENDING",
        assigned_agent=None,
        created_at=0,
        started_at=None,
        completed_at=None,
        estimated_load=0.1,
        actual_load=None,
        dependencies=[],
        payload={"description": "Test task payload"},
    )
    coordinator.task_cache[task_data.task_id] = task_data

    # Try assigning the task
    assigned = await coordinator.try_assign_task(task_data)
    if assigned:
        logging.info(f"Task {task_data.task_id} successfully assigned!")
    else:
        logging.warning(f"Task {task_data.task_id} could not be assigned.")

# Run the test
if __name__ == "__main__":
    asyncio.run(test_task_assignment())

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("test_mock_agent.log")
    ]
)

class MockAgent:
    #"""Mock agent for testing the MasterCoordinator.#"""
    def __init__(self, agent_id, capabilities):
        self.agent_id = agent_id
        self.capabilities = capabilities

    async def heartbeat(self):
        #"""Simulate sending a heartbeat signal.#"""
        logging.info(f"Agent {self.agent_id} is alive.")

async def simulate_agents():
    #"""Simulate mock agents and their interactions.#"""
    agents = [
        MockAgent("agent_1", ["capability_1"]),
        MockAgent("agent_2", ["capability_2"]),
        MockAgent("agent_3", ["capability_3"])
    ]

    for agent in agents:
        await agent.heartbeat()

if __name__ == "__main__":
    asyncio.run(simulate_agents())


||||||| base
=======
import asyncio
import logging
from src.agents.coordinator import MasterCoordinator
from src.agents.task_management import Task, TaskPriority
# Mock setup
async def test_task_assignment():
    logging.basicConfig(level=logging.INFO)

    # Initialize MasterCoordinator
    coordinator = MasterCoordinator(openai_api_key="your_openai_api_key")

    # Mock agent registry
    coordinator.agent_registry = {
        "agent_1": {"capabilities": ["capability_1"]},
        "agent_2": {"capabilities": ["capability_2"]},
    }

    # Register a task
    task_data = Task(
        task_id="task_001",
        priority=TaskPriority.HIGH,
        required_capability="capability_1",
        status="PENDING",
        assigned_agent=None,
        created_at=0,
        started_at=None,
        completed_at=None,
        estimated_load=0.1,
        actual_load=None,
        dependencies=[],
        payload={"description": "Test task payload"},
    )
    coordinator.task_cache[task_data.task_id] = task_data

    # Try assigning the task
    assigned = await coordinator.try_assign_task(task_data)
    if assigned:
        logging.info(f"Task {task_data.task_id} successfully assigned!")
    else:
        logging.warning(f"Task {task_data.task_id} could not be assigned.")

# Run the test
if __name__ == "__main__":
    asyncio.run(test_task_assignment())

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("test_mock_agent.log")
    ]
)

class MockAgent:
    """Mock agent for testing the MasterCoordinator."""
    def __init__(self, agent_id, capabilities):
        self.agent_id = agent_id
        self.capabilities = capabilities

    async def heartbeat(self):
        """Simulate sending a heartbeat signal."""
        logging.info(f"Agent {self.agent_id} is alive.")

async def simulate_agents():
    """Simulate mock agents and their interactions."""
    agents = [
        MockAgent("agent_1", ["capability_1"]),
        MockAgent("agent_2", ["capability_2"]),
        MockAgent("agent_3", ["capability_3"])
    ]

    for agent in agents:
        await agent.heartbeat()

if __name__ == "__main__":
    asyncio.run(simulate_agents())
>>>>>>> theirs
