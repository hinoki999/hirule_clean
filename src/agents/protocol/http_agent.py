<<<<<<< ours
# src/agents/protocol/http_agent.py
from ..base_agent import BaseAgent, AgentCapability
import logging
from uuid import uuid4

class HTTPAgent(BaseAgent):
    def __init__(self, agent_id: str = None):
        if not agent_id:
            agent_id = f"http_agent_{str(uuid4())[:8]}"
        super().__init__(agent_id=agent_id, capabilities=[AgentCapability.PROTOCOL])
        self.protocol = "HTTP3"
        logging.info(f"Initialized HTTP agent: {agent_id}")

    async def process_request(self, request: dict) -> dict:
        ###"""Process an HTTP request###"""
        try:
            logging.info(f"Processing HTTP request: {request}")
            # Basic request processing logic
            response = {
                'status': 'success',
                'protocol': self.protocol,
                'agent_id': self.agent_id,
                'message': f"Processed request using {self.protocol}"
            }
            return response
        except Exception as e:
            logging.error(f"Error processing HTTP request: {str(e)}")
            return {
                'status': 'error',
                'message': str(e)
            }

    async def start(self):
        ###"""Start the HTTP agent###"""
        await super().start()
        logging.info(f"HTTP Agent {self.agent_id} started")

    async def stop(self):
        ###"""Stop the HTTP agent###"""
        await super().stop()
        logging.info(f"HTTP Agent {self.agent_id} stopped")


||||||| base
=======
# src/agents/protocol/http_agent.py
from ..base_agent import BaseAgent, AgentCapability
import logging
from uuid import uuid4

class HTTPAgent(BaseAgent):
    def __init__(self, agent_id: str = None):
        if not agent_id:
            agent_id = f"http_agent_{str(uuid4())[:8]}"
        super().__init__(agent_id=agent_id, capabilities=[AgentCapability.PROTOCOL])
        self.protocol = "HTTP3"
        logging.info(f"Initialized HTTP agent: {agent_id}")

    async def process_request(self, request: dict) -> dict:
        """Process an HTTP request"""
        try:
            logging.info(f"Processing HTTP request: {request}")
            # Basic request processing logic
            response = {
                'status': 'success',
                'protocol': self.protocol,
                'agent_id': self.agent_id,
                'message': f"Processed request using {self.protocol}"
            }
            return response
        except Exception as e:
            logging.error(f"Error processing HTTP request: {str(e)}")
            return {
                'status': 'error',
                'message': str(e)
            }

    async def start(self):
        """Start the HTTP agent"""
        await super().start()
        logging.info(f"HTTP Agent {self.agent_id} started")

    async def stop(self):
        """Stop the HTTP agent"""
        await super().stop()
        logging.info(f"HTTP Agent {self.agent_id} stopped")
>>>>>>> theirs
