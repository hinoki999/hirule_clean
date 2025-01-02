# tests/test_agents/test_agent_registration.py
import pytest
import pytest_asyncio
from src.agents.master_coordinator import MasterCoordinator
from tests.test_agents.test_helpers import AgentTestHarness
from src.agents.base import BaseAgent, AgentCapability

class TestAgent(BaseAgent):
    #"""Simple test agent implementation#"""
    def __init__(self, agent_id: str):
        super().__init__(agent_id=agent_id, capabilities=[AgentCapability.SEMANTIC])
        self.status = "RUNNING"

    async def setup(self):
        await super().setup()

    async def cleanup(self):
        pass

    async def process_message(self, message: dict):
        return {"status": "success"}

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
class TestAgentRegistration:
    #"""Test suite for agent registration functionality#"""

    async def test_single_agent_registration(self, test_env):
        #"""Test registering a single agent#"""
        coordinator = test_env["coordinator"]
        harness = test_env["harness"]

        # Create and register agent
        agent = TestAgent("test_agent_1")
        await agent.setup()

        success = await coordinator.register_agent(agent)
        harness.record_event({
            "type": "agent_registration",
            "agent_id": agent.agent_id,
            "success": success
        })

        assert success, "Agent registration should succeed"
        assert agent.agent_id in coordinator.registered_agents

        await agent.cleanup()

    async def test_duplicate_registration(self, test_env):
        #"""Test attempting to register the same agent twice#"""
        coordinator = test_env["coordinator"]
        harness = test_env["harness"]

        agent = TestAgent("test_agent_2")
        await agent.setup()

        # First registration
        success1 = await coordinator.register_agent(agent)
        # Attempt duplicate registration
        success2 = await coordinator.register_agent(agent)

        harness.record_event({
            "type": "duplicate_registration_attempt",
            "agent_id": agent.agent_id,
            "first_attempt": success1,
            "second_attempt": success2
        })

        assert success1, "First registration should succeed"
        assert not success2, "Second registration should fail"

        await agent.cleanup()

    async def test_multiple_agent_registration(self, test_env):
        #"""Test registering multiple agents#"""
        coordinator = test_env["coordinator"]
        harness = test_env["harness"]

        # Create multiple agents
        agents = [TestAgent(f"test_agent_{i}") for i in range(3)]

        # Setup all agents
        for agent in agents:
            await agent.setup()

        # Register all agents
        results = []
        for agent in agents:
            success = await coordinator.register_agent(agent)
            results.append(success)
            harness.record_event({
                "type": "multi_agent_registration",
                "agent_id": agent.agent_id,
                "success": success
            })

        assert all(results), "All registrations should succeed"
        assert len(coordinator.registered_agents) == len(agents)

        # Cleanup
        for agent in agents:
            await agent.cleanup()


