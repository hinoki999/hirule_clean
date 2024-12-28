import pytest
from datetime import datetime
from src.agents.lead_enrichment_agent import LeadEnrichmentAgent
from src.core.messaging import Message

@pytest.fixture
async def enrichment_agent():
    agent = LeadEnrichmentAgent()
    await agent.start()
    yield agent
    await agent.stop()

@pytest.fixture
def sample_lead_data():
    return {
        "company_name": "Test Company",
        "contact_email": "test@company.com",
        "website": "https://testcompany.com"
    }

@pytest.mark.asyncio
async def test_agent_initialization():
    """Test basic agent initialization"""
    agent = LeadEnrichmentAgent()
    assert agent is not None
    assert agent.agent_type == "lead_enrichment"
    assert hasattr(agent, '_processed_leads')
    assert isinstance(agent._processed_leads, dict)

@pytest.mark.asyncio
async def test_basic_lead_enrichment(enrichment_agent, sample_lead_data):
    """Test basic lead enrichment functionality"""
    enriched_data = await enrichment_agent.enrich_lead(sample_lead_data)
    
    # Check basic structure
    assert "lead_id" in enriched_data
    assert "enrichment_status" in enriched_data
    assert "processed_at" in enriched_data
    assert enriched_data["enrichment_status"] == "completed"
    
    # Verify data retention
    assert enriched_data["lead_id"] in enrichment_agent._processed_leads

@pytest.mark.asyncio
async def test_invalid_lead_data(enrichment_agent):
    """Test handling of invalid lead data"""
    invalid_data = {"website": "https://test.com"}  # Missing company_name
    enriched_data = await enrichment_agent.enrich_lead(invalid_data)
    
    assert enriched_data["enrichment_status"] == "failed"
    assert "error" in enriched_data

@pytest.mark.asyncio
async def test_message_handling(enrichment_agent, sample_lead_data):
    """Test message-based enrichment requests"""
    message = Message(
        id="test-msg-1",
        sender="test-sender",
        recipient=enrichment_agent.agent_id,
        message_type="ENRICH_LEAD",
        payload=sample_lead_data
    )
    
    response = await enrichment_agent.handle_message(message)
    assert response is not None
    assert "enrichment_status" in response
    assert response["enrichment_status"] == "completed"