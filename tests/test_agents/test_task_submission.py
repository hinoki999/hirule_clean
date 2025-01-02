import pytest
import pytest_asyncio
import asyncio
import logging
from src.agents.master_coordinator import MasterCoordinator
from tests.test_agents.test_helpers import AgentTestHarness
from tests.test_agents.mock_agent import MockAgent

@pytest_asyncio.fixture
async def test_env():
    #"""Setup test environment with coordinator and harness#"""
    coordinator = MasterCoordinator()
    harness = AgentTestHarness(coordinator)
    await coordinator.setup()
    yield {...}
    await coordinator.cleanup()

    try:
        await coordinator.setup()
        logging.info("Test environment setup complete")

        yield {
            "coordinator": coordinator,
            "harness": harness
        }
    except Exception as e:
        logging.error(f"Error during test environment setup: {e}")
        raise
    finally:
        try:
            await coordinator.cleanup()
            # Ensure all tasks are cleaned up
            pending = [t for t in asyncio.all_tasks()
                      if t is not asyncio.current_task()]
            if pending:
                await asyncio.gather(*pending, return_exceptions=True)
        except Exception as e:
            logging.error(f"Error during cleanup: {e}")

@pytest.mark.asyncio
class TestTaskSubmission:
    async def test_single_task_submission(self, test_env):
        coordinator = test_env["coordinator"]
        harness = test_env["harness"]

        agent = MockAgent("task_handler_1")
        try:
            await agent.setup()
            await coordinator.register_agent(agent)

            task = {
                "type": "semantic",
                "content": "test task",
                "priority": 1
            }

            task_id = await coordinator.submit_task(task)
            harness.record_event({
                "type": "task_submission",
                "task_id": task_id,
                "task_data": task
            })

            assert task_id is not None, "Task ID should be generated"
            assert coordinator.task_queue.qsize() == 1, "Task queue should contain exactly one task"

            # Verify task is properly queued
            queued_task = await coordinator.task_queue.get()
            assert queued_task["type"] == task["type"], "Task type mismatch"
            assert queued_task["content"] == task["content"], "Task content mismatch"

        except Exception as e:
            harness.record_error(e)
            raise
        finally:
            await agent.cleanup()

    async def test_priority_ordering(self, test_env):
        coordinator = test_env["coordinator"]
        harness = test_env["harness"]

        agent = MockAgent("priority_handler")
        try:
            await agent.setup()
            await coordinator.register_agent(agent)

            tasks = [
                {"type": "semantic", "content": "high priority", "priority": 0},
                {"type": "semantic", "content": "medium priority", "priority": 1},
                {"type": "semantic", "content": "low priority", "priority": 2}
            ]

            task_ids = []
            for task in tasks:
                task_id = await coordinator.submit_task(task)
                task_ids.append(task_id)
                harness.record_event({
                    "type": "priority_task_submission",
                    "task_id": task_id,
                    "priority": task["priority"]
                })

            assert coordinator.task_queue.qsize() == 3, "All tasks should be queued"

            processed_tasks = []
            async with asyncio.timeout(2.0):  # Add timeout for task processing
                while not coordinator.task_queue.empty():
                    task = await coordinator.task_queue.get()
                    harness.record_event({
                        "type": "task_processing_order",
                        "task_id": task.get("task_id"),
                        "task_data": task
                    })
                    processed_tasks.append(task)

            # Detailed verification of priority ordering
            for i in range(1, len(processed_tasks)):
                current_priority = processed_tasks[i].get("priority")
                previous_priority = processed_tasks[i-1].get("priority")
                assert current_priority is not None, f"Priority missing in task {i}"
                assert previous_priority is not None, f"Priority missing in task {i-1}"
                assert current_priority >= previous_priority, 
                    f"Priority ordering violated at position {i}: {previous_priority} -> {current_priority}"

        except asyncio.TimeoutError:
            harness.record_error("Timeout while processing priority tasks")
            raise
        except Exception as e:
            harness.record_error(e)
            raise
        finally:
            await agent.cleanup()

    async def test_task_validation(self, test_env):
        coordinator = test_env["coordinator"]
        harness = test_env["harness"]

        invalid_tasks = [
            {},  # Empty task
            {"type": "unknown"},  # Unknown type
            {"type": "semantic"}  # Missing required fields
        ]

        for i, task in enumerate(invalid_tasks):
            try:
                task_id = await coordinator.submit_task(task)
                harness.record_event({
                    "type": "invalid_task_submission",
                    "task_index": i,
                    "task": task,
                    "result": task_id
                })
                # If we get here, the validation didn't catch an invalid task
                pytest.fail(f"Invalid task {i} was accepted: {task}")
            except Exception as e:
                harness.record_error({
                    "task_index": i,
                    "task": task,
                    "error": str(e)
                })
                # Here we expect an exception for invalid tasks
                assert isinstance(e, (ValueError, TypeError)), 
                    f"Unexpected error type for invalid task: {type(e)}"


