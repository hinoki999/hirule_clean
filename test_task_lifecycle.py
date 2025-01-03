<<<<<<< ours
import asyncio
import logging
import os
import sys
from pathlib import Path

# Add the src directory to the Python path
current_dir = Path(__file__).parent
src_path = str(current_dir / "src")
sys.path.insert(0, src_path)

# Import necessary classes
from src.agents.task_management import TaskTracker, TaskPriority, TaskStatus
from src.agents.coordinator import MasterCoordinator

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    datefmt="%Y-%m-%d %H:%M:%S",
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("test_task_lifecycle.log")
    ]
)

async def test_task_registration():
    #"""Simulates task registration and logs the lifecycle.#"""
    try:
        # Create TaskTracker instance directly for testing
        task_tracker = TaskTracker()

        # Create a test task
        task = task_tracker.create_task(
            required_capability="test_capability",
            priority=TaskPriority.HIGH,
            payload={"description": "Test task"}
        )

        logging.info(f"Task {task.task_id} created with priority {task.priority}.")

        # Update task status
        await task_tracker.update_task_status(task.task_id, TaskStatus.COMPLETED)
        logging.info(f"Task {task.task_id} marked as completed.")

        logging.info("Task lifecycle tested successfully.")

    except Exception as e:
        logging.error(f"Error during task lifecycle test: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(test_task_registration())


||||||| base
=======
import asyncio
import logging
import os
import sys
from pathlib import Path

# Add the src directory to the Python path
current_dir = Path(__file__).parent
src_path = str(current_dir / "src")
sys.path.insert(0, src_path)

# Import necessary classes
from src.agents.task_management import TaskTracker, TaskPriority, TaskStatus
from src.agents.coordinator import MasterCoordinator

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    datefmt="%Y-%m-%d %H:%M:%S",
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("test_task_lifecycle.log")
    ]
)

async def test_task_registration():
    """Simulates task registration and logs the lifecycle."""
    try:
        # Create TaskTracker instance directly for testing
        task_tracker = TaskTracker()
        
        # Create a test task
        task = task_tracker.create_task(
            required_capability="test_capability",
            priority=TaskPriority.HIGH,
            payload={"description": "Test task"}
        )
        
        logging.info(f"Task {task.task_id} created with priority {task.priority}.")
        
        # Update task status
        await task_tracker.update_task_status(task.task_id, TaskStatus.COMPLETED)
        logging.info(f"Task {task.task_id} marked as completed.")
        
        logging.info("Task lifecycle tested successfully.")
        
    except Exception as e:
        logging.error(f"Error during task lifecycle test: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(test_task_registration())
>>>>>>> theirs
