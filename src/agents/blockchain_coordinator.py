# src/agents/blockchain_coordinator.py
from typing import Dict
import asyncio
import logging
from uuid import uuid4
from .base import BaseAgent, AgentCapability

class BlockchainCoordinator(BaseAgent):
    def __init__(self, agent_id: str = None):
        if not agent_id:
            agent_id = f"blockchain_coordinator_{str(uuid4())[:8]}"
        super().__init__(agent_id=agent_id, capabilities=[AgentCapability.BLOCKCHAIN])

        self.blockchain_agents = {}
        self.task_queue = asyncio.Queue()
        self.is_running = False
        self.processing_task = None
        logging.info(f"Initializing Blockchain Coordinator: {agent_id}")

    def register_agent(self, agent):
        ###"""Register a blockchain agent with the coordinator###"""
        if agent.agent_id in self.blockchain_agents:
            logging.warning(f"Agent {agent.agent_id} already registered")
            return False
        self.blockchain_agents[agent.agent_id] = agent
        logging.info(f"Successfully registered agent: {agent.agent_id}")
        return True

    async def submit_task(self, task: dict) -> str:
        ###"""Submit a blockchain task for processing###"""
        task_id = str(uuid4())
        task['task_id'] = task_id
        await self.task_queue.put(task)
        logging.info(f"Task {task_id} submitted successfully")
        return task_id

    async def start(self):
        self.is_running = True
        logging.info(f"Starting Blockchain Coordinator: {self.agent_id}")
        self.processing_task = asyncio.create_task(self._process_tasks())
        await asyncio.sleep(0)  # Allow task to start

    async def stop(self):
        self.is_running = False
        if self.processing_task:
            try:
                await asyncio.wait_for(self.processing_task, timeout=1.0)
            except asyncio.TimeoutError:
                if not self.processing_task.done():
                    self.processing_task.cancel()
        for agent in self.blockchain_agents.values():
            await agent.stop()
        logging.info(f"Blockchain Coordinator {self.agent_id} stopped")

    async def _process_tasks(self):
        ###"""Process tasks from the queue###"""
        while self.is_running:
            try:
                try:
                    task = await asyncio.wait_for(self.task_queue.get(), timeout=0.1)
                except asyncio.TimeoutError:
                    continue

                logging.info(f"Processing blockchain task: {task['task_id']}")

                if self.blockchain_agents:
                    # Here we'd implement more sophisticated agent selection based on task type
                    selected_agent = await self._select_agent_for_task(task)
                    if selected_agent:
                        try:
                            result = await selected_agent.process_task(task)
                            logging.info(f"Task {task['task_id']} processed: {result}")
                        except Exception as e:
                            logging.error(f"Error processing task {task['task_id']}: {str(e)}")
                    else:
                        logging.warning(f"No suitable agent found for task {task['task_id']}")
                else:
                    logging.warning(f"No agents available to process task {task['task_id']}")

                self.task_queue.task_done()

            except Exception as e:
                logging.error(f"Error in task processing loop: {str(e)}")
                await asyncio.sleep(0.1)

    async def _select_agent_for_task(self, task: dict):
        ###"""Select the most appropriate agent for a given task###"""
        if not self.blockchain_agents:
            return None

        # Get task type and requirements
        task_type = task.get('type', 'general')

        # For now, simple selection - just get first available agent
        # In a real implementation, this would match task requirements with agent capabilities
        return list(self.blockchain_agents.values())[0]


