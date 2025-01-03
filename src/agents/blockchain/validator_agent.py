<<<<<<< ours
# src/agents/blockchain/validator_agent.py
from ..base_agent import BaseAgent, AgentCapability
import logging
from uuid import uuid4

class ValidatorAgent(BaseAgent):
    def __init__(self, agent_id: str = None):
        if not agent_id:
            agent_id = f"validator_agent_{str(uuid4())[:8]}"
        super().__init__(agent_id=agent_id, capabilities=[AgentCapability.BLOCKCHAIN])

        self.validated_blocks = set()
        logging.info(f"Initialized Validator Agent: {agent_id}")

    async def process_task(self, task: dict) -> dict:
        ###"""Process a validation task###"""
        try:
            logging.info(f"Validating block: {task.get('block_data', 'Unknown')}")

            # Simple validation logic - could be expanded based on needs
            validation_result = self._validate_block(task.get('block_data'))

            response = {
                'task_id': task.get('task_id'),
                'status': 'success' if validation_result else 'failed',
                'validated': validation_result,
                'timestamp': task.get('timestamp'),
                'validator_id': self.agent_id
            }

            if validation_result:
                self.validated_blocks.add(task.get('block_data'))

            return response

        except Exception as e:
            logging.error(f"Error validating block: {str(e)}")
            return {
                'task_id': task.get('task_id'),
                'status': 'error',
                'error': str(e)
            }

    def _validate_block(self, block_data: str) -> bool:
        ###"""
        Basic block validation logic
        In a real implementation, this would check:
        - Block structure
        - Signatures
        - Transaction validity
        - Consensus rules
        ###"""
        if not block_data:
            return False

        # Simple validation for now
        return True

    async def start(self):
        ###"""Start the validator agent###"""
        await super().start()
        logging.info(f"Validator Agent {self.agent_id} started")

    async def stop(self):
        ###"""Stop the validator agent###"""
        await super().stop()
        logging.info(f"Validator Agent {self.agent_id} stopped")


||||||| base
=======
# src/agents/blockchain/validator_agent.py
from ..base_agent import BaseAgent, AgentCapability
import logging
from uuid import uuid4

class ValidatorAgent(BaseAgent):
    def __init__(self, agent_id: str = None):
        if not agent_id:
            agent_id = f"validator_agent_{str(uuid4())[:8]}"
        super().__init__(agent_id=agent_id, capabilities=[AgentCapability.BLOCKCHAIN])
        
        self.validated_blocks = set()
        logging.info(f"Initialized Validator Agent: {agent_id}")

    async def process_task(self, task: dict) -> dict:
        """Process a validation task"""
        try:
            logging.info(f"Validating block: {task.get('block_data', 'Unknown')}")
            
            # Simple validation logic - could be expanded based on needs
            validation_result = self._validate_block(task.get('block_data'))
            
            response = {
                'task_id': task.get('task_id'),
                'status': 'success' if validation_result else 'failed',
                'validated': validation_result,
                'timestamp': task.get('timestamp'),
                'validator_id': self.agent_id
            }
            
            if validation_result:
                self.validated_blocks.add(task.get('block_data'))
                
            return response
            
        except Exception as e:
            logging.error(f"Error validating block: {str(e)}")
            return {
                'task_id': task.get('task_id'),
                'status': 'error',
                'error': str(e)
            }

    def _validate_block(self, block_data: str) -> bool:
        """
        Basic block validation logic
        In a real implementation, this would check:
        - Block structure
        - Signatures
        - Transaction validity
        - Consensus rules
        """
        if not block_data:
            return False
            
        # Simple validation for now
        return True

    async def start(self):
        """Start the validator agent"""
        await super().start()
        logging.info(f"Validator Agent {self.agent_id} started")

    async def stop(self):
        """Stop the validator agent"""
        await super().stop()
        logging.info(f"Validator Agent {self.agent_id} stopped")
>>>>>>> theirs
