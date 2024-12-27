# tests/test_communication/test_message_delivery.py
import pytest
import asyncio
import logging
from pytest_asyncio import fixture
from src.communication.message_bus import MessageBus
from src.communication.messages import Message, MessageStatus

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@pytest.mark.asyncio
class TestMessageDelivery:
    @fixture
    async def message_bus(self):
        """MessageBus fixture"""
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

    async def test_message_delivery(self, message_bus: MessageBus):
        """Test basic message delivery"""
        logger.debug("Starting message_delivery test")
        
        message = Message(
            sender_id="test_sender",
            recipient_id="test_recipient",
            message_type="test",
            content={"test": "data"}
        )

        received_messages = []
        delivery_event = asyncio.Event()
        
        async def message_handler(msg):
            logger.debug(f"Message handler received message {msg.id}")
            received_messages.append(msg)
            delivery_event.set()
        
        logger.debug("Subscribing message handler")
        await message_bus.subscribe("test", message_handler)
        
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