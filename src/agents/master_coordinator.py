from enum import Enum, auto
import asyncio
import uuid
from typing import Dict, List, Optional
from src.agents.base import BaseAgent, AgentCapability

class CoordinatorStatus(Enum):
    INITIALIZING = auto()
    RUNNING = auto()
    PAUSED = auto()
    STOPPED = auto()

class MasterCoordinator(BaseAgent):
    def __init__(self, agent_id: str = "master_coordinator"):
        super().__init__(agent_id=agent_id, capabilities=[AgentCapability.COORDINATION])
        self.status = CoordinatorStatus.INITIALIZING
        self.registered_agents: Dict[str, BaseAgent] = {}
        self.coordinator_agents = {
            "protocol": None,  # Protocol Coordinator
            "blockchain": None,  # Blockchain Coordinator
            "semantic": None    # Semantic Coordinator
        }
        self.task_queue = asyncio.Queue()
        self.task_statuses: Dict[str, dict] = {}
        self._health_check_interval = 60  # seconds
        self._last_health_check = None

    async def get_task_status(self, task_id: str) -> dict:
        ###"""Get status of a specific task###"""
        try:
            return self.task_statuses.get(task_id, {
                "status": "unknown",
                "error": "Task not found"
            })
        except Exception as e:
            print(f"Error getting task status: {str(e)}")
            return {"status": "error", "error": str(e)}

    def __init__(self, agent_id: str = "master_coordinator"):
        super().__init__(agent_id=agent_id, capabilities=[AgentCapability.COORDINATION])
        self.status = CoordinatorStatus.INITIALIZING
        self.registered_agents: Dict[str, BaseAgent] = {}
        self.coordinator_agents = {
            "protocol": None,  # Protocol Coordinator
            "blockchain": None,  # Blockchain Coordinator
            "semantic": None    # Semantic Coordinator
        }
        self.task_queue = asyncio.Queue()
        self.task_statuses: Dict[str, dict] = {}  # Add task status tracking
        self._health_check_interval = 60  # seconds
        self._last_health_check = None

    async def setup(self):
        ###"""Implement abstract setup method###"""
        await super().setup()
        return await self.initialize()

    async def cleanup(self):
        ###"""Implement abstract cleanup method###"""
        # Cancel health check task if it exists
        if hasattr(self, '_health_check_task') and self._health_check_task:
            self._health_check_task.cancel()
            try:
                await self._health_check_task
            except asyncio.CancelledError:
                pass  # Expected when cancelling task

        await self.stop()

    async def _health_check_loop(self):
        ###"""Periodic health check of registered agents###"""
        while self.status == CoordinatorStatus.RUNNING:
            try:
                await self._check_agent_health()
                self._last_health_check = asyncio.get_running_loop().time()
                await asyncio.sleep(self._health_check_interval)
            except asyncio.CancelledError:
                break  # Exit cleanly on cancellation
            except Exception as e:
                print(f"Health check error: {str(e)}")
                await asyncio.sleep(5)  # Brief delay before retry

    async def process_message(self, message: Dict) -> Optional[Dict]:
        ###"""Process incoming messages for coordination###"""
        try:
            message_type = message.get('type', '')
            handlers = {
                'register': self.register_agent,
                'deregister': self.deregister_agent,
                'submit_task': self.submit_task,
                'get_status': self.get_status
            }

            handler = handlers.get(message_type)
            if handler:
                result = await handler(**message.get('data', {}))
                return {'status': 'success', 'result': result}

            return {
                'status': 'error',
                'message': f'Unknown message type: {message_type}'
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }

    def _generate_task_id(self) -> str:
        ###"""Generate a unique task ID###"""
        return str(uuid.uuid4())

    async def initialize(self):
        ###"""Initialize the Master Coordinator###"""
        try:
            print(f"Initializing Master Coordinator: {self.agent_id}")
            # Initialize core systems
            await self._setup_coordinators()
            await self._setup_monitoring()

            self.status = CoordinatorStatus.RUNNING
            print("Master Coordinator initialization complete")
            return True
        except Exception as e:
            print(f"Error during initialization: {str(e)}")
            self.status = CoordinatorStatus.STOPPED
            return False

    async def _setup_coordinators(self):
        ###"""Initialize sub-coordinators###"""
        try:
            # This will be implemented as we create each coordinator type
            for coordinator_type in self.coordinator_agents.keys():
                print(f"Setting up {coordinator_type} coordinator...")
                # Placeholder for coordinator initialization
                # self.coordinator_agents[coordinator_type] = await self._create_coordinator(coordinator_type)
            return True
        except Exception as e:
            print(f"Error setting up coordinators: {str(e)}")
            return False

    async def _setup_monitoring(self):
        ###"""Setup monitoring and health checking###"""
        try:
            # Start health check loop
            self._health_check_task = asyncio.create_task(self._health_check_loop())
            print("Monitoring system initialized")
            return True
        except Exception as e:
            print(f"Error setting up monitoring: {str(e)}")
            return False

    async def _check_agent_health(self):
        ###"""Check health of all registered agents###"""
        unhealthy_agents = []

        for agent_id, agent in self.registered_agents.items():
            try:
                # Assuming agents have a get_status method
                status = await agent.get_status()
                if status.get('status') not in ['RUNNING', 'ACTIVE']:
                    unhealthy_agents.append(agent_id)
            except Exception:
                unhealthy_agents.append(agent_id)

        # Deregister unhealthy agents
        for agent_id in unhealthy_agents:
            print(f"Deregistering unhealthy agent: {agent_id}")
            await self.deregister_agent(agent_id)

    async def register_agent(self, agent: BaseAgent) -> bool:
        ###"""Register a new agent with the coordinator###"""
        try:
            agent_id = agent.agent_id
            if agent_id in self.registered_agents:
                print(f"Agent {agent_id} already registered")
                return False

            self.registered_agents[agent_id] = agent
            print(f"Successfully registered agent: {agent_id}")
            print(f"Agent capabilities: {agent.capabilities}")
            return True
        except Exception as e:
            print(f"Error registering agent {agent.agent_id}: {str(e)}")
            return False

    async def deregister_agent(self, agent_id: str) -> bool:
        ###"""Remove an agent from the coordinator###"""
        if agent_id in self.registered_agents:
            del self.registered_agents[agent_id]
            print(f"Successfully deregistered agent: {agent_id}")
            return True
        return False

    async def submit_task(self, task_data: dict) -> str:
        ###"""Submit a new task###"""
        try:
            task_id = self._generate_task_id()
            task = {
                "task_id": task_id,
                "status": "pending",
                **task_data
            }
            await self.task_queue.put(task)
            print(f"Task {task_id} submitted successfully")  # Single log message
            return task_id
        except Exception as e:
            print(f"Error submitting task: {str(e)}")
            return None

    async def process_tasks(self):
        ###"""Process queued tasks###"""
        while self.status == CoordinatorStatus.RUNNING:
            try:
                if self.task_queue.empty():
                    await asyncio.sleep(0.1)
                    continue

                task = await self.task_queue.get()
                print(f"Processing task: {task['task_id']}")  # Add processing log
                result = await self._process_single_task(task)

                if result:
                    print(f"Task {task['task_id']} completed successfully")
                else:
                    print(f"Task {task['task_id']} failed")

            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Error in process_tasks: {str(e)}")

    async def _process_single_task(self, task: dict) -> bool:
        ###"""Process an individual task###"""
        task_id = task.get('task_id', 'unknown')
        try:
            # Try direct agent first
            agent = self._find_agent_for_task(task)
            if agent:
                task['timestamp'] = asyncio.get_running_loop().time()
                task['status'] = 'processing'

                result = await agent.process_task(task)

                task['status'] = 'completed' if result else 'failed'
                task['completion_time'] = asyncio.get_running_loop().time()
                return result

            # Try coordinator if no direct agent
            coordinator = self._select_coordinator(task)
            if coordinator:
                return await coordinator.process_task(task)

            print(f"No handler found for task {task_id}")
            return False

        except asyncio.CancelledError:
            task['status'] = 'cancelled'
            raise
        except Exception as e:
            print(f"Error processing task {task_id}: {str(e)}")
            task['status'] = 'failed'
            task['error'] = str(e)
            return False

    def _find_agent_for_task(self, task: dict) -> Optional[BaseAgent]:
        ###"""Find suitable agent for task based on capabilities###"""
        task_type = task.get("type")
        print(f"Finding agent for task type: {task_type}")

        if not task_type:
            print("No task type specified")
            return None

        # Convert task type to capability
        capability_mapping = {
            "semantic": AgentCapability.SEMANTIC,
            "protocol": AgentCapability.PROTOCOL,
            "blockchain": AgentCapability.BLOCKCHAIN
        }

        required_capability = capability_mapping.get(task_type)
        if not required_capability:
            print(f"No capability mapping for task type: {task_type}")
            return None

        print(f"Looking for agent with capability: {required_capability}")
        # Find agent with matching capability
        for agent in self.registered_agents.values():
            print(f"Checking agent {agent.agent_id} with capabilities: {agent.capabilities}")
            if required_capability in agent.capabilities:
                print(f"Found suitable agent: {agent.agent_id}")
                return agent

        print("No suitable agent found")
        return None

    def _select_coordinator(self, task: dict) -> Optional[BaseAgent]:
        ###"""Select appropriate coordinator based on task type###"""
        task_type = task.get("type", "")

        coordinator_mapping = {
            "protocol": self.coordinator_agents["protocol"],
            "blockchain": self.coordinator_agents["blockchain"],
            "semantic": self.coordinator_agents["semantic"]
        }

        coordinator = coordinator_mapping.get(task_type)
        if coordinator:
            print(f"Found coordinator for task type: {task_type}")
        return coordinator

    async def start(self):
        ###"""Start the coordinator###"""
        if self.status != CoordinatorStatus.RUNNING:
            await self.initialize()
            if self.status == CoordinatorStatus.RUNNING:
                asyncio.create_task(self.process_tasks())
                print("Master Coordinator started successfully")
                return True
        return False

    async def stop(self):
        ###"""Stop the coordinator###"""
        self.status = CoordinatorStatus.STOPPED
        # Create a copy of registered agents for safe iteration
        agents_to_deregister = list(self.registered_agents.keys())
        for agent_id in agents_to_deregister:
            await self.deregister_agent(agent_id)
        print("Master Coordinator stopped")

    async def get_status(self) -> dict:
        ###"""Get current coordinator status###"""
        return {
            "status": self.status.name,
            "registered_agents": len(self.registered_agents),
            "pending_tasks": self.task_queue.qsize(),
            "last_health_check": self._last_health_check
        }


