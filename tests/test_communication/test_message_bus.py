<<<<<<< ours
# tests/test_communication/test_message_bus.py
import pytest
import asyncio
import logging
from pytest_asyncio import fixture
from src.communication.message_bus import MessageBus
from src.communication.messages import Message, MessageStatus

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@pytest.mark.asyncio
class TestMessageBus:
    @fixture
    async def message_bus(self):
        #"""MessageBus fixture with proper setup/teardown#"""
        logger.debug("Setting up MessageBus fixture")
        bus = MessageBus()
        await bus.start()
        try:
            yield bus
        finally:
            logger.debug("Starting fixture cleanup")
            try:
                if not bus.message_queue.empty():
                    logger.debug("Waiting for message queue to drain")
                    await asyncio.wait_for(bus.message_queue.join(), timeout=1.0)
            except asyncio.TimeoutError:
                logger.warning("Timeout waiting for message queue to drain")

            logger.debug("Stopping message bus")
            await bus.stop()
            logger.debug("Fixture cleanup complete")

    async def test_message_bus_startup(self, message_bus: MessageBus):
        #"""Test MessageBus initialization and startup#"""
        logger.debug("Starting message_bus_startup test")
        assert message_bus.is_running

        logger.debug("Stopping message bus")
        await message_bus.stop()
        assert not message_bus.is_running

        logger.debug("Restarting message bus")
        await message_bus.start()
        assert message_bus.is_running
        logger.debug("Startup test complete")

    async def test_basic_message_publishing(self, message_bus: MessageBus):
        #"""Test basic message publishing#"""
        logger.debug("Starting basic_message_publishing test")
        message = Message(
            sender_id="test_sender",
            recipient_id="test_recipient",
            message_type="test",
            content={"data": "test"}
        )

        logger.debug(f"Publishing test message {message.id}")
        success = await message_bus.publish(message)
        assert success, "Message publishing failed"
        assert message.id in message_bus.message_history

        # Wait for message processing
        logger.debug("Waiting for message processing")
        await message_bus.message_queue.join()

        assert message.status in (MessageStatus.QUEUED, MessageStatus.DELIVERED)
        logger.debug("Publishing test complete")

    async def test_message_delivery(self, message_bus: MessageBus):
        #"""Test message delivery to subscribers#"""
        logger.debug("Starting message_delivery test")
        received_messages = []
        delivery_event = asyncio.Event()

        async def test_handler(message):
            logger.debug(f"Test handler received message {message.id}")
            received_messages.append(message)
            delivery_event.set()

        logger.debug("Subscribing test handler")
        await message_bus.subscribe("test_type", test_handler)

        message = Message(
            sender_id="test_sender",
            recipient_id="test_recipient",
            message_type="test_type",
            content={"test": "data"}
        )

        logger.debug(f"Publishing test message {message.id}")
        await message_bus.publish(message)

        try:
            logger.debug("Waiting for message delivery")
            await asyncio.wait_for(delivery_event.wait(), timeout=2.0)
            assert len(received_messages) == 1
            assert received_messages[0].id == message.id
            logger.debug("Message delivered successfully")
        except asyncio.TimeoutError:
            logger.error("Message delivery timeout")
            pytest.fail("Message was not delivered within timeout")


||||||| base
=======
# tests/test_communication/test_message_bus.py
import pytest
import asyncio
import logging
from pytest_asyncio import fixture
from src.communication.message_bus import MessageBus
from src.communication.messages import Message, MessageStatus

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@pytest.mark.asyncio
class TestMessageBus:
    @fixture
    async def message_bus(self):
        """MessageBus fixture with proper setup/teardown"""
        logger.debug("Setting up MessageBus fixture")
        bus = MessageBus()
        await bus.start()
        try:
            yield bus
        finally:
            logger.debug("Starting fixture cleanup")
            try:
                if not bus.message_queue.empty():
                    logger.debug("Waiting for message queue to drain")
                    await asyncio.wait_for(bus.message_queue.join(), timeout=1.0)
            except asyncio.TimeoutError:
                logger.warning("Timeout waiting for message queue to drain")
            
            logger.debug("Stopping message bus")
            await bus.stop()
            logger.debug("Fixture cleanup complete")

    async def test_message_bus_startup(self, message_bus: MessageBus):
        """Test MessageBus initialization and startup"""
        logger.debug("Starting message_bus_startup test")
        assert message_bus.is_running
        
        logger.debug("Stopping message bus")
        await message_bus.stop()
        assert not message_bus.is_running
        
        logger.debug("Restarting message bus")
        await message_bus.start()
        assert message_bus.is_running
        logger.debug("Startup test complete")

    async def test_basic_message_publishing(self, message_bus: MessageBus):
        """Test basic message publishing"""
        logger.debug("Starting basic_message_publishing test")
        message = Message(
            sender_id="test_sender",
            recipient_id="test_recipient",
            message_type="test",
            content={"data": "test"}
        )
        
        logger.debug(f"Publishing test message {message.id}")
        success = await message_bus.publish(message)
        assert success, "Message publishing failed"
        assert message.id in message_bus.message_history
        
        # Wait for message processing
        logger.debug("Waiting for message processing")
        await message_bus.message_queue.join()
        
        assert message.status in (MessageStatus.QUEUED, MessageStatus.DELIVERED)
        logger.debug("Publishing test complete")

    async def test_message_delivery(self, message_bus: MessageBus):
        """Test message delivery to subscribers"""
        logger.debug("Starting message_delivery test")
        received_messages = []
        delivery_event = asyncio.Event()
        
        async def test_handler(message):
            logger.debug(f"Test handler received message {message.id}")
            received_messages.append(message)
            delivery_event.set()
        
        logger.debug("Subscribing test handler")
        await message_bus.subscribe("test_type", test_handler)
        
        message = Message(
            sender_id="test_sender",
            recipient_id="test_recipient",
            message_type="test_type",
            content={"test": "data"}
        )
        
        logger.debug(f"Publishing test message {message.id}")
        await message_bus.publish(message)
        
        try:
            logger.debug("Waiting for message delivery")
            await asyncio.wait_for(delivery_event.wait(), timeout=2.0)
            assert len(received_messages) == 1
            assert received_messages[0].id == message.id
            logger.debug("Message delivered successfully")
        except asyncio.TimeoutError:
            logger.error("Message delivery timeout")
            pytest.fail("Message was not delivered within timeout")
>>>>>>> theirs
