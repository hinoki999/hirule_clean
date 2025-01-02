<<<<<<< ours
# src/agents/protocol_coordinator.py
from typing import Dict
import asyncio
import logging
from uuid import uuid4
from .base import BaseAgent, AgentCapability
from src.agents.protocol.coap_agent import CoAPAgent


class ProtocolCoordinator(BaseAgent):
    def __init__(self, agent_id: str = None):
        if not agent_id:
            agent_id = f"protocol_coordinator_{str(uuid4())[:8]}"
        super().__init__(agent_id=agent_id, capabilities=[AgentCapability.PROTOCOL])

        self.protocol_agents = {}
        self.task_queue = asyncio.Queue()
        self.is_running = False
        self.processing_task = None
        logging.info(f"Initializing Protocol Coordinator: {agent_id}")

    def register_agent(self, agent):  # Changed to non-async for simplicity
        ###"""Register a protocol agent with the coordinator###"""
        if agent.agent_id in self.protocol_agents:
            logging.warning(f"Agent {agent.agent_id} already registered")
            return False
        self.protocol_agents[agent.agent_id] = agent
        logging.info(f"Successfully registered agent: {agent.agent_id}")
        return True

    async def start(self):
        self.is_running = True
        logging.info(f"Starting Protocol Coordinator: {self.agent_id}")

        # Optionally create a CoAPAgent instance
        coap_agent = CoAPAgent()
        self.register_agent(coap_agent)

        # Start the CoAPAgent (so it can spin up the CoAP server)
        await coap_agent.start()

        self.processing_task = asyncio.create_task(self._process_tasks())
        await asyncio.sleep(0)
    async def submit_task(self, task: dict) -> str:
        ###"""Submit a protocol task for processing###"""
        task_id = str(uuid4())
        task['task_id'] = task_id
        await self.task_queue.put(task)
        logging.info(f"Task {task_id} submitted successfully")
        return task_id

    async def start(self):
        self.is_running = True
        logging.info(f"Starting Protocol Coordinator: {self.agent_id}")
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
        for agent in self.protocol_agents.values():
            await agent.stop()
        logging.info(f"Protocol Coordinator {self.agent_id} stopped")

    async def _process_tasks(self):
        while self.is_running:
            try:
                try:
                    task = await asyncio.wait_for(self.task_queue.get(), timeout=0.1)
                except asyncio.TimeoutError:
                    continue

                logging.info(f"Processing task: {task['task_id']}")

                if self.protocol_agents:
                    agent = list(self.protocol_agents.values())[0]
                    try:
                        if hasattr(agent, 'process_request'):
                            result = await agent.process_request(task)
                            logging.info(f"Task {task['task_id']} processed: {result}")
                    except Exception as e:
                        logging.error(f"Error processing task {task['task_id']}: {str(e)}")
                else:
                    logging.warning(f"No agents available to process task {task['task_id']}")

                self.task_queue.task_done()

            except Exception as e:
                logging.error(f"Error in task processing loop: {str(e)}")
                await asyncio.sleep(0.1)


||||||| base
=======
# src/agents/protocol_coordinator.py
from typing import Dict
import asyncio
import logging
from uuid import uuid4
from .base import BaseAgent, AgentCapability
from src.agents.protocol.coap_agent import CoAPAgent


class ProtocolCoordinator(BaseAgent):
    def __init__(self, agent_id: str = None):
        if not agent_id:
            agent_id = f"protocol_coordinator_{str(uuid4())[:8]}"
        super().__init__(agent_id=agent_id, capabilities=[AgentCapability.PROTOCOL])
        
        self.protocol_agents = {}
        self.task_queue = asyncio.Queue()
        self.is_running = False
        self.processing_task = None
        logging.info(f"Initializing Protocol Coordinator: {agent_id}")

    def register_agent(self, agent):  # Changed to non-async for simplicity
        """Register a protocol agent with the coordinator"""
        if agent.agent_id in self.protocol_agents:
            logging.warning(f"Agent {agent.agent_id} already registered")
            return False
        self.protocol_agents[agent.agent_id] = agent
        logging.info(f"Successfully registered agent: {agent.agent_id}")
        return True

    async def start(self):
        self.is_running = True
        logging.info(f"Starting Protocol Coordinator: {self.agent_id}")

        # Optionally create a CoAPAgent instance
        coap_agent = CoAPAgent()
        self.register_agent(coap_agent)
        
        # Start the CoAPAgent (so it can spin up the CoAP server)
        await coap_agent.start()

        self.processing_task = asyncio.create_task(self._process_tasks())
        await asyncio.sleep(0)
    async def submit_task(self, task: dict) -> str:
        """Submit a protocol task for processing"""
        task_id = str(uuid4())
        task['task_id'] = task_id
        await self.task_queue.put(task)
        logging.info(f"Task {task_id} submitted successfully")
        return task_id

    async def start(self):
        self.is_running = True
        logging.info(f"Starting Protocol Coordinator: {self.agent_id}")
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
        for agent in self.protocol_agents.values():
            await agent.stop()
        logging.info(f"Protocol Coordinator {self.agent_id} stopped")

    async def _process_tasks(self):
        while self.is_running:
            try:
                try:
                    task = await asyncio.wait_for(self.task_queue.get(), timeout=0.1)
                except asyncio.TimeoutError:
                    continue

                logging.info(f"Processing task: {task['task_id']}")
                
                if self.protocol_agents:
                    agent = list(self.protocol_agents.values())[0]
                    try:
                        if hasattr(agent, 'process_request'):
                            result = await agent.process_request(task)
                            logging.info(f"Task {task['task_id']} processed: {result}")
                    except Exception as e:
                        logging.error(f"Error processing task {task['task_id']}: {str(e)}")
                else:
                    logging.warning(f"No agents available to process task {task['task_id']}")
                
                self.task_queue.task_done()
                    
            except Exception as e:
                logging.error(f"Error in task processing loop: {str(e)}")
                await asyncio.sleep(0.1)
>>>>>>> theirs
