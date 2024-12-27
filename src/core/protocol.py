from typing import Dict, Any, Optional, Callable, List
from enum import Enum
import asyncio
import json
import uuid
from dataclasses import dataclass
import time
import logging


class ProtocolMessageType(Enum):
    # System messages
    REGISTER = "register"
    HEARTBEAT = "heartbeat"
    SHUTDOWN = "shutdown"
    
    # Task-related messages
    TASK_REQUEST = "task_request"
    TASK_ASSIGNMENT = "task_assignment"
    TASK_STATUS = "task_status"
    TASK_RESULT = "task_result"
    
    # Capability messages
    CAPABILITY_UPDATE = "capability_update"
    CAPABILITY_QUERY = "capability_query"
    
    # Load balancing messages
    LOAD_REPORT = "load_report"
    LOAD_QUERY = "load_query"
    
    # Error messages
    ERROR = "error"
    WARNING = "warning"


@dataclass
class ProtocolMessage:
    """
    Standardized message format for agent communication.
    """
    message_id: str
    message_type: ProtocolMessageType
    sender: str
    recipient: str
    payload: Dict[str, Any]
    timestamp: float
    correlation_id: Optional[str] = None
    reply_to: Optional[str] = None
    ttl: int = 3600  # Time-to-live in seconds


class CommunicationProtocol:
    """
    Implements the agent communication protocol.
    Manages message creation, serialization, and handling.
    """

    def __init__(self):
        self.logger = logging.getLogger("CommunicationProtocol")
        self._message_handlers: Dict[ProtocolMessageType, List[Callable]] = {}
        self._pending_responses: Dict[str, asyncio.Future] = {}
        self._message_history: Dict[str, ProtocolMessage] = {}

    def create_message(self,
                       message_type: ProtocolMessageType,
                       sender: str,
                       recipient: str,
                       payload: Dict[str, Any],
                       correlation_id: Optional[str] = None,
                       reply_to: Optional[str] = None) -> ProtocolMessage:
        """
        Create a new protocol message.
        """
        self.logger.debug(f"Creating message of type {message_type} from {sender} to {recipient}")
        return ProtocolMessage(
            message_id=str(uuid.uuid4()),
            message_type=message_type,
            sender=sender,
            recipient=recipient,
            payload=payload,
            timestamp=time.time(),
            correlation_id=correlation_id,
            reply_to=reply_to
        )

    async def send_message(self, message: ProtocolMessage) -> Optional[ProtocolMessage]:
        """
        Send a message and optionally wait for a response if `reply_to` is set.
        """
        self.logger.info(f"Sending message {message.message_id} of type {message.message_type}")
        self._message_history[message.message_id] = message

        # Create a future for response if a reply is expected
        if message.reply_to:
            response_future = asyncio.Future()
            self._pending_responses[message.message_id] = response_future

        # Handle the message
        await self._handle_message(message)

        # Wait for a response if needed
        if message.reply_to:
            try:
                response = await asyncio.wait_for(
                    self._pending_responses[message.message_id],
                    timeout=30  # Configurable timeout
                )
                return response
            except asyncio.TimeoutError:
                self.logger.warning(f"Response for message {message.message_id} timed out.")
                del self._pending_responses[message.message_id]
                return None
        return None

    async def _handle_message(self, message: ProtocolMessage):
        """
        Handle an incoming message.
        """
        self.logger.debug(f"Handling message {message.message_id} of type {message.message_type}")

        # Check if the message has expired
        if time.time() - message.timestamp > message.ttl:
            self.logger.warning(f"Message {message.message_id} has expired.")
            return

        # Handle responses to pending messages
        if message.correlation_id and message.correlation_id in self._pending_responses:
            future = self._pending_responses[message.correlation_id]
            if not future.done():
                future.set_result(message)
            del self._pending_responses[message.correlation_id]
            return

        # Process the message with registered handlers
        if message.message_type in self._message_handlers:
            for handler in self._message_handlers[message.message_type]:
                try:
                    await handler(message)
                except Exception as e:
                    self.logger.error(f"Error in handler for message {message.message_id}: {str(e)}")
                    error_message = self.create_message(
                        message_type=ProtocolMessageType.ERROR,
                        sender="system",
                        recipient=message.sender,
                        payload={"error": str(e)},
                        correlation_id=message.message_id
                    )
                    await self.send_message(error_message)

    def register_handler(self, message_type: ProtocolMessageType, handler: Callable):
        """
        Register a handler for a specific message type.
        """
        self.logger.info(f"Registering handler for message type {message_type}")
        if message_type not in self._message_handlers:
            self._message_handlers[message_type] = []
        self._message_handlers[message_type].append(handler)

    def serialize_message(self, message: ProtocolMessage) -> str:
        """
        Serialize a message for transmission.
        """
        self.logger.debug(f"Serializing message {message.message_id}")
        return json.dumps({
            "message_id": message.message_id,
            "message_type": message.message_type.value,
            "sender": message.sender,
            "recipient": message.recipient,
            "payload": message.payload,
            "timestamp": message.timestamp,
            "correlation_id": message.correlation_id,
            "reply_to": message.reply_to,
            "ttl": message.ttl
        })

    @staticmethod
    def deserialize_message(data: str) -> ProtocolMessage:
        """
        Deserialize a received message.
        """
        try:
            msg_dict = json.loads(data)
            return ProtocolMessage(
                message_id=msg_dict["message_id"],
                message_type=ProtocolMessageType(msg_dict["message_type"]),
                sender=msg_dict["sender"],
                recipient=msg_dict["recipient"],
                payload=msg_dict["payload"],
                timestamp=msg_dict["timestamp"],
                correlation_id=msg_dict.get("correlation_id"),
                reply_to=msg_dict.get("reply_to"),
                ttl=msg_dict.get("ttl", 3600)
            )
        except (json.JSONDecodeError, KeyError) as e:
            logging.error(f"Failed to deserialize message: {str(e)}")
            raise ValueError("Invalid message format") from e
