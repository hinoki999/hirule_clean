<<<<<<< ours
# src/agents/blockchain/network_agent.py
from ..base_agent import BaseAgent, AgentCapability
import logging
from uuid import uuid4
import asyncio
from typing import Dict
import time

class NetworkAgent(BaseAgent):
    def __init__(self, agent_id: str = None, max_peers: int = 10):
        if not agent_id:
            agent_id = f"network_agent_{str(uuid4())[:8]}"
        super().__init__(agent_id=agent_id, capabilities=[AgentCapability.BLOCKCHAIN])

        self.max_peers = max_peers
        self.peers: Dict[str, 'PeerInfo'] = {}
        self.pending_messages = asyncio.Queue()
        self.is_running = False
        self.sync_status = False
        self.background_tasks = []

        logging.info(f"Initialized Network Agent: {agent_id}")

    async def start(self):
        ###"""Start the network agent and its background tasks###"""
        self.is_running = True
        await super().start()

        # Start background tasks with proper tracking
        self.background_tasks = [
            asyncio.create_task(self._peer_discovery_loop()),
            asyncio.create_task(self._message_processing_loop()),
            asyncio.create_task(self._network_sync_loop())
        ]

        logging.info(f"Network Agent {self.agent_id} started")

    async def stop(self):
        ###"""Stop the network agent and cleanup###"""
        self.is_running = False

        # Cancel all background tasks
        if self.background_tasks:
            for task in self.background_tasks:
                if not task.done():
                    task.cancel()
                    try:
                        await asyncio.wait_for(task, timeout=1.0)
                    except (asyncio.CancelledError, asyncio.TimeoutError):
                        pass
                    except Exception as e:
                        logging.error(f"Error cancelling task: {str(e)}")

        self.background_tasks.clear()

        # Disconnect all peers
        peer_ids = list(self.peers.keys())
        for peer_id in peer_ids:
            await self.disconnect_peer(peer_id)

        # Cleanup queue
        while not self.pending_messages.empty():
            try:
                self.pending_messages.get_nowait()
            except asyncio.QueueEmpty:
                break

        await super().stop()
        logging.info(f"Network Agent {self.agent_id} stopped")

    async def connect_peer(self, task: dict) -> bool:
        ###"""Connect to a new peer###"""
        peer_id = task.get('peer_id')
        if not peer_id or peer_id in self.peers:
            return False

        if len(self.peers) >= self.max_peers:
            logging.warning(f"Max peers ({self.max_peers}) reached, rejecting connection")
            return False

        self.peers[peer_id] = PeerInfo(
            peer_id=peer_id,
            address=task.get('address'),
            port=task.get('port'),
            connected_at=time.time()
        )
        logging.info(f"Connected to peer: {peer_id}")
        return True

    async def process_task(self, task: dict) -> dict:
        ###"""Process network-related tasks###"""
        try:
            task_type = task.get('type', '')
            handlers = {
                'connect_peer': self.connect_peer,
                'broadcast_transaction': self.broadcast_transaction,
                'broadcast_block': self.broadcast_block,
                'get_peer_info': self.get_peer_info,
                'sync_request': self.handle_sync_request
            }

            if task_type in handlers:
                result = await handlers[task_type](task)
                return {
                    'task_id': task.get('task_id'),
                    'status': 'success',
                    'result': result
                }
            else:
                return {
                    'task_id': task.get('task_id'),
                    'status': 'error',
                    'error': f'Unknown task type: {task_type}'
                }

        except Exception as e:
            logging.error(f"Error processing network task: {str(e)}")
            return {
                'task_id': task.get('task_id'),
                'status': 'error',
                'error': str(e)
            }

    async def disconnect_peer(self, peer_id: str) -> bool:
        ###"""Disconnect from a peer###"""
        if peer_id in self.peers:
            del self.peers[peer_id]
            logging.info(f"Disconnected from peer: {peer_id}")
            return True
        return False

    async def broadcast_transaction(self, task: dict) -> bool:
        ###"""Broadcast a transaction to all peers###"""
        transaction = task.get('transaction')
        if not transaction:
            return False

        message = {
            'type': 'transaction',
            'data': transaction,
            'timestamp': time.time()
        }

        await self._broadcast_to_peers(message)
        return True

    async def broadcast_block(self, task: dict) -> bool:
        ###"""Broadcast a new block to all peers###"""
        block = task.get('block')
        if not block:
            return False

        message = {
            'type': 'block',
            'data': block,
            'timestamp': time.time()
        }

        await self._broadcast_to_peers(message)
        return True

    async def get_peer_info(self, task: dict) -> dict:
        ###"""Get information about connected peers###"""
        return {
            'peer_count': len(self.peers),
            'peers': [peer.to_dict() for peer in self.peers.values()],
            'sync_status': self.sync_status
        }

    async def handle_sync_request(self, task: dict) -> dict:
        ###"""Handle a synchronization request from a peer###"""
        start_block = task.get('start_block')
        end_block = task.get('end_block')
        peer_id = task.get('peer_id')

        if not all([start_block, end_block, peer_id]):
            return {'error': 'Missing required sync parameters'}

        return {
            'status': 'sync_started',
            'start_block': start_block,
            'end_block': end_block
        }

    async def _broadcast_to_peers(self, message: dict):
        ###"""Broadcast a message to all connected peers###"""
        for peer_id, peer in self.peers.items():
            try:
                await self._send_to_peer(peer_id, message)
            except Exception as e:
                logging.error(f"Error broadcasting to peer {peer_id}: {str(e)}")

    async def _send_to_peer(self, peer_id: str, message: dict):
        ###"""Send a message to a specific peer###"""
        if peer_id not in self.peers:
            raise ValueError(f"Unknown peer: {peer_id}")
        logging.debug(f"Sending message to peer {peer_id}: {message['type']}")

    async def _peer_discovery_loop(self):
        ###"""Background task for discovering new peers###"""
        while self.is_running:
            try:
                await asyncio.sleep(30)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logging.error(f"Error in peer discovery: {str(e)}")
                await asyncio.sleep(1)

    async def _message_processing_loop(self):
        ###"""Background task for processing incoming messages###"""
        while self.is_running:
            try:
                if not self.pending_messages.empty():
                    message = await self.pending_messages.get()
                await asyncio.sleep(0.1)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logging.error(f"Error processing messages: {str(e)}")

    async def _network_sync_loop(self):
        ###"""Background task for maintaining network synchronization###"""
        while self.is_running:
            try:
                await self._check_sync_status()
                await asyncio.sleep(60)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logging.error(f"Error in network sync: {str(e)}")

    async def _check_sync_status(self):
        ###"""Check if we're synchronized with the network###"""
        if not self.peers:
            self.sync_status = False
            return

class PeerInfo:
    ###"""Store information about a connected peer###"""
    def __init__(self, peer_id: str, address: str, port: int, connected_at: float):
        self.peer_id = peer_id
        self.address = address
        self.port = port
        self.connected_at = connected_at
        self.last_seen = connected_at
        self.failed_pings = 0

    def to_dict(self) -> dict:
        return {
            'peer_id': self.peer_id,
            'address': self.address,
            'port': self.port,
            'connected_at': self.connected_at,
            'last_seen': self.last_seen,
            'failed_pings': self.failed_pings
        }


||||||| base
=======
# src/agents/blockchain/network_agent.py
from ..base_agent import BaseAgent, AgentCapability
import logging
from uuid import uuid4
import asyncio
from typing import Dict
import time

class NetworkAgent(BaseAgent):
    def __init__(self, agent_id: str = None, max_peers: int = 10):
        if not agent_id:
            agent_id = f"network_agent_{str(uuid4())[:8]}"
        super().__init__(agent_id=agent_id, capabilities=[AgentCapability.BLOCKCHAIN])
        
        self.max_peers = max_peers
        self.peers: Dict[str, 'PeerInfo'] = {}
        self.pending_messages = asyncio.Queue()
        self.is_running = False
        self.sync_status = False
        self.background_tasks = []
        
        logging.info(f"Initialized Network Agent: {agent_id}")

    async def start(self):
        """Start the network agent and its background tasks"""
        self.is_running = True
        await super().start()
        
        # Start background tasks with proper tracking
        self.background_tasks = [
            asyncio.create_task(self._peer_discovery_loop()),
            asyncio.create_task(self._message_processing_loop()),
            asyncio.create_task(self._network_sync_loop())
        ]
        
        logging.info(f"Network Agent {self.agent_id} started")

    async def stop(self):
        """Stop the network agent and cleanup"""
        self.is_running = False
        
        # Cancel all background tasks
        if self.background_tasks:
            for task in self.background_tasks:
                if not task.done():
                    task.cancel()
                    try:
                        await asyncio.wait_for(task, timeout=1.0)
                    except (asyncio.CancelledError, asyncio.TimeoutError):
                        pass
                    except Exception as e:
                        logging.error(f"Error cancelling task: {str(e)}")
        
        self.background_tasks.clear()
        
        # Disconnect all peers
        peer_ids = list(self.peers.keys())
        for peer_id in peer_ids:
            await self.disconnect_peer(peer_id)
        
        # Cleanup queue
        while not self.pending_messages.empty():
            try:
                self.pending_messages.get_nowait()
            except asyncio.QueueEmpty:
                break
                
        await super().stop()
        logging.info(f"Network Agent {self.agent_id} stopped")

    async def connect_peer(self, task: dict) -> bool:
        """Connect to a new peer"""
        peer_id = task.get('peer_id')
        if not peer_id or peer_id in self.peers:
            return False
            
        if len(self.peers) >= self.max_peers:
            logging.warning(f"Max peers ({self.max_peers}) reached, rejecting connection")
            return False
            
        self.peers[peer_id] = PeerInfo(
            peer_id=peer_id,
            address=task.get('address'),
            port=task.get('port'),
            connected_at=time.time()
        )
        logging.info(f"Connected to peer: {peer_id}")
        return True

    async def process_task(self, task: dict) -> dict:
        """Process network-related tasks"""
        try:
            task_type = task.get('type', '')
            handlers = {
                'connect_peer': self.connect_peer,
                'broadcast_transaction': self.broadcast_transaction,
                'broadcast_block': self.broadcast_block,
                'get_peer_info': self.get_peer_info,
                'sync_request': self.handle_sync_request
            }
            
            if task_type in handlers:
                result = await handlers[task_type](task)
                return {
                    'task_id': task.get('task_id'),
                    'status': 'success',
                    'result': result
                }
            else:
                return {
                    'task_id': task.get('task_id'),
                    'status': 'error',
                    'error': f'Unknown task type: {task_type}'
                }
                
        except Exception as e:
            logging.error(f"Error processing network task: {str(e)}")
            return {
                'task_id': task.get('task_id'),
                'status': 'error',
                'error': str(e)
            }

    async def disconnect_peer(self, peer_id: str) -> bool:
        """Disconnect from a peer"""
        if peer_id in self.peers:
            del self.peers[peer_id]
            logging.info(f"Disconnected from peer: {peer_id}")
            return True
        return False

    async def broadcast_transaction(self, task: dict) -> bool:
        """Broadcast a transaction to all peers"""
        transaction = task.get('transaction')
        if not transaction:
            return False
            
        message = {
            'type': 'transaction',
            'data': transaction,
            'timestamp': time.time()
        }
        
        await self._broadcast_to_peers(message)
        return True

    async def broadcast_block(self, task: dict) -> bool:
        """Broadcast a new block to all peers"""
        block = task.get('block')
        if not block:
            return False
            
        message = {
            'type': 'block',
            'data': block,
            'timestamp': time.time()
        }
        
        await self._broadcast_to_peers(message)
        return True

    async def get_peer_info(self, task: dict) -> dict:
        """Get information about connected peers"""
        return {
            'peer_count': len(self.peers),
            'peers': [peer.to_dict() for peer in self.peers.values()],
            'sync_status': self.sync_status
        }

    async def handle_sync_request(self, task: dict) -> dict:
        """Handle a synchronization request from a peer"""
        start_block = task.get('start_block')
        end_block = task.get('end_block')
        peer_id = task.get('peer_id')
        
        if not all([start_block, end_block, peer_id]):
            return {'error': 'Missing required sync parameters'}
            
        return {
            'status': 'sync_started',
            'start_block': start_block,
            'end_block': end_block
        }

    async def _broadcast_to_peers(self, message: dict):
        """Broadcast a message to all connected peers"""
        for peer_id, peer in self.peers.items():
            try:
                await self._send_to_peer(peer_id, message)
            except Exception as e:
                logging.error(f"Error broadcasting to peer {peer_id}: {str(e)}")

    async def _send_to_peer(self, peer_id: str, message: dict):
        """Send a message to a specific peer"""
        if peer_id not in self.peers:
            raise ValueError(f"Unknown peer: {peer_id}")
        logging.debug(f"Sending message to peer {peer_id}: {message['type']}")

    async def _peer_discovery_loop(self):
        """Background task for discovering new peers"""
        while self.is_running:
            try:
                await asyncio.sleep(30)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logging.error(f"Error in peer discovery: {str(e)}")
                await asyncio.sleep(1)

    async def _message_processing_loop(self):
        """Background task for processing incoming messages"""
        while self.is_running:
            try:
                if not self.pending_messages.empty():
                    message = await self.pending_messages.get()
                await asyncio.sleep(0.1)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logging.error(f"Error processing messages: {str(e)}")

    async def _network_sync_loop(self):
        """Background task for maintaining network synchronization"""
        while self.is_running:
            try:
                await self._check_sync_status()
                await asyncio.sleep(60)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logging.error(f"Error in network sync: {str(e)}")

    async def _check_sync_status(self):
        """Check if we're synchronized with the network"""
        if not self.peers:
            self.sync_status = False
            return

class PeerInfo:
    """Store information about a connected peer"""
    def __init__(self, peer_id: str, address: str, port: int, connected_at: float):
        self.peer_id = peer_id
        self.address = address
        self.port = port
        self.connected_at = connected_at
        self.last_seen = connected_at
        self.failed_pings = 0

    def to_dict(self) -> dict:
        return {
            'peer_id': self.peer_id,
            'address': self.address,
            'port': self.port,
            'connected_at': self.connected_at,
            'last_seen': self.last_seen,
            'failed_pings': self.failed_pings
        }
>>>>>>> theirs
