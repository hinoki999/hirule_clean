<<<<<<< ours
from typing import Dict, Any, Optional, Callable, Awaitable
from abc import ABC, abstractmethod
import asyncio
import logging
from datetime import datetime
from src.core.protocol import ProtocolMessage, ProtocolMessageType
from src.agents.base import BaseAgent
from src.core.config import Config
from src.core.messaging import MessageBus
class MessageHandler:
    ###"""Base class for message handlers.###"""

    def __init__(self, agent: BaseAgent):
        self.agent = agent
        self.logger = logging.getLogger(f"{agent.agent_id}_handler")
        self._handlers: Dict[ProtocolMessageType, Callable] = {}
        self.setup_handlers()

    def setup_handlers(self):
        ###"""Setup message type handlers.###"""
        self.register_handler(ProtocolMessageType.HEARTBEAT, self.handle_heartbeat)
        self.register_handler(ProtocolMessageType.ERROR, self.handle_error)

    def register_handler(self,
                        message_type: ProtocolMessageType,
                        handler: Callable[[ProtocolMessage], Awaitable[None]]):
        ###"""Register a handler for a message type.###"""
        self._handlers[message_type] = handler

    async def handle_message(self, message: ProtocolMessage):
        ###"""Handle incoming message.###"""
        try:
            if message.message_type in self._handlers:
                await self._handlers[message.message_type](message)
            else:
                self.logger.warning(f"No handler for message type: {message.message_type}")
        except Exception as e:
            self.logger.error(f"Error handling message: {str(e)}")
            await self.handle_error(message, str(e))

    async def handle_heartbeat(self, message: ProtocolMessage):
        ###"""Handle heartbeat messages.###"""
        pass  # Default implementation

    async def handle_error(self, message: ProtocolMessage, error: str = None):
        ###"""Handle error messages.###"""
        self.logger.error(f"Error in message {message.message_id}: {error or message.payload.get('error')}")

class TaskAgentHandler(MessageHandler):
    ###"""Handler for task-executing agents.###"""

    def setup_handlers(self):
        super().setup_handlers()
        self.register_handler(ProtocolMessageType.TASK_ASSIGNMENT, self.handle_task_assignment)
        self.register_handler(ProtocolMessageType.TASK_REQUEST, self.handle_task_request)

    async def handle_task_assignment(self, message: ProtocolMessage):
        ###"""Handle new task assignments.###"""
        task_info = message.payload
        task_id = task_info["task_id"]

        try:
            # Update agent's task queue
            await self.agent.add_task(task_id, task_info)

            # Acknowledge receipt
            response = self.agent.protocol.create_message(
                message_type=ProtocolMessageType.TASK_STATUS,
                sender=self.agent.agent_id,
                recipient=message.sender,
                payload={
                    "task_id": task_id,
                    "status": "ACCEPTED"
                },
                correlation_id=message.message_id
            )
            await self.agent.protocol.send_message(response)

        except Exception as e:
            # Report failure
            error_response = self.agent.protocol.create_message(
                message_type=ProtocolMessageType.ERROR,
                sender=self.agent.agent_id,
                recipient=message.sender,
                payload={
                    "task_id": task_id,
                    "error": str(e)
                },
                correlation_id=message.message_id
            )
            await self.agent.protocol.send_message(error_response)

    async def handle_task_request(self, message: ProtocolMessage):
        ###"""Handle task requests.###"""
        # Implement based on agent capabilities
        pass

class ProtocolAgentHandler(MessageHandler):
    ###"""Handler for protocol-translating agents.###"""

    def setup_handlers(self):
        super().setup_handlers()
        self.register_handler(ProtocolMessageType.CAPABILITY_QUERY, self.handle_capability_query)
        self.register_handler(ProtocolMessageType.PROTOCOL_TRANSLATION, self.handle_protocol_translation)

    async def handle_capability_query(self, message: ProtocolMessage):
        ###"""Handle capability queries.###"""
        response = self.agent.protocol.create_message(
            message_type=ProtocolMessageType.CAPABILITY_UPDATE,
            sender=self.agent.agent_id,
            recipient=message.sender,
            payload={
                "capabilities": [cap.name for cap in self.agent.capabilities]
            },
            correlation_id=message.message_id
        )
        await self.agent.protocol.send_message(response)

    async def handle_protocol_translation(self, message: ProtocolMessage):
        ###"""Handle protocol translation requests.###"""
        # Implement protocol translation logic
        pass


||||||| base
=======
from typing import Dict, Any, Optional, Callable, Awaitable
from abc import ABC, abstractmethod
import asyncio
import logging
from datetime import datetime
from src.core.protocol import ProtocolMessage, ProtocolMessageType
from src.agents.base import BaseAgent
from src.core.config import Config
from src.core.messaging import MessageBus
class MessageHandler:
    """Base class for message handlers."""
    
    def __init__(self, agent: BaseAgent):
        self.agent = agent
        self.logger = logging.getLogger(f"{agent.agent_id}_handler")
        self._handlers: Dict[ProtocolMessageType, Callable] = {}
        self.setup_handlers()

    def setup_handlers(self):
        """Setup message type handlers."""
        self.register_handler(ProtocolMessageType.HEARTBEAT, self.handle_heartbeat)
        self.register_handler(ProtocolMessageType.ERROR, self.handle_error)

    def register_handler(self, 
                        message_type: ProtocolMessageType, 
                        handler: Callable[[ProtocolMessage], Awaitable[None]]):
        """Register a handler for a message type."""
        self._handlers[message_type] = handler

    async def handle_message(self, message: ProtocolMessage):
        """Handle incoming message."""
        try:
            if message.message_type in self._handlers:
                await self._handlers[message.message_type](message)
            else:
                self.logger.warning(f"No handler for message type: {message.message_type}")
        except Exception as e:
            self.logger.error(f"Error handling message: {str(e)}")
            await self.handle_error(message, str(e))

    async def handle_heartbeat(self, message: ProtocolMessage):
        """Handle heartbeat messages."""
        pass  # Default implementation

    async def handle_error(self, message: ProtocolMessage, error: str = None):
        """Handle error messages."""
        self.logger.error(f"Error in message {message.message_id}: {error or message.payload.get('error')}")

class TaskAgentHandler(MessageHandler):
    """Handler for task-executing agents."""
    
    def setup_handlers(self):
        super().setup_handlers()
        self.register_handler(ProtocolMessageType.TASK_ASSIGNMENT, self.handle_task_assignment)
        self.register_handler(ProtocolMessageType.TASK_REQUEST, self.handle_task_request)

    async def handle_task_assignment(self, message: ProtocolMessage):
        """Handle new task assignments."""
        task_info = message.payload
        task_id = task_info["task_id"]
        
        try:
            # Update agent's task queue
            await self.agent.add_task(task_id, task_info)
            
            # Acknowledge receipt
            response = self.agent.protocol.create_message(
                message_type=ProtocolMessageType.TASK_STATUS,
                sender=self.agent.agent_id,
                recipient=message.sender,
                payload={
                    "task_id": task_id,
                    "status": "ACCEPTED"
                },
                correlation_id=message.message_id
            )
            await self.agent.protocol.send_message(response)
            
        except Exception as e:
            # Report failure
            error_response = self.agent.protocol.create_message(
                message_type=ProtocolMessageType.ERROR,
                sender=self.agent.agent_id,
                recipient=message.sender,
                payload={
                    "task_id": task_id,
                    "error": str(e)
                },
                correlation_id=message.message_id
            )
            await self.agent.protocol.send_message(error_response)

    async def handle_task_request(self, message: ProtocolMessage):
        """Handle task requests."""
        # Implement based on agent capabilities
        pass

class ProtocolAgentHandler(MessageHandler):
    """Handler for protocol-translating agents."""
    
    def setup_handlers(self):
        super().setup_handlers()
        self.register_handler(ProtocolMessageType.CAPABILITY_QUERY, self.handle_capability_query)
        self.register_handler(ProtocolMessageType.PROTOCOL_TRANSLATION, self.handle_protocol_translation)

    async def handle_capability_query(self, message: ProtocolMessage):
        """Handle capability queries."""
        response = self.agent.protocol.create_message(
            message_type=ProtocolMessageType.CAPABILITY_UPDATE,
            sender=self.agent.agent_id,
            recipient=message.sender,
            payload={
                "capabilities": [cap.name for cap in self.agent.capabilities]
            },
            correlation_id=message.message_id
        )
        await self.agent.protocol.send_message(response)

    async def handle_protocol_translation(self, message: ProtocolMessage):
        """Handle protocol translation requests."""
        # Implement protocol translation logic
        pass
>>>>>>> theirs
