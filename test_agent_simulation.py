<<<<<<< ours
import asyncio
import logging
from datetime import datetime
import os
import sys
from typing import Dict, Any, List

# Add src to path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_dir, "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

# Fixed imports to match your file structure
from src.agents.capability import Capability, CapabilityRegistry
from src.agents.task_management import TaskTracker, TaskStatus, TaskPriority
from src.core.messaging import MessageBus, Message

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('agent_simulation.log')
    ]
)
logger = logging.getLogger(__name__)

class SimulatedAgent:
    #"""Simulated agent that can process tasks.#"""

    def __init__(self, agent_id: str, capabilities: List[Capability],
                 message_bus: MessageBus, task_tracker: TaskTracker):
        self.agent_id = agent_id
        self.capabilities = capabilities
        self.message_bus = message_bus
        self.task_tracker = task_tracker
        self.current_task = None
        self.running = False
        self.message_bus.register_agent(self.agent_id)

    async def start(self):
        #"""Start the agent's processing loop.#"""
        self.running = True
        self.message_bus.subscribe('task_assignment', self._handle_task_assignment)
        logger.info(f"Agent {self.agent_id} started")

        while self.running:
            if not self.current_task:
                # Look for tasks that match our capabilities
                for capability in self.capabilities:
                    pending_tasks = await self.task_tracker.get_pending_tasks(capability.name)
                    if pending_tasks:
                        await self._process_task(pending_tasks[0])
                        break
            await asyncio.sleep(0.1)  # Prevent CPU spinning

    async def stop(self):
        #"""Stop the agent.#"""
        self.running = False
        self.message_bus.unregister_agent(self.agent_id)
        logger.info(f"Agent {self.agent_id} stopped")

    async def _process_task(self, task):
        #"""Process a task.#"""
        self.current_task = task
        await self.task_tracker.assign_task(task.task_id, self.agent_id)

        # Simulate task processing
        logger.info(f"Agent {self.agent_id} processing task {task.task_id}")
        await self.task_tracker.update_task_status(task.task_id, TaskStatus.RUNNING)

        # Simulate work being done
        await asyncio.sleep(1)

        # Complete the task
        result = {"processed_by": self.agent_id, "timestamp": datetime.now().isoformat()}
        await self.task_tracker.update_task_status(
            task.task_id,
            TaskStatus.COMPLETED,
            result=result,
            actual_load=0.8
        )
        logger.info(f"Agent {self.agent_id} completed task {task.task_id}")
        self.current_task = None

    async def _handle_task_assignment(self, message: Message):
        #"""Handle incoming task assignment messages.#"""
        if message.recipient == self.agent_id:
            task_id = message.payload.get('task_id')
            logger.info(f"Agent {self.agent_id} received task assignment {task_id}")

            # Send acknowledgment
            ack = self.message_bus.create_message(
                sender=self.agent_id,
                recipient=message.sender,
                message_type='task_ack',
                payload={'task_id': task_id, 'status': 'accepted'}
            )
            await self.message_bus.publish(ack)

async def run_simulation():
    #"""Run a simulation with multiple agents processing tasks.#"""
    message_bus = MessageBus()
    task_tracker = TaskTracker()
    capability_registry = CapabilityRegistry()

    # Create agents with different capabilities
    agents = [
        SimulatedAgent(
            "agent1",
            [Capability.DATA_COMPRESSION, Capability.SEMANTIC_ANALYSIS],
            message_bus,
            task_tracker
        ),
        SimulatedAgent(
            "agent2",
            [Capability.MODEL_TRAINING, Capability.DATA_COMPRESSION],
            message_bus,
            task_tracker
        ),
        SimulatedAgent(
            "agent3",
            [Capability.SEMANTIC_ANALYSIS, Capability.MODEL_TRAINING],
            message_bus,
            task_tracker
        )
    ]

    # Register agent capabilities
    for agent in agents:
        for capability in agent.capabilities:
            capability_registry.register_agent_capability(agent.agent_id, capability)

    # Start agents
    agent_tasks = [asyncio.create_task(agent.start()) for agent in agents]

    try:
        # Create some test tasks
        tasks = [
            task_tracker.create_task(
                required_capability=Capability.DATA_COMPRESSION.name,
                priority=TaskPriority.HIGH,
                payload={"data": f"test_data_{i}"}
            ) for i in range(3)
        ]

        tasks.extend([
            task_tracker.create_task(
                required_capability=Capability.MODEL_TRAINING.name,
                priority=TaskPriority.MEDIUM,
                payload={"model": f"model_{i}"}
            ) for i in range(2)
        ])

        # Wait for tasks to be processed
        await asyncio.sleep(5)

        # Verify all tasks are completed
        all_completed = True
        for task in tasks:
            if task.status != TaskStatus.COMPLETED:
                all_completed = False
                logger.error(f"Task {task.task_id} not completed, status: {task.status}")

        if all_completed:
            logger.info("All tasks completed successfully")

    finally:
        # Stop all agents
        for agent in agents:
            await agent.stop()

        # Cancel agent tasks
        for task in agent_tasks:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

if __name__ == "__main__":
    asyncio.run(run_simulation())


||||||| base
=======
import asyncio
import logging
from datetime import datetime
import os
import sys
from typing import Dict, Any, List

# Add src to path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_dir, "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

# Fixed imports to match your file structure
from src.agents.capability import Capability, CapabilityRegistry
from src.agents.task_management import TaskTracker, TaskStatus, TaskPriority
from src.core.messaging import MessageBus, Message

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('agent_simulation.log')
    ]
)
logger = logging.getLogger(__name__)

class SimulatedAgent:
    """Simulated agent that can process tasks."""
    
    def __init__(self, agent_id: str, capabilities: List[Capability], 
                 message_bus: MessageBus, task_tracker: TaskTracker):
        self.agent_id = agent_id
        self.capabilities = capabilities
        self.message_bus = message_bus
        self.task_tracker = task_tracker
        self.current_task = None
        self.running = False
        self.message_bus.register_agent(self.agent_id)
        
    async def start(self):
        """Start the agent's processing loop."""
        self.running = True
        self.message_bus.subscribe('task_assignment', self._handle_task_assignment)
        logger.info(f"Agent {self.agent_id} started")
        
        while self.running:
            if not self.current_task:
                # Look for tasks that match our capabilities
                for capability in self.capabilities:
                    pending_tasks = await self.task_tracker.get_pending_tasks(capability.name)
                    if pending_tasks:
                        await self._process_task(pending_tasks[0])
                        break
            await asyncio.sleep(0.1)  # Prevent CPU spinning
                
    async def stop(self):
        """Stop the agent."""
        self.running = False
        self.message_bus.unregister_agent(self.agent_id)
        logger.info(f"Agent {self.agent_id} stopped")
        
    async def _process_task(self, task):
        """Process a task."""
        self.current_task = task
        await self.task_tracker.assign_task(task.task_id, self.agent_id)
        
        # Simulate task processing
        logger.info(f"Agent {self.agent_id} processing task {task.task_id}")
        await self.task_tracker.update_task_status(task.task_id, TaskStatus.RUNNING)
        
        # Simulate work being done
        await asyncio.sleep(1)
        
        # Complete the task
        result = {"processed_by": self.agent_id, "timestamp": datetime.now().isoformat()}
        await self.task_tracker.update_task_status(
            task.task_id, 
            TaskStatus.COMPLETED,
            result=result,
            actual_load=0.8
        )
        logger.info(f"Agent {self.agent_id} completed task {task.task_id}")
        self.current_task = None
        
    async def _handle_task_assignment(self, message: Message):
        """Handle incoming task assignment messages."""
        if message.recipient == self.agent_id:
            task_id = message.payload.get('task_id')
            logger.info(f"Agent {self.agent_id} received task assignment {task_id}")
            
            # Send acknowledgment
            ack = self.message_bus.create_message(
                sender=self.agent_id,
                recipient=message.sender,
                message_type='task_ack',
                payload={'task_id': task_id, 'status': 'accepted'}
            )
            await self.message_bus.publish(ack)

async def run_simulation():
    """Run a simulation with multiple agents processing tasks."""
    message_bus = MessageBus()
    task_tracker = TaskTracker()
    capability_registry = CapabilityRegistry()
    
    # Create agents with different capabilities
    agents = [
        SimulatedAgent(
            "agent1",
            [Capability.DATA_COMPRESSION, Capability.SEMANTIC_ANALYSIS],
            message_bus,
            task_tracker
        ),
        SimulatedAgent(
            "agent2",
            [Capability.MODEL_TRAINING, Capability.DATA_COMPRESSION],
            message_bus,
            task_tracker
        ),
        SimulatedAgent(
            "agent3",
            [Capability.SEMANTIC_ANALYSIS, Capability.MODEL_TRAINING],
            message_bus,
            task_tracker
        )
    ]
    
    # Register agent capabilities
    for agent in agents:
        for capability in agent.capabilities:
            capability_registry.register_agent_capability(agent.agent_id, capability)
    
    # Start agents
    agent_tasks = [asyncio.create_task(agent.start()) for agent in agents]
    
    try:
        # Create some test tasks
        tasks = [
            task_tracker.create_task(
                required_capability=Capability.DATA_COMPRESSION.name,
                priority=TaskPriority.HIGH,
                payload={"data": f"test_data_{i}"}
            ) for i in range(3)
        ]
        
        tasks.extend([
            task_tracker.create_task(
                required_capability=Capability.MODEL_TRAINING.name,
                priority=TaskPriority.MEDIUM,
                payload={"model": f"model_{i}"}
            ) for i in range(2)
        ])
        
        # Wait for tasks to be processed
        await asyncio.sleep(5)
        
        # Verify all tasks are completed
        all_completed = True
        for task in tasks:
            if task.status != TaskStatus.COMPLETED:
                all_completed = False
                logger.error(f"Task {task.task_id} not completed, status: {task.status}")
        
        if all_completed:
            logger.info("All tasks completed successfully")
        
    finally:
        # Stop all agents
        for agent in agents:
            await agent.stop()
        
        # Cancel agent tasks
        for task in agent_tasks:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

if __name__ == "__main__":
    asyncio.run(run_simulation())
>>>>>>> theirs
