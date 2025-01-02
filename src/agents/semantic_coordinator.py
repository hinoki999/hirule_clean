<<<<<<< ours
# src/agents/semantic_coordinator.py
from typing import Dict, List, Optional
from uuid import uuid4
import asyncio
import logging
from .base import BaseAgent, AgentCapability
from .semantic_agent import SemanticAgent

class SemanticCoordinator(BaseAgent):
    def __init__(self, agent_id: str = None):
        if not agent_id:
            agent_id = f"semantic_coordinator_{str(uuid4())[:8]}"
        super().__init__(agent_id=agent_id, capabilities=[AgentCapability.SEMANTIC])

        self.semantic_agents: Dict[str, SemanticAgent] = {}
        self.task_queue = asyncio.Queue()
        self.is_running = False

        logging.info(f"Initializing Semantic Coordinator: {agent_id}")

    async def start(self):
        ###"""Start the semantic coordinator###"""
        self.is_running = True
        logging.info(f"Starting Semantic Coordinator: {self.agent_id}")
        await self._process_tasks()

    async def stop(self):
        ###"""Stop the semantic coordinator###"""
        self.is_running = False
        for agent_id, agent in self.semantic_agents.items():
            await agent.stop()
        logging.info(f"Semantic Coordinator {self.agent_id} stopped")

    async def register_agent(self, agent: SemanticAgent) -> bool:
        ###"""Register a semantic agent with the coordinator###"""
        if agent.agent_id in self.semantic_agents:
            logging.warning(f"Agent {agent.agent_id} already registered")
            return False

        self.semantic_agents[agent.agent_id] = agent
        logging.info(f"Successfully registered agent: {agent.agent_id}")
        return True

    async def submit_task(self, task: dict) -> str:
        ###"""Submit a semantic task for processing###"""
        task_id = str(uuid4())
        task['task_id'] = task_id
        await self.task_queue.put(task)
        logging.info(f"Task {task_id} submitted successfully")
        return task_id

    async def _process_tasks(self):
        ###"""Process tasks from the queue###"""
        while self.is_running:
            try:
                if self.task_queue.empty():
                    await asyncio.sleep(0.1)
                    continue

                task = await self.task_queue.get()
                # Implement task distribution logic here
                logging.info(f"Processing task: {task['task_id']}")
                # Add task processing logic

            except Exception as e:
                logging.error(f"Error processing task: {str(e)}")


||||||| base
=======
# src/agents/semantic_coordinator.py
from typing import Dict, List, Optional
from uuid import uuid4
import asyncio
import logging
from .base import BaseAgent, AgentCapability
from .semantic_agent import SemanticAgent

class SemanticCoordinator(BaseAgent):
    def __init__(self, agent_id: str = None):
        if not agent_id:
            agent_id = f"semantic_coordinator_{str(uuid4())[:8]}"
        super().__init__(agent_id=agent_id, capabilities=[AgentCapability.SEMANTIC])
        
        self.semantic_agents: Dict[str, SemanticAgent] = {}
        self.task_queue = asyncio.Queue()
        self.is_running = False
        
        logging.info(f"Initializing Semantic Coordinator: {agent_id}")

    async def start(self):
        """Start the semantic coordinator"""
        self.is_running = True
        logging.info(f"Starting Semantic Coordinator: {self.agent_id}")
        await self._process_tasks()

    async def stop(self):
        """Stop the semantic coordinator"""
        self.is_running = False
        for agent_id, agent in self.semantic_agents.items():
            await agent.stop()
        logging.info(f"Semantic Coordinator {self.agent_id} stopped")

    async def register_agent(self, agent: SemanticAgent) -> bool:
        """Register a semantic agent with the coordinator"""
        if agent.agent_id in self.semantic_agents:
            logging.warning(f"Agent {agent.agent_id} already registered")
            return False
            
        self.semantic_agents[agent.agent_id] = agent
        logging.info(f"Successfully registered agent: {agent.agent_id}")
        return True

    async def submit_task(self, task: dict) -> str:
        """Submit a semantic task for processing"""
        task_id = str(uuid4())
        task['task_id'] = task_id
        await self.task_queue.put(task)
        logging.info(f"Task {task_id} submitted successfully")
        return task_id

    async def _process_tasks(self):
        """Process tasks from the queue"""
        while self.is_running:
            try:
                if self.task_queue.empty():
                    await asyncio.sleep(0.1)
                    continue
                    
                task = await self.task_queue.get()
                # Implement task distribution logic here
                logging.info(f"Processing task: {task['task_id']}")
                # Add task processing logic
                
            except Exception as e:
                logging.error(f"Error processing task: {str(e)}")
>>>>>>> theirs
