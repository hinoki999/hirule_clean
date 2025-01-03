<<<<<<< ours
import pytest
import pytest_asyncio
import asyncio
import logging
import platform
from src.agents.protocol.coap_agent import CoAPAgent
from src.communication.messages import Message

# Setup basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Use pytest_asyncio.fixture instead of pytest.fixture for async fixtures
@pytest_asyncio.fixture(scope="function", autouse=True)
async def event_loop_policy():
    #"""Set event loop policy for Windows.#"""
    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

@pytest_asyncio.fixture
async def coap_agent():
    #"""Create and cleanup a CoAP agent for testing.#"""
    # Setup
    agent = CoAPAgent(agent_id="test_coap_agent", coap_port=5684)
    try:
        await agent.setup()
        # Return the agent itself, not a generator
        return agent
    finally:
        # Cleanup will happen after the test
        try:
            await agent.cleanup()
        except Exception as e:
            logging.error(f"Error during cleanup: {e}")

@pytest.mark.asyncio
class TestCoAPAgent:

    async def test_initialization(self, coap_agent):
        #"""Test agent initialization#"""
        assert isinstance(coap_agent, CoAPAgent)
        assert coap_agent.agent_id == "test_coap_agent"
        assert coap_agent.coap_port == 5684
        assert coap_agent.protocol == "CoAP"

    async def test_process_request(self, coap_agent):
        #"""Test basic request processing#"""
        request = {
            "method": "GET",
            "uri": "coap://example.com/test",
            "payload": "test_data"
        }

        response = await coap_agent.process_request(request)
        assert response["status"] == "success"
        assert response["protocol"] == "CoAP"
        assert response["agent_id"] == coap_agent.agent_id

    async def test_error_handling(self, coap_agent):
        #"""Test invalid request handling#"""
        invalid_request = {
            "method": "INVALID",
            "uri": None
        }

        response = await coap_agent.process_request(invalid_request)
        assert response["status"] == "error"


||||||| base
=======
import pytest
import pytest_asyncio
import asyncio
import logging
import platform
from src.agents.protocol.coap_agent import CoAPAgent
from src.communication.messages import Message

# Setup basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Use pytest_asyncio.fixture instead of pytest.fixture for async fixtures
@pytest_asyncio.fixture(scope="function", autouse=True)
async def event_loop_policy():
    """Set event loop policy for Windows."""
    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

@pytest_asyncio.fixture
async def coap_agent():
    """Create and cleanup a CoAP agent for testing."""
    # Setup
    agent = CoAPAgent(agent_id="test_coap_agent", coap_port=5684)
    try:
        await agent.setup()
        # Return the agent itself, not a generator
        return agent
    finally:
        # Cleanup will happen after the test
        try:
            await agent.cleanup()
        except Exception as e:
            logging.error(f"Error during cleanup: {e}")

@pytest.mark.asyncio
class TestCoAPAgent:
    
    async def test_initialization(self, coap_agent):
        """Test agent initialization"""
        assert isinstance(coap_agent, CoAPAgent)
        assert coap_agent.agent_id == "test_coap_agent"
        assert coap_agent.coap_port == 5684
        assert coap_agent.protocol == "CoAP"

    async def test_process_request(self, coap_agent):
        """Test basic request processing"""
        request = {
            "method": "GET",
            "uri": "coap://example.com/test",
            "payload": "test_data"
        }
        
        response = await coap_agent.process_request(request)
        assert response["status"] == "success"
        assert response["protocol"] == "CoAP"
        assert response["agent_id"] == coap_agent.agent_id

    async def test_error_handling(self, coap_agent):
        """Test invalid request handling"""
        invalid_request = {
            "method": "INVALID",
            "uri": None
        }
        
        response = await coap_agent.process_request(invalid_request)
        assert response["status"] == "error"
>>>>>>> theirs
