import pytest
import pytest_asyncio
from src.agents.master_coordinator import MasterCoordinator, CoordinatorStatus
from tests.test_agents.test_helpers import AgentTestHarness
from tests.test_agents.mock_agent import MockAgent

@pytest_asyncio.fixture
async def test_env():
    coordinator = MasterCoordinator()
    harness = AgentTestHarness(coordinator)
    await coordinator.setup()

    yield {
        "coordinator": coordinator,
        "harness": harness
    }

    await coordinator.cleanup()

@pytest.mark.asyncio
class TestTaskProcessing:
    async def test_basic_task_processing(self, test_env):
        coordinator = test_env["coordinator"]
        agent = MockAgent("processor_1")
        await agent.setup()
        await coordinator.register_agent(agent)

        task_id = await coordinator.submit_task({
            "type": "semantic",
            "content": "process me",
            "priority": 1
        })

        await coordinator.process_tasks()
        assert agent.process_task_called
        assert len(agent.processed_tasks) == 1
        assert agent.processed_tasks[0]["task_id"] == task_id

        await agent.cleanup()

    async def test_task_priority_handling(self, test_env):
        coordinator = test_env["coordinator"]
        agent = MockAgent("priority_processor")
        await agent.setup()
        await coordinator.register_agent(agent)

        # Submit tasks with different priorities
        task_ids = []
        for priority in [3, 1, 2]:
            task_id = await coordinator.submit_task({
                "type": "semantic",
                "content": f"priority_{priority}",
                "priority": priority
            })
            task_ids.append(task_id)

        await coordinator.process_tasks()
        assert len(agent.processed_tasks) == 3

        # Verify processing order maintained priority
        priorities = [task["priority"] for task in agent.processed_tasks]
        assert priorities == sorted(priorities)

        await agent.cleanup()

    async def test_error_handling(self, test_env):
        coordinator = test_env["coordinator"]
        error_agent = MockAgent("error_agent")

        # Configure agent to raise an error
        async def simulate_error(task):
            raise Exception("Simulated processing error")
        error_agent.process_task = simulate_error

        await error_agent.setup()
        await coordinator.register_agent(error_agent)

        task_id = await coordinator.submit_task({
            "type": "semantic",
            "content": "error_task",
            "priority": 1
        })

        await coordinator.process_tasks()

        # Verify error was handled gracefully
        task_status = await coordinator.get_task_status(task_id)
        assert task_status["status"] == "failed"
        assert "error" in task_status

        await error_agent.cleanup()

    async def test_agent_capability_matching(self, test_env):
        coordinator = test_env["coordinator"]
        semantic_agent = MockAgent("semantic_agent", capabilities=["semantic"])
        protocol_agent = MockAgent("protocol_agent", capabilities=["protocol"])

        await semantic_agent.setup()
        await protocol_agent.setup()
        await coordinator.register_agent(semantic_agent)
        await coordinator.register_agent(protocol_agent)

        # Submit tasks for different capabilities
        semantic_task = await coordinator.submit_task({
            "type": "semantic",
            "content": "semantic task"
        })

        protocol_task = await coordinator.submit_task({
            "type": "protocol",
            "content": "protocol task"
        })

        await coordinator.process_tasks()

        # Verify tasks were routed to correct agents
        assert semantic_task in [t["task_id"] for t in semantic_agent.processed_tasks]
        assert protocol_task in [t["task_id"] for t in protocol_agent.processed_tasks]

        await semantic_agent.cleanup()
        await protocol_agent.cleanup()

    async def test_coordinator_status_changes(self, test_env):
        coordinator = test_env["coordinator"]
        agent = MockAgent("status_test_agent")
        await agent.setup()
        await coordinator.register_agent(agent)

        # Submit task while running
        task_id = await coordinator.submit_task({
            "type": "semantic",
            "content": "test task"
        })

        # Stop coordinator
        await coordinator.stop()
        assert coordinator.status == CoordinatorStatus.STOPPED

        # Verify no more tasks are processed
        new_task_id = await coordinator.submit_task({
            "type": "semantic",
            "content": "should not process"
        })

        assert new_task_id is None  # Task submission should fail when stopped

        await agent.cleanup()


