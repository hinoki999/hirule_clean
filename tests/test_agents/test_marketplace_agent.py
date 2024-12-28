import pytest
import asyncio
from datetime import datetime
from src.agents.marketplace_agent import MarketplaceAgent
from src.core.messaging import Message

@pytest.fixture
async def marketplace_agent():
    agent = MarketplaceAgent()
    await agent.start()
    yield agent
    await agent.stop()

@pytest.fixture
def sample_agent_data():
    return {
        "agent_id": "test-agent-1",
        "name": "Test Agent",
        "category": "AI",
        "price": 100.0,
        "capabilities": ["text", "image"],
    }

@pytest.mark.asyncio
async def test_marketplace_agent_initialization():
    agent = MarketplaceAgent()
    assert agent is not None
    assert agent.agent_type == "marketplace"

@pytest.mark.asyncio
async def test_agent_registration(marketplace_agent, sample_agent_data):
    # Create registration message
    message = Message(
        id="test-msg-1",
        sender="test-sender",
        recipient=marketplace_agent.agent_id,
        message_type="REGISTER_AGENT",
        payload=sample_agent_data
    )
    
    # Test registration
    await marketplace_agent._handle_agent_registration(message)
    
    # Verify registration
    agents = await marketplace_agent.get_registered_agents()
    assert len(agents) == 1
    assert agents[0]["agent_id"] == sample_agent_data["agent_id"]

@pytest.mark.asyncio
async def test_agent_search(marketplace_agent, sample_agent_data):
    # Register an agent first
    reg_message = Message(
        id="reg-msg-1",
        sender="test-sender",
        recipient=marketplace_agent.agent_id,
        message_type="REGISTER_AGENT",
        payload=sample_agent_data
    )
    await marketplace_agent._handle_agent_registration(reg_message)
    
    # Search for agents
    search_message = Message(
        id="search-msg-1",
        sender="test-sender",
        recipient=marketplace_agent.agent_id,
        message_type="SEARCH_AGENTS",
        payload={"category": "AI"}
    )
    
    # Test search
    response = await marketplace_agent._handle_agent_search(search_message)
    assert response is not None
    assert len(response) >= 1
    assert response[0]["category"] == "AI"