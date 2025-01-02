# test_blockchain_coordinator.py (maintaining full robustness)
import pytest
import logging
import asyncio
from src.agents.blockchain_coordinator import BlockchainCoordinator
from src.agents.blockchain.validator_agent import ValidatorAgent
from src.agents.blockchain.consensus_agent import ConsensusAgent

@pytest.fixture
async def coordinator():
    #"""Setup and teardown of blockchain coordinator with proper cleanup#"""
    coordinator = BlockchainCoordinator()
    logging.info("Test setup complete")
    yield coordinator

    try:
        await coordinator.stop()
    except Exception as e:
        logging.error(f"Error during teardown: {e}")
    finally:
        # Get all running tasks except current
        pending = [t for t in asyncio.all_tasks()
                  if t is not asyncio.current_task()
                  and not t.done()]

        if pending:
            for task in pending:
                task.cancel()
                try:
                    await asyncio.wait_for(asyncio.shield(task), timeout=1.0)
                except (asyncio.CancelledError, asyncio.TimeoutError):
                    pass

        logging.info("Test teardown complete")

@pytest.mark.asyncio
async def test_blockchain_coordinator(coordinator):
    # Test initialization with detailed logging
    assert coordinator.agent_id is not None, "Coordinator ID should be initialized"
    assert len(coordinator.blockchain_agents) == 0, "Initial agent count should be 0"
    logging.info("Initialization test passed")

    # Test agent registration with proper verification
    validator_agent = ValidatorAgent()
    consensus_agent = ConsensusAgent()

    success = coordinator.register_agent(validator_agent)
    assert success, "Validator agent registration failed"
    success = coordinator.register_agent(consensus_agent)
    assert success, "Consensus agent registration failed"

    assert len(coordinator.blockchain_agents) == 2, "Expected exactly 2 registered agents"
    logging.info("Agent registration tests passed")

    # Test coordinator operations with proper startup verification
    await coordinator.start()
    assert coordinator.is_running, "Coordinator should be running after start"
    logging.info("Coordinator start test passed")

    # Test task submission with complete error handling
    task = {
        "type": "validate_block",
        "block_data": "Test block data",
        "timestamp": "2024-12-20T21:00:00Z"
    }
    try:
        task_id = await coordinator.submit_task(task)
        assert task_id is not None, "Task ID should be generated"

        # Allow time for task processing with timeout
        async with asyncio.timeout(1.0):
            await asyncio.sleep(0.5)

    except asyncio.TimeoutError:
        pytest.fail("Task processing timeout")
    except Exception as e:
        pytest.fail(f"Task processing failed: {str(e)}")

    # Verify proper shutdown
    await coordinator.stop()
    assert not coordinator.is_running, "Coordinator should not be running after stop"
    logging.info("All tests completed successfully")


