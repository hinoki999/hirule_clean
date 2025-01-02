<<<<<<< ours
from src.agents.base import BaseAgent  # Update to explicit import
from src.core.protocol import ProtocolMessageType, ProtocolMessage
import asyncio
import logging

class ProtocolAgent(BaseAgent):
    ###"""
    Protocol Agent for handling protocol translation.
    ###"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.translations = {
            "mqtt": self._handle_mqtt,
            "coap": self._handle_coap,
            "http3": self._handle_http3,
        }

    async def setup(self):
        ###"""Setup protocol agent.###"""
        self.logger.info(f"Setting up Protocol Agent {self.agent_id}")
        self.register_handler(ProtocolMessageType.PROTOCOL_TRANSLATION, self.handle_translation)

    async def handle_translation(self, message: ProtocolMessage):
        ###"""Handle protocol translation requests.###"""
        source_protocol = message.payload.get("source_protocol")
        target_protocol = message.payload.get("target_protocol")
        data = message.payload.get("data")

        if source_protocol in self.translations:
            translated_data = await self.translations[source_protocol](data, target_protocol)
            response = self.protocol.create_message(
                message_type=ProtocolMessageType.PROTOCOL_TRANSLATION,
                sender=self.agent_id,
                recipient=message.sender,
                payload={"translated_data": translated_data},
                correlation_id=message.message_id
            )
            await self.protocol.send_message(response)
        else:
            self.logger.error(f"Unsupported protocol: {source_protocol}")
            error_response = self.protocol.create_message(
                message_type=ProtocolMessageType.ERROR,
                sender=self.agent_id,
                recipient=message.sender,
                payload={"error": f"Unsupported protocol: {source_protocol}"},
                correlation_id=message.message_id
            )
            await self.protocol.send_message(error_response)

    async def _handle_mqtt(self, data, target_protocol):
        ###"""Translate MQTT data to target protocol.###"""
        # Add actual MQTT parsing and conversion logic
        self.logger.info(f"Translating MQTT data to {target_protocol}")
        return f"MQTT data converted to {target_protocol}"

    async def _handle_coap(self, data, target_protocol):
        ###"""Translate CoAP data to target protocol.###"""
        # Add actual CoAP parsing and conversion logic
        self.logger.info(f"Translating CoAP data to {target_protocol}")
        return f"CoAP data converted to {target_protocol}"

    async def _handle_http3(self, data, target_protocol):
        ###"""Translate HTTP/3 data to target protocol.###"""
        # Add actual HTTP/3 parsing and conversion logic
        self.logger.info(f"Translating HTTP/3 data to {target_protocol}")
        return f"HTTP/3 data converted to {target_protocol}"


||||||| base
=======
from src.agents.base import BaseAgent  # Update to explicit import
from src.core.protocol import ProtocolMessageType, ProtocolMessage
import asyncio
import logging

class ProtocolAgent(BaseAgent):
    """
    Protocol Agent for handling protocol translation.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.translations = {
            "mqtt": self._handle_mqtt,
            "coap": self._handle_coap,
            "http3": self._handle_http3,
        }

    async def setup(self):
        """Setup protocol agent."""
        self.logger.info(f"Setting up Protocol Agent {self.agent_id}")
        self.register_handler(ProtocolMessageType.PROTOCOL_TRANSLATION, self.handle_translation)

    async def handle_translation(self, message: ProtocolMessage):
        """Handle protocol translation requests."""
        source_protocol = message.payload.get("source_protocol")
        target_protocol = message.payload.get("target_protocol")
        data = message.payload.get("data")

        if source_protocol in self.translations:
            translated_data = await self.translations[source_protocol](data, target_protocol)
            response = self.protocol.create_message(
                message_type=ProtocolMessageType.PROTOCOL_TRANSLATION,
                sender=self.agent_id,
                recipient=message.sender,
                payload={"translated_data": translated_data},
                correlation_id=message.message_id
            )
            await self.protocol.send_message(response)
        else:
            self.logger.error(f"Unsupported protocol: {source_protocol}")
            error_response = self.protocol.create_message(
                message_type=ProtocolMessageType.ERROR,
                sender=self.agent_id,
                recipient=message.sender,
                payload={"error": f"Unsupported protocol: {source_protocol}"},
                correlation_id=message.message_id
            )
            await self.protocol.send_message(error_response)

    async def _handle_mqtt(self, data, target_protocol):
        """Translate MQTT data to target protocol."""
        # Add actual MQTT parsing and conversion logic
        self.logger.info(f"Translating MQTT data to {target_protocol}")
        return f"MQTT data converted to {target_protocol}"

    async def _handle_coap(self, data, target_protocol):
        """Translate CoAP data to target protocol."""
        # Add actual CoAP parsing and conversion logic
        self.logger.info(f"Translating CoAP data to {target_protocol}")
        return f"CoAP data converted to {target_protocol}"

    async def _handle_http3(self, data, target_protocol):
        """Translate HTTP/3 data to target protocol."""
        # Add actual HTTP/3 parsing and conversion logic
        self.logger.info(f"Translating HTTP/3 data to {target_protocol}")
        return f"HTTP/3 data converted to {target_protocol}"
>>>>>>> theirs
