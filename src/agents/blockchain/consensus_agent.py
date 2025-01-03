<<<<<<< ours
# src/agents/blockchain/consensus_agent.py
from ..base_agent import BaseAgent, AgentCapability
import logging
from uuid import uuid4
import asyncio
from typing import List, Dict

class ConsensusAgent(BaseAgent):
    def __init__(self, agent_id: str = None):
        if not agent_id:
            agent_id = f"consensus_agent_{str(uuid4())[:8]}"
        super().__init__(agent_id=agent_id, capabilities=[AgentCapability.BLOCKCHAIN])

        self.consensus_state = {}
        self.participant_votes = {}
        self.is_running = False
        logging.info(f"Initialized Consensus Agent: {agent_id}")

    async def process_task(self, task: dict) -> dict:
        ###"""Process a consensus task###"""
        try:
            logging.info(f"Processing consensus task: {task.get('type', 'Unknown')}")

            if task.get('type') == 'propose_block':
                return await self._handle_block_proposal(task)
            elif task.get('type') == 'vote':
                return await self._handle_vote(task)
            else:
                return {
                    'task_id': task.get('task_id'),
                    'status': 'error',
                    'error': 'Unknown task type'
                }

        except Exception as e:
            logging.error(f"Error processing consensus task: {str(e)}")
            return {
                'task_id': task.get('task_id'),
                'status': 'error',
                'error': str(e)
            }

    async def _handle_block_proposal(self, task: dict) -> dict:
        ###"""Handle a new block proposal###"""
        block_id = task.get('block_id')

        if not block_id:
            return {'status': 'error', 'error': 'No block ID provided'}

        self.consensus_state[block_id] = {
            'proposed_by': task.get('proposer'),
            'timestamp': task.get('timestamp'),
            'votes': set(),
            'status': 'proposed'
        }

        return {
            'task_id': task.get('task_id'),
            'status': 'success',
            'block_id': block_id,
            'message': 'Block proposal registered'
        }

    async def _handle_vote(self, task: dict) -> dict:
        ###"""Handle a vote for a proposed block###"""
        block_id = task.get('block_id')
        voter = task.get('voter')

        if not block_id or not voter:
            return {'status': 'error', 'error': 'Missing block ID or voter'}

        if block_id not in self.consensus_state:
            return {'status': 'error', 'error': 'Unknown block ID'}

        self.consensus_state[block_id]['votes'].add(voter)

        # Check if consensus is reached (simple majority for now)
        vote_count = len(self.consensus_state[block_id]['votes'])
        if vote_count >= 2:  # Simplified consensus threshold
            self.consensus_state[block_id]['status'] = 'confirmed'

        return {
            'task_id': task.get('task_id'),
            'status': 'success',
            'block_id': block_id,
            'vote_count': vote_count,
            'consensus_reached': self.consensus_state[block_id]['status'] == 'confirmed'
        }

    async def start(self):
        ###"""Start the consensus agent###"""
        self.is_running = True
        await super().start()
        logging.info(f"Consensus Agent {self.agent_id} started")

    async def stop(self):
        ###"""Stop the consensus agent###"""
        self.is_running = False
        await super().stop()
        logging.info(f"Consensus Agent {self.agent_id} stopped")


||||||| base
=======
# src/agents/blockchain/consensus_agent.py
from ..base_agent import BaseAgent, AgentCapability
import logging
from uuid import uuid4
import asyncio
from typing import List, Dict

class ConsensusAgent(BaseAgent):
    def __init__(self, agent_id: str = None):
        if not agent_id:
            agent_id = f"consensus_agent_{str(uuid4())[:8]}"
        super().__init__(agent_id=agent_id, capabilities=[AgentCapability.BLOCKCHAIN])
        
        self.consensus_state = {}
        self.participant_votes = {}
        self.is_running = False
        logging.info(f"Initialized Consensus Agent: {agent_id}")

    async def process_task(self, task: dict) -> dict:
        """Process a consensus task"""
        try:
            logging.info(f"Processing consensus task: {task.get('type', 'Unknown')}")
            
            if task.get('type') == 'propose_block':
                return await self._handle_block_proposal(task)
            elif task.get('type') == 'vote':
                return await self._handle_vote(task)
            else:
                return {
                    'task_id': task.get('task_id'),
                    'status': 'error',
                    'error': 'Unknown task type'
                }
                
        except Exception as e:
            logging.error(f"Error processing consensus task: {str(e)}")
            return {
                'task_id': task.get('task_id'),
                'status': 'error',
                'error': str(e)
            }

    async def _handle_block_proposal(self, task: dict) -> dict:
        """Handle a new block proposal"""
        block_id = task.get('block_id')
        
        if not block_id:
            return {'status': 'error', 'error': 'No block ID provided'}
            
        self.consensus_state[block_id] = {
            'proposed_by': task.get('proposer'),
            'timestamp': task.get('timestamp'),
            'votes': set(),
            'status': 'proposed'
        }
        
        return {
            'task_id': task.get('task_id'),
            'status': 'success',
            'block_id': block_id,
            'message': 'Block proposal registered'
        }

    async def _handle_vote(self, task: dict) -> dict:
        """Handle a vote for a proposed block"""
        block_id = task.get('block_id')
        voter = task.get('voter')
        
        if not block_id or not voter:
            return {'status': 'error', 'error': 'Missing block ID or voter'}
            
        if block_id not in self.consensus_state:
            return {'status': 'error', 'error': 'Unknown block ID'}
            
        self.consensus_state[block_id]['votes'].add(voter)
        
        # Check if consensus is reached (simple majority for now)
        vote_count = len(self.consensus_state[block_id]['votes'])
        if vote_count >= 2:  # Simplified consensus threshold
            self.consensus_state[block_id]['status'] = 'confirmed'
            
        return {
            'task_id': task.get('task_id'),
            'status': 'success',
            'block_id': block_id,
            'vote_count': vote_count,
            'consensus_reached': self.consensus_state[block_id]['status'] == 'confirmed'
        }

    async def start(self):
        """Start the consensus agent"""
        self.is_running = True
        await super().start()
        logging.info(f"Consensus Agent {self.agent_id} started")

    async def stop(self):
        """Stop the consensus agent"""
        self.is_running = False
        await super().stop()
        logging.info(f"Consensus Agent {self.agent_id} stopped")
>>>>>>> theirs
