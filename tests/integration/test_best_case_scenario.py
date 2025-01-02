# tests/integration/test_best_case_scenario.py
import pytest
import pytest_asyncio
from src.agents.master_coordinator import MasterCoordinator
from tests.test_agents.mock_agent import MockAgent

@pytest_asyncio.fixture
async def analysis_system():
    #"""Setup complete analysis system#"""
    coordinator = MasterCoordinator()
    await coordinator.setup()

    # Create specialized mock agents
    protocol_agent = MockAgent("protocol_agent")
    semantic_agent = MockAgent("semantic_agent")

    # Setup agents
    await protocol_agent.setup()
    await semantic_agent.setup()

    # Register agents
    await coordinator.register_agent(protocol_agent)
    await coordinator.register_agent(semantic_agent)

    yield {
        "coordinator": coordinator,
        "protocol_agent": protocol_agent,
        "semantic_agent": semantic_agent
    }

    # Cleanup
    await coordinator.cleanup()
    await protocol_agent.cleanup()
    await semantic_agent.cleanup()

@pytest.mark.asyncio
async def test_smart_contract_analysis_pipeline(analysis_system):
    #"""Test the complete smart contract analysis pipeline#"""
    coordinator = analysis_system["coordinator"]

    # Sample smart contract for testing
    smart_contract = #"""
    contract TestContract {
        uint256 public value;

        function setValue(uint256 _value) public {
            value = _value;
        }
    }
    #"""

    # Submit analysis task
    task = {
        "type": "smart_contract_analysis",
        "content": smart_contract,
        "analysis_types": ["security", "semantic"],
        "priority": 1
    }

    # Track start time for performance measurement
    task_id = await coordinator.submit_task(task)

    # Process the analysis
    await coordinator.process_tasks()

    # Verify results
    status = await coordinator.get_status()
    assert status["status"] == "RUNNING"
    assert status["pending_tasks"] == 0


