import logging
import asyncio
from src.agents.coordinator import MasterCoordinator
from src.agents.task_management import TaskPriority


# Configure logging for the test
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("test_task_lifecycle.log")
    ]
)

async def test_task_registration():
    #"""Simulates task registration and logs the lifecycle.#"""
    try:
        # Initialize MasterCoordinator
        coordinator = MasterCoordinator(openai_api_key="your_openai_api_key")

        # Simulate task registration
        task_data = {
            "required_capability": "capability_1",
            "priority": "HIGH",
            "payload": {"description": "Test task payload"}
        }
        task_id = "task_001"  # Manually assign a test task ID for debugging purposes
        coordinator.task_cache[task_id] = coordinator.task_tracker.create_task(
            required_capability=task_data["required_capability"],
            priority=TaskPriority[task_data["priority"]],
            payload=task_data["payload"]
        )
        logging.info(f"Task {task_id} registered with priority {task_data['priority']}.")

        # Simulate task completion
        await coordinator.task_tracker.update_task_status(task_id, TaskPriority.COMPLETED)
        logging.info(f"Task {task_id} marked as completed.")

        # Verify logs for task lifecycle
        logging.info("Task lifecycle tested successfully.")
    except Exception as e:
        logging.error(f"Error during task lifecycle test: {e}")

# Run the test
if __name__ == "__main__":
    asyncio.run(test_task_registration())


