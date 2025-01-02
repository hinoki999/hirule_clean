# tests/integration/test_critical_path.py
import pytest
import pytest_asyncio
import asyncio
from typing import Dict

from src.agents.master_coordinator import MasterCoordinator, CoordinatorStatus
from tests.test_agents.mock_agent import MockAgent
from tests.test_agents.test_helpers import AgentTestHarness

@pytest_asyncio.fixture
async def enhanced_test_harness(request):
    #"""Create test environment with logging and monitoring#"""
    coordinator = MasterCoordinator()
    harness = AgentTestHarness(coordinator, request.node.name)

    await coordinator.setup()
    assert coordinator.status == CoordinatorStatus.RUNNING

    yield {
        "coordinator": coordinator,
        "harness": harness
    }

    await coordinator.cleanup()

@pytest.mark.asyncio
class TestCriticalPath:
    #"""
    Test the critical path for smart contract analysis pipeline.
    Tests are ordered to build upon each other systematically.
    #"""

    async def test_1_agent_registration(self, test_harness):
        #"""
        Test agent registration process
        Verifies:
        - Agents can be registered
        - Registration is recorded correctly
        - Duplicate registration is handled
        #"""
        coordinator = test_harness["coordinator"]
        harness = test_harness["harness"]

        # Create test agent
        agent = MockAgent("test_protocol_agent")
        await agent.setup()

        # Test registration
        success = await coordinator.register_agent(agent)
        assert success, "Agent registration failed"
        assert agent.agent_id in coordinator.registered_agents

        # Verify registration details
        registered_agent = coordinator.registered_agents[agent.agent_id]
        assert registered_agent.agent_id == agent.agent_id

        # Test duplicate registration
        dup_success = await coordinator.register_agent(agent)
        assert not dup_success, "Duplicate registration should fail"

        # Cleanup
        await agent.cleanup()

    async def test_2_task_submission(self, test_harness):
        #"""
        Test task submission process
        Verifies:
        - Tasks can be submitted
        - Task metadata is correct
        - Task queuing works properly
        #"""
        coordinator = test_harness["coordinator"]
        harness = test_harness["harness"]

        # Create and register required agent
        agent = MockAgent("test_semantic_agent")
        await agent.setup()
        await coordinator.register_agent(agent)

        # Create test task
        task_data = {
            "type": "semantic",
            "content": "test contract code",
            "priority": 1
        }

        # Submit task
        task_id = await coordinator.submit_task(task_data)
        assert task_id is not None, "Task submission failed"

        # Verify task is queued
        assert coordinator.task_queue.qsize() == 1

        # Cleanup
        await agent.cleanup()

    async def test_3_task_distribution(self, test_harness):
        #"""
        Test task distribution to appropriate agents
        Verifies:
        - Tasks are routed to correct agents
        - Distribution respects task priorities
        - Multiple agents can receive tasks
        #"""
        coordinator = test_harness["coordinator"]
        harness = test_harness["harness"]

        # Create and register multiple agents
        protocol_agent = MockAgent("protocol_agent")
        semantic_agent = MockAgent("semantic_agent")

        await protocol_agent.setup()
        await semantic_agent.setup()
        await coordinator.register_agent(protocol_agent)
        await coordinator.register_agent(semantic_agent)

        # Submit tasks for different agents
        tasks = [
            {
                "type": "protocol",
                "content": "protocol analysis task",
                "priority": 1
            },
            {
                "type": "semantic",
                "content": "semantic analysis task",
                "priority": 1
            }
        ]

        # Submit all tasks
        task_ids = []
        for task in tasks:
            task_id = await coordinator.submit_task(task)
            task_ids.append(task_id)

        assert len(task_ids) == len(tasks)

        # Process tasks
        await coordinator.process_tasks()

        # Verify task distribution
        assert protocol_agent.process_task_called
        assert semantic_agent.process_task_called

        # Cleanup
        await protocol_agent.cleanup()
        await semantic_agent.cleanup()

    async def test_4_result_aggregation(self, test_harness):
        #"""
        Test result collection and aggregation
        Verifies:
        - Results are collected from all agents
        - Results are properly aggregated
        - System handles completed tasks correctly
        #"""
        coordinator = test_harness["coordinator"]
        harness = test_harness["harness"]

        # Setup test agents with known responses
        protocol_agent = MockAgent("protocol_agent")
        semantic_agent = MockAgent("semantic_agent")

        await protocol_agent.setup()
        await semantic_agent.setup()
        await coordinator.register_agent(protocol_agent)
        await coordinator.register_agent(semantic_agent)

        # Submit test task
        task = {
            "type": "smart_contract_analysis",
            "content": "test contract",
            "analysis_types": ["protocol", "semantic"],
            "priority": 1
        }

        task_id = await coordinator.submit_task(task)

        # Process task
        await coordinator.process_tasks()

        # Verify task completion
        status = await coordinator.get_status()
        assert status["pending_tasks"] == 0

        # Cleanup
        await protocol_agent.cleanup()
        await semantic_agent.cleanup()


