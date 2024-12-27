# tests/test_agents/test_helpers.py
import asyncio
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
from src.agents.base import BaseAgent

# Setup basic logging
def setup_test_logging(test_name: str) -> logging.Logger:
    """Setup logging for tests"""
    log_dir = Path("tests/logs")
    log_dir.mkdir(exist_ok=True)
    
    logger = logging.getLogger(test_name)
    logger.setLevel(logging.DEBUG)
    
    # Add file handler with timestamps
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"{test_name}_{timestamp}.log"
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger

# Existing helper functions with enhanced logging
async def register_multiple_agents(coordinator, agents: List[BaseAgent]) -> List[bool]:
    """
    Helper to register multiple agents with the coordinator
    Returns a list of registration results
    """
    logger = setup_test_logging("agent_registration")
    results = []
    
    for agent in agents:
        try:
            result = await coordinator.register_agent(agent)
            results.append(result)
            logger.info(f"Agent {agent.agent_id} registration: {'success' if result else 'failed'}")
        except Exception as e:
            logger.error(f"Error registering agent {agent.agent_id}: {str(e)}")
            results.append(False)
            
    return results

async def submit_test_tasks(
    coordinator, 
    count: int, 
    task_type: str = "semantic",
    base_priority: int = 0
) -> List[str]:
    """
    Submit multiple test tasks to the coordinator
    
    Args:
        coordinator: The coordinator to submit tasks to
        count: Number of tasks to submit
        task_type: Type of tasks to create
        base_priority: Base priority level (0-2)
    
    Returns:
        List of task IDs
    """
    logger = setup_test_logging("task_submission")
    
    tasks = [
        {
            "type": task_type,
            "content": f"test_task_{i}",
            "priority": (i + base_priority) % 3
        }
        for i in range(count)
    ]
    
    task_ids = []
    for task in tasks:
        try:
            task_id = await coordinator.submit_task(task)
            task_ids.append(task_id)
            logger.info(f"Task submitted successfully: {task_id}")
        except Exception as e:
            logger.error(f"Error submitting task: {str(e)}")
            task_ids.append(None)
    
    return task_ids

class AgentTestHarness:
    """Test harness for simulating agent behavior and recording test events"""
    
    def __init__(self, coordinator):
        self.coordinator = coordinator
        self.events: List[Dict] = []
        self.errors: List[Exception] = []
        self.logger = setup_test_logging(f"harness_{coordinator.agent_id}")
        self.start_time = asyncio.get_running_loop().time()

    def record_event(self, event: Dict) -> None:
        """Record a test event"""
        event["timestamp"] = asyncio.get_running_loop().time()
        self.events.append(event)
        self.logger.info(f"Event recorded: {event}")

    def record_error(self, error: Exception) -> None:
        """Record a test error"""
        self.errors.append(error)
        error_event = {
            "type": "error",
            "error": str(error),
            "traceback": getattr(error, "__traceback__", None)
        }
        self.record_event(error_event)
        self.logger.error(f"Error recorded: {str(error)}", exc_info=True)

    async def simulate_agent_failure(self, agent_id: str) -> bool:
        """
        Simulate an agent failing
        
        Args:
            agent_id: ID of the agent to fail
            
        Returns:
            bool: Whether the simulation was successful
        """
        self.logger.info(f"Simulating failure for agent: {agent_id}")
        
        agent = self.coordinator.registered_agents.get(agent_id)
        if not agent:
            error = ValueError(f"Agent {agent_id} not found")
            self.record_error(error)
            return False
            
        agent.status = "FAILED"
        self.record_event({
            "type": "agent_failure",
            "agent_id": agent_id,
            "time_since_start": asyncio.get_running_loop().time() - self.start_time
        })
        
        await self.coordinator._check_agent_health()
        self.logger.info(f"Agent {agent_id} failure simulation complete")
        return True

    def get_events_by_type(self, event_type: str) -> List[Dict]:
        """Get all events of a specific type"""
        events = [e for e in self.events if e["type"] == event_type]
        self.logger.debug(f"Retrieved {len(events)} events of type: {event_type}")
        return events

    def clear_records(self) -> None:
        """Clear all recorded events and errors"""
        self.logger.info(f"Clearing {len(self.events)} events and {len(self.errors)} errors")
        self.events.clear()
        self.errors.clear()

    async def verify_coordinator_state(self) -> Dict:
        """Verify coordinator state and log results"""
        status = await self.coordinator.get_status()
        self.logger.info(f"Coordinator status: {status}")
        return status

    def get_test_duration(self) -> float:
        """Get duration since test harness initialization"""
        return asyncio.get_running_loop().time() - self.start_time