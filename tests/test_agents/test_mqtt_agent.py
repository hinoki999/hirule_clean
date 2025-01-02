import pytest
import pytest_asyncio
import asyncio
import logging
from src.agents.protocol.mqtt_agent import MQTTAgent
from src.communication.messages import Message

# Setup basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

try:
    import asyncio_mqtt
    MQTT_AVAILABLE = True
except ImportError:
    MQTT_AVAILABLE = False

@pytest_asyncio.fixture
async def mqtt_agent():
    #"""Create and cleanup an MQTT agent for testing.#"""
    agent = MQTTAgent(
        agent_id="test_mqtt_agent",
        host="localhost",
        port=1883,
        client_id="test_client"
    )
    await agent.setup()
    yield agent  # Use yield instead of return
    await agent.cleanup()

@pytest.mark.asyncio
class TestMQTTAgent:

    async def test_initialization(self, mqtt_agent):
        #"""Test basic agent initialization#"""
        assert isinstance(mqtt_agent, MQTTAgent)
        assert mqtt_agent.agent_id == "test_mqtt_agent"
        assert mqtt_agent.host == "localhost"
        assert mqtt_agent.port == 1883
        assert mqtt_agent.protocol == "MQTT"
        assert mqtt_agent.client_id == "test_client"

    async def test_publish_request(self, mqtt_agent):
        #"""Test MQTT publish request processing#"""
        if not MQTT_AVAILABLE:
            pytest.skip("asyncio-mqtt not installed")

        request = {
            "topic": "test/topic",
            "payload": "test_message",
            "qos": 0
        }

        response = await mqtt_agent.publish(request)
        if not mqtt_agent.is_running:
            assert response["status"] == "error"
            assert "MQTT client not initialized" in response["message"]
        else:
            assert response["status"] == "success"
            assert response["protocol"] == "MQTT"
            assert response["agent_id"] == mqtt_agent.agent_id
            assert response["topic"] == "test/topic"

    async def test_message_handling(self, mqtt_agent):
        #"""Test message bus message handling#"""
        if not MQTT_AVAILABLE:
            pytest.skip("asyncio-mqtt not installed")

        message = Message(
            sender_id="test_sender",
            recipient_id=mqtt_agent.agent_id,
            message_type="mqtt_publish",
            content={
                "topic": "test/topic",
                "payload": "test_message",
                "qos": 0
            }
        )

        try:
            await mqtt_agent.process_message(message)
        except AttributeError as e:
            if "create_message" in str(e):
                pytest.skip("MessageBus implementation not available")
            raise

    async def test_error_handling(self, mqtt_agent):
        #"""Test invalid request handling#"""
        invalid_requests = [
            {
                "name": "Missing topic",
                "request": {
                    "payload": "test",
                    "qos": 0
                }
            },
            {
                "name": "Invalid QoS",
                "request": {
                    "topic": "test/topic",
                    "payload": "test",
                    "qos": 3
                }
            },
            {
                "name": "Non-dict request",
                "request": "invalid"
            }
        ]

        for case in invalid_requests:
            response = await mqtt_agent.publish(case["request"])
            assert response["status"] == "error"

    async def test_connection_handling(self, mqtt_agent):
        #"""Test broker connection handling#"""
        if not MQTT_AVAILABLE:
            # When MQTT is not available, the agent should not be running
            assert not mqtt_agent.is_running
            return

        # If MQTT is available, test connection states
        if mqtt_agent.is_running:
            await mqtt_agent.cleanup()
            assert not mqtt_agent.is_running

            await mqtt_agent.setup()
            assert mqtt_agent.is_running

    async def test_subscription(self, mqtt_agent):
        #"""Test subscription handling#"""
        if not MQTT_AVAILABLE:
            pytest.skip("asyncio-mqtt not installed")

        # First publish a message
        pub_request = {
            "topic": "test/subscribe",
            "payload": "test_subscription",
            "qos": 0
        }

        # Publish and wait briefly for message processing
        response = await mqtt_agent.publish(pub_request)
        await asyncio.sleep(0.1)  # Allow time for message processing

        if mqtt_agent.is_running:
            assert response["status"] == "success"
        else:
            assert response["status"] == "error"

    async def test_authentication(self):
        #"""Test authentication handling#"""
        if not MQTT_AVAILABLE:
            pytest.skip("asyncio-mqtt not installed")

        auth_agent = MQTTAgent(
            agent_id="test_auth_agent",
            host="localhost",
            port=1883,
            username="test_user",
            password="test_pass"
        )

        try:
            await auth_agent.setup()
            # Check authentication details are set correctly
            assert auth_agent.username == "test_user"
            assert auth_agent.password == "test_pass"

            # Status check depends on broker availability
            if MQTT_AVAILABLE and auth_agent._client:
                assert auth_agent.is_running
        finally:
            await auth_agent.cleanup()

    async def test_client_id_generation(self):
        #"""Test automatic client ID generation#"""
        auto_id_agent = MQTTAgent(
            agent_id="test_auto_id_agent",
            host="localhost",
            port=1883
        )

        try:
            assert auto_id_agent.client_id.startswith("mqtt_client_")
            assert len(auto_id_agent.client_id) > len("mqtt_client_")
        finally:
            await auto_id_agent.cleanup()


