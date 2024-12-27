import asyncio
import logging
from typing import Dict, Any, List
import openai
from src.agents.task_management import Task, TaskPriority, TaskStatus, TaskTracker
from src.core.protocol import CommunicationProtocol, ProtocolMessageType
from src.core.utils import SystemMetrics
from src.agents.capability import CapabilityRegistry

class MasterCoordinator:
    """
    Master Coordinator enhanced with caching, task prioritization, protocol handling,
    and GPT-4 integration for task reasoning and optimization.
    """

    def __init__(self, *args, **kwargs):
        # Initialize core components
        self.capability_registry = CapabilityRegistry()
        self.task_tracker = TaskTracker()
        self.protocol = CommunicationProtocol()
        self.agent_registry: Dict[str, Dict[str, Any]] = {}
        self.performance_metrics: Dict[str, Dict[str, float]] = {}
        self.task_cache: Dict[str, Task] = {}
        self.completed_cache: Dict[str, Task] = {}
        self.cache_limit = 1000  # Cache limit for tasks
        self.logger = logging.getLogger(__name__)
        self.metrics = SystemMetrics()

        # GPT-4 integration
        self.openai_api_key = kwargs.get("openai_api_key", None)
        if not self.openai_api_key:
            raise ValueError("OpenAI API key not provided. Ensure 'openai_api_key' is set in the initialization.")
        openai.api_key = self.openai_api_key

    async def try_assign_task(self, task: Task) -> bool:
        """
        Attempt to assign a task to a capable agent.
        """
        try:
            capable_agents = [
                agent_id
                for agent_id, info in self.agent_registry.items()
                if task.required_capability in info.get("capabilities", [])
            ]

            if not capable_agents:
                self.logger.warning(f"No capable agents found for task {task.task_id}.")
                return False

            best_agent = capable_agents[0]  # Select the first capable agent
            await self.assign_task_to_agent(best_agent, task)
            self.logger.info(f"Task {task.task_id} assigned to agent {best_agent}.")
            return True
        except Exception as e:
            self.logger.error(f"Error assigning task {task.task_id}: {e}")
            return False

    async def assign_task_to_agent(self, agent_id: str, task: Task):
        """
        Assign a task to an agent and notify them.
        """
        try:
            task.status = TaskStatus.ASSIGNED
            task.assigned_agent = agent_id
            self.task_cache[task.task_id] = task
            await self.protocol.send_message(
                recipient=agent_id,
                message_type=ProtocolMessageType.TASK_ASSIGNMENT,
                payload={"task_id": task.task_id, "task_data": task.payload},
            )
            self.logger.info(f"Task {task.task_id} successfully sent to agent {agent_id}.")
        except Exception as e:
            self.logger.error(f"Error sending task {task.task_id} to agent {agent_id}: {e}")
