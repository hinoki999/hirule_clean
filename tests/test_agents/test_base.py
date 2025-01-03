<<<<<<< ours
import pytest
import pytest_asyncio
import asyncio
import logging
from datetime import datetime, timezone
from typing import Dict, Optional


#
# Minimal stubs for missing classes so this test can run.
# Replace these with your real implementations if they already exist.
#

class Message:
    def __init__(
        self,
        message_type: str,
        timestamp: datetime,
        data: Dict,
        destination_agent_id: str,
        source_agent_id: str,
    ):
        self.message_type = message_type
        self.timestamp = timestamp
        self.data = data
        self.destination_agent_id = destination_agent_id
        self.source_agent_id = source_agent_id


class MessageBus:
    async def start(self):
        raise NotImplementedError

    async def stop(self):
        raise NotImplementedError

    async def send_message(self, message: Message):
        raise NotImplementedError

    async def get_messages(self, agent_id: str):
        raise NotImplementedError


class MockMessageBus(MessageBus):
    #"""A mock message bus for testing purposes.#"""
    def __init__(self):
        self._messages = {}

    async def start(self):
        #"""Start the mock message bus (no-op).#"""
        pass

    async def stop(self):
        #"""Stop the mock message bus (no-op).#"""
        pass

    async def send_message(self, message: Message):
        #"""Store messages in a dictionary by agent ID.#"""
        if message.destination_agent_id not in self._messages:
            self._messages[message.destination_agent_id] = []
        self._messages[message.destination_agent_id].append(message)

    async def get_messages(self, agent_id: str):
        #"""Retrieve all messages for a given agent ID.#"""
        return self._messages.get(agent_id, [])


#
# BaseAgent and BaseTestAgent
#

class BaseAgent:
    def __init__(self, agent_id: str, message_bus: MessageBus):
        self.agent_id = agent_id
        self.message_bus = message_bus
        self.running = False
        self._heartbeat_task: Optional[asyncio.Task] = None
        # Simple logger for demonstration
        self.logger = logging.getLogger(__name__)

    async def setup(self):
        #"""Placeholder for any agent setup you need.#"""
        pass

    async def cleanup(self):
        #"""Placeholder for any cleanup code you need.#"""
        pass

    async def start(self):
        #"""Subclass responsibility.#"""
        raise NotImplementedError

    async def stop(self):
        #"""Subclass responsibility.#"""
        raise NotImplementedError

    async def _start_heartbeat(self):
        #"""Continuously sends heartbeat messages while the agent is running.#"""

        async def heartbeat():
            while self.running:
                msg = Message(
                    message_type="heartbeat",
                    timestamp=datetime.now(timezone.utc),  # use timezone-aware UTC
                    data={},
                    destination_agent_id=self.agent_id,
                    source_agent_id=self.agent_id,
                )
                await self.message_bus.send_message(msg)
                # Adjust sleep as needed for your real environment;
                # shorter sleeps help tests see a heartbeat quickly.
                await asyncio.sleep(0.05)

        self._heartbeat_task = asyncio.create_task(heartbeat())


class BaseTestAgent(BaseAgent):
    #"""Base test agent implementation with heartbeat.#"""

    def __init__(self, agent_id: str, message_bus: MessageBus):
        super().__init__(agent_id, message_bus)
        self._task_queue = None
        self._task_processor = None

    async def start(self):
        #"""Start the agent with proper event loop binding.#"""
        if not self.running:
            self.running = True
            self._task_queue = asyncio.Queue()
            self._task_processor = asyncio.create_task(self._process_tasks())
            await self._start_heartbeat()

    async def _process_tasks(self):
        #"""Process queued tasks.#"""
        try:
            while self.running:
                task = await self._task_queue.get()
                try:
                    await task
                except Exception as e:
                    self.logger.error(f"Error processing task: {e}")
                finally:
                    self._task_queue.task_done()
        except asyncio.CancelledError:
            pass

    async def stop(self):
        #"""Stop the agent and clean up resources.#"""
        if self.running:
            self.running = False

            # Cancel the heartbeat, if it exists
            if self._heartbeat_task:
                self._heartbeat_task.cancel()
                try:
                    await self._heartbeat_task
                except asyncio.CancelledError:
                    pass
                self._heartbeat_task = None

            # Cancel the task processor
            if self._task_processor:
                self._task_processor.cancel()
                try:
                    await self._task_processor
                except asyncio.CancelledError:
                    pass
                self._task_processor = None

            # Make sure we process all tasks in the queue
            if self._task_queue:
                await self._task_queue.join()
                self._task_queue = None


#
# Actual Agent class under test
#

class TestAgent(BaseTestAgent):
    #"""
    We prevent Pytest from thinking this is a test class
    by setting __test__ to False.
    #"""
    __test__ = False

    # Provide any further agent-specific logic here if needed.
    pass


#
# Pytest fixtures
#

@pytest_asyncio.fixture
async def test_agent():
    #"""Fixture to create and clean up a test agent.#"""
    message_bus = MockMessageBus()
    await message_bus.start()

    agent = TestAgent(agent_id="test_agent", message_bus=message_bus)
    await agent.setup()
    yield agent

    # Cleanup
    await agent.cleanup()
    if agent.running:
        await agent.stop()

    await message_bus.stop()


#
# Actual Test
#

@pytest.mark.asyncio
async def test_heartbeat(test_agent: TestAgent):
    #"""Test agent heartbeat functionality.#"""
    await test_agent.start()

    # Sleep briefly so the heartbeat can send at least one message
    await asyncio.sleep(0.1)

    # Check that a heartbeat message was recorded
    messages = await test_agent.message_bus.get_messages(test_agent.agent_id)
    assert any(msg.message_type == "heartbeat" for msg in messages), 
        "Expected at least one heartbeat message."

    # Cleanup
    await test_agent.stop()


||||||| base
=======
import pytest
import pytest_asyncio
import asyncio
import logging
from datetime import datetime, timezone
from typing import Dict, Optional


#
# Minimal stubs for missing classes so this test can run.
# Replace these with your real implementations if they already exist.
#

class Message:
    def __init__(
        self,
        message_type: str,
        timestamp: datetime,
        data: Dict,
        destination_agent_id: str,
        source_agent_id: str,
    ):
        self.message_type = message_type
        self.timestamp = timestamp
        self.data = data
        self.destination_agent_id = destination_agent_id
        self.source_agent_id = source_agent_id


class MessageBus:
    async def start(self):
        raise NotImplementedError

    async def stop(self):
        raise NotImplementedError

    async def send_message(self, message: Message):
        raise NotImplementedError

    async def get_messages(self, agent_id: str):
        raise NotImplementedError


class MockMessageBus(MessageBus):
    """A mock message bus for testing purposes."""
    def __init__(self):
        self._messages = {}

    async def start(self):
        """Start the mock message bus (no-op)."""
        pass

    async def stop(self):
        """Stop the mock message bus (no-op)."""
        pass

    async def send_message(self, message: Message):
        """Store messages in a dictionary by agent ID."""
        if message.destination_agent_id not in self._messages:
            self._messages[message.destination_agent_id] = []
        self._messages[message.destination_agent_id].append(message)

    async def get_messages(self, agent_id: str):
        """Retrieve all messages for a given agent ID."""
        return self._messages.get(agent_id, [])


#
# BaseAgent and BaseTestAgent
#

class BaseAgent:
    def __init__(self, agent_id: str, message_bus: MessageBus):
        self.agent_id = agent_id
        self.message_bus = message_bus
        self.running = False
        self._heartbeat_task: Optional[asyncio.Task] = None
        # Simple logger for demonstration
        self.logger = logging.getLogger(__name__)

    async def setup(self):
        """Placeholder for any agent setup you need."""
        pass

    async def cleanup(self):
        """Placeholder for any cleanup code you need."""
        pass

    async def start(self):
        """Subclass responsibility."""
        raise NotImplementedError

    async def stop(self):
        """Subclass responsibility."""
        raise NotImplementedError

    async def _start_heartbeat(self):
        """Continuously sends heartbeat messages while the agent is running."""

        async def heartbeat():
            while self.running:
                msg = Message(
                    message_type="heartbeat",
                    timestamp=datetime.now(timezone.utc),  # use timezone-aware UTC
                    data={},
                    destination_agent_id=self.agent_id,
                    source_agent_id=self.agent_id,
                )
                await self.message_bus.send_message(msg)
                # Adjust sleep as needed for your real environment;
                # shorter sleeps help tests see a heartbeat quickly.
                await asyncio.sleep(0.05)

        self._heartbeat_task = asyncio.create_task(heartbeat())


class BaseTestAgent(BaseAgent):
    """Base test agent implementation with heartbeat."""

    def __init__(self, agent_id: str, message_bus: MessageBus):
        super().__init__(agent_id, message_bus)
        self._task_queue = None
        self._task_processor = None

    async def start(self):
        """Start the agent with proper event loop binding."""
        if not self.running:
            self.running = True
            self._task_queue = asyncio.Queue()
            self._task_processor = asyncio.create_task(self._process_tasks())
            await self._start_heartbeat()

    async def _process_tasks(self):
        """Process queued tasks."""
        try:
            while self.running:
                task = await self._task_queue.get()
                try:
                    await task
                except Exception as e:
                    self.logger.error(f"Error processing task: {e}")
                finally:
                    self._task_queue.task_done()
        except asyncio.CancelledError:
            pass

    async def stop(self):
        """Stop the agent and clean up resources."""
        if self.running:
            self.running = False

            # Cancel the heartbeat, if it exists
            if self._heartbeat_task:
                self._heartbeat_task.cancel()
                try:
                    await self._heartbeat_task
                except asyncio.CancelledError:
                    pass
                self._heartbeat_task = None

            # Cancel the task processor
            if self._task_processor:
                self._task_processor.cancel()
                try:
                    await self._task_processor
                except asyncio.CancelledError:
                    pass
                self._task_processor = None

            # Make sure we process all tasks in the queue
            if self._task_queue:
                await self._task_queue.join()
                self._task_queue = None


#
# Actual Agent class under test
#

class TestAgent(BaseTestAgent):
    """
    We prevent Pytest from thinking this is a test class
    by setting __test__ to False.
    """
    __test__ = False

    # Provide any further agent-specific logic here if needed.
    pass


#
# Pytest fixtures
#

@pytest_asyncio.fixture
async def test_agent():
    """Fixture to create and clean up a test agent."""
    message_bus = MockMessageBus()
    await message_bus.start()

    agent = TestAgent(agent_id="test_agent", message_bus=message_bus)
    await agent.setup()
    yield agent

    # Cleanup
    await agent.cleanup()
    if agent.running:
        await agent.stop()

    await message_bus.stop()


#
# Actual Test
#

@pytest.mark.asyncio
async def test_heartbeat(test_agent: TestAgent):
    """Test agent heartbeat functionality."""
    await test_agent.start()

    # Sleep briefly so the heartbeat can send at least one message
    await asyncio.sleep(0.1)

    # Check that a heartbeat message was recorded
    messages = await test_agent.message_bus.get_messages(test_agent.agent_id)
    assert any(msg.message_type == "heartbeat" for msg in messages), \
        "Expected at least one heartbeat message."

    # Cleanup
    await test_agent.stop()
>>>>>>> theirs
