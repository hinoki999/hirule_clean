import asyncio
import logging
from uuid import uuid4
from typing import Optional, Dict, Any
import pytest
from aiomqtt import Client
from monitoring.protocol.mqtt_monitor import MQTTMonitor

class MQTTAgent:
    def __init__(self):
        self.monitor = MQTTMonitor()

    async def start(self):
        await self.monitor.start_monitoring(self.handle_monitoring_update)

    async def handle_monitoring_update(self, metrics: Dict, health_status: bool):
        if not health_status:
            await self.handle_health_issue(metrics)

    async def handle_health_issue(self, metrics: Dict):
        # Implement recovery logic
        pass

@pytest.mark.asyncio
async def test_mqtt_connection():
    async with Client("localhost") as client:
        assert client.is_connected
        await client.disconnect()

try:
    import asyncio_mqtt
    from asyncio_mqtt import Client as AsyncioMQTTClient, MqttError
    from typing import TYPE_CHECKING
    if TYPE_CHECKING:
        from asyncio_mqtt import Client as AsyncioMQTTClient
except ImportError:
    asyncio_mqtt = None
    AsyncioMQTTClient = None

from src.agents.base import BaseAgent, AgentCapability
from src.communication.messages import Message

class MQTTAgent(BaseAgent):
    def __init__(self,
                 agent_id: str = None,
                 host: str = "localhost",
                 port: int = 1883,
                 username: Optional[str] = None,
                 password: Optional[str] = None,
                 client_id: Optional[str] = None):
        ###"""Initialize MQTT Agent.

        Args:
            agent_id: Unique identifier for this agent
            host: MQTT broker hostname
            port: MQTT broker port
            username: Optional username for authentication
            password: Optional password for authentication
            client_id: Optional client ID for MQTT connection
        ###"""
        if not agent_id:
            agent_id = f"mqtt_agent_{str(uuid4())[:8]}"

        super().__init__(agent_id=agent_id, capabilities=[AgentCapability.PROTOCOL])

        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self._client: Optional['AsyncioMQTTClient'] = None
        self.protocol = "MQTT"

        self._listener_task = None
        self.logger = logging.getLogger(self.agent_id)
        self.is_running = False

        self.logger.info(f"Initialized MQTTAgent: {agent_id}")

    async def setup(self):
        ###"""Initialize the MQTT client and connect to broker.###"""
        try:
            await super().setup()

            if not asyncio_mqtt:
                self.logger.warning("asyncio-mqtt not installed. MQTT functionality will be limited.")
                return

            self._client = Client(
                hostname=self.host,
                port=self.port,
                username=self.username,
                password=self.password,
                client_id=self.client_id
            )

            await self._client.connect()
            self.is_running = True
            self.logger.info(f"Connected to MQTT broker at {self.host}:{self.port}")

        except Exception as e:
            self.logger.error(f"Error during setup: {e}")
            self.is_running = False
            raise

    async def start(self):
        ###"""Start the MQTT agent and initialize subscriptions.###"""
        if not self.is_running:
            await self.setup()
        await self.post_start()
        self.is_running = True

    async def post_start(self):
        ###"""Post-start initialization and subscription setup.###"""
        try:
            await super().post_start()
            if self._client:
                self._listener_task = asyncio.create_task(self._message_listener())
                self.logger.info("MQTT message listener started")
        except Exception as e:
            self.logger.error(f"Error during post_start: {e}")
            self.is_running = False
            raise

    async def cleanup(self):
        ###"""Cleanup resources and disconnect from broker.###"""
        try:
            if self._listener_task and not self._listener_task.done():
                self._listener_task.cancel()
                try:
                    await self._listener_task
                except asyncio.CancelledError:
                    pass

            if self._client:
                await self._client.disconnect()
                self.logger.info("Disconnected from MQTT broker")

            await super().cleanup()
        finally:
            self.is_running = False
            self._client = None

    async def process_message(self, message: Message):
        ###"""Process incoming messages from the message bus.###"""
        try:
            self.logger.info(f"Received Message ID {message.id}, Type: {message.message_type}")

            if message.message_type == "mqtt_publish":
                response_data = await self.publish(message.content)
                reply = self.message_bus.create_message(
                    sender=self.agent_id,
                    recipient_id=message.sender_id,
                    message_type="mqtt_response",
                    content=response_data
                )
                await self.message_bus.publish(reply)
            else:
                self.logger.debug(f"Unhandled message type: {message.message_type}")

        except Exception as e:
            self.logger.error(f"Error processing message: {e}")
            raise

    async def publish(self, request: Dict[str, Any]) -> Dict[str, Any]:
        ###"""Publish a message to an MQTT topic.

        Args:
            request: Dictionary containing topic and payload

        Returns:
            Dict containing status and response info
        ###"""
        try:
            if not isinstance(request, dict):
                raise ValueError("Request must be a dictionary")

            self.logger.info(f"Processing MQTT publish request: {request}")

            if not self._client:
                return {
                    "status": "error",
                    "message": "MQTT client not initialized"
                }

            topic = request.get('topic')
            payload = request.get('payload')
            qos = request.get('qos', 0)

            if not topic:
                return {
                    "status": "error",
                    "message": "Topic is required"
                }

            await self._client.publish(topic, payload, qos=qos)

            return {
                "status": "success",
                "protocol": self.protocol,
                "agent_id": self.agent_id,
                "topic": topic,
                "message": f"Published to {topic}"
            }

        except Exception as e:
            self.logger.error(f"Error in publish: {str(e)}")
            return {
                "status": "error",
                "message": str(e)
            }

    async def _message_listener(self):
        ###"""Listen for incoming MQTT messages.###"""
        try:
            if not self._client:
                return

            async with self._client.messages() as messages:
                await self._client.subscribe("#")  # Subscribe to all topics
                self.logger.info("Subscribed to MQTT topics")

                async for message in messages:
                    try:
                        await self._handle_mqtt_message(message)
                    except Exception as e:
                        self.logger.error(f"Error handling MQTT message: {e}")

        except asyncio.CancelledError:
            self.logger.info("MQTT message listener cancelled")
            raise
        except Exception as e:
            self.logger.error(f"Error in message listener: {e}")
            raise

    async def _handle_mqtt_message(self, mqtt_message):
        ###"""Handle incoming MQTT messages and forward to message bus.###"""
        try:
            message_data = {
                "topic": mqtt_message.topic,
                "payload": mqtt_message.payload.decode(),
                "qos": mqtt_message.qos,
                "retain": mqtt_message.retain
            }

            # Create and publish message to bus
            message = self.message_bus.create_message(
                sender=self.agent_id,
                recipient_id="broadcast",
                message_type="mqtt_message",
                content=message_data
            )
            await self.message_bus.publish(message)

        except Exception as e:
            self.logger.error(f"Error handling MQTT message: {e}")
            raise


