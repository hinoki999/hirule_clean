import pytest
import pytest_asyncio
import uuid
from datetime import datetime
from src.agents.base import BaseAgent
from src.agents.lead_enrichment_agent import LeadEnrichmentAgent
from src.core.messaging import Message

@pytest_asyncio.fixture
async def enrichment_agent():
    agent = LeadEnrichmentAgent()
    await agent.setup()
    yield agent
    await agent.cleanup()

@pytest.fixture
def sample_lead_data():
    return {
        "company_name": "Test Company",
        "contact_email": "test@company.com",
        "website": "https://testcompany.com"
    }

@pytest.mark.asyncio
async def test_metrics_collection(enrichment_agent, sample_lead_data):
    """Test metrics collection during lead processing"""
    # Process a valid lead
    enriched_data = await enrichment_agent.enrich_lead(sample_lead_data)
    assert enriched_data["enrichment_status"] == "completed"
    
    # Process an invalid lead
    invalid_data = {"website": "https://test.com"}
    invalid_enriched = await enrichment_agent.enrich_lead(invalid_data)
    assert invalid_enriched["enrichment_status"] == "failed"
    
    # Get metrics
    metrics_data = enrichment_agent.get_metrics()
    
    # Verify metrics structure
    assert "metrics" in metrics_data
    assert "error_distribution" in metrics_data
    
    # Check metric values
    metrics = metrics_data["metrics"]
    assert metrics["total_processed"] == 2
    assert metrics["success_rate"] == 50.0
    assert metrics["error_count"] == 1
    assert "validation_error" in metrics_data["error_distribution"]

@pytest.mark.asyncio
async def test_metrics_message_handling(enrichment_agent):
    """Test metrics retrieval via message"""
    message = Message(
        id=str(uuid.uuid4()),
        sender="test-sender",
        recipient=enrichment_agent.agent_id,
        message_type="GET_METRICS",
        payload={},
        timestamp=datetime.now().timestamp(),
        priority=0,
        reply_to=None
    )
    
    response = await enrichment_agent.process_message(message)
    assert response is not None
    assert "metrics" in response
    assert "error_distribution" in response

# Keep existing tests
@pytest.mark.asyncio
async def test_agent_initialization():
    """Test basic agent initialization"""
    agent = LeadEnrichmentAgent()
    assert agent is not None
    assert isinstance(agent, BaseAgent)
    assert hasattr(agent, '_processed_leads')
    assert isinstance(agent._processed_leads, dict)
    assert hasattr(agent, 'validator')
    assert hasattr(agent, 'metrics')

@pytest.mark.asyncio
async def test_basic_lead_enrichment(enrichment_agent, sample_lead_data):
    """Test basic lead enrichment functionality"""
    enriched_data = await enrichment_agent.enrich_lead(sample_lead_data)
    
    # Check basic structure
    assert "lead_id" in enriched_data
    assert "enrichment_status" in enriched_data
    assert "processed_at" in enriched_data
    assert "validation_details" in enriched_data
    assert enriched_data["enrichment_status"] == "completed"
    
    # Check validation details
    validation_details = enriched_data["validation_details"]
    assert validation_details["validation_status"] == "valid"
    assert isinstance(validation_details["errors"], list)
    assert isinstance(validation_details["warnings"], list)
    assert len(validation_details["errors"]) == 0
    
    # Verify data retention
    assert enriched_data["lead_id"] in enrichment_agent._processed_leads

@pytest.mark.asyncio
async def test_invalid_lead_data(enrichment_agent):
    """Test handling of invalid lead data"""
    invalid_data = {"website": "https://test.com"}  # Missing company_name
    enriched_data = await enrichment_agent.enrich_lead(invalid_data)
    
    assert enriched_data["enrichment_status"] == "failed"
    assert "validation_details" in enriched_data
    assert enriched_data["validation_details"]["validation_status"] == "invalid"
    assert len(enriched_data["validation_details"]["errors"]) > 0

@pytest.mark.asyncio
async def test_lead_with_warnings(enrichment_agent):
    """Test handling of lead data with warnings"""
    warning_data = {
        "company_name": "TEST COMPANY ALL CAPS",
        "contact_email": "test@company.com",
        "website": "https://testcompany.com"
    }
    enriched_data = await enrichment_agent.enrich_lead(warning_data)
    
    assert enriched_data["enrichment_status"] == "completed"
    assert "validation_details" in enriched_data
    assert enriched_data["validation_details"]["validation_status"] == "valid"
    assert len(enriched_data["validation_details"]["warnings"]) > 0

    # Check metrics for warning capture
    metrics_data = enrichment_agent.get_metrics()
    assert metrics_data["metrics"]["warning_rate"] > 0

@pytest.mark.asyncio
async def test_message_handling(enrichment_agent, sample_lead_data):
    """Test message-based enrichment requests"""
    message = Message(
        id=str(uuid.uuid4()),
        sender="test-sender",
        recipient=enrichment_agent.agent_id,
        message_type="ENRICH_LEAD",
        payload=sample_lead_data,
        timestamp=datetime.now().timestamp(),
        priority=0,
        reply_to=None
    )
    
    response = await enrichment_agent.process_message(message)
    assert response is not None
    assert "enrichment_status" in response
    assert response["enrichment_status"] == "completed"
import pytest
import pytest_asyncio
import uuid
from datetime import datetime
from src.agents.base import BaseAgent
from src.agents.lead_enrichment_agent import LeadEnrichmentAgent
from src.core.messaging import Message

@pytest.mark.asyncio
async def test_external_enrichment():
    """Test external enrichment functionality"""
    agent = LeadEnrichmentAgent()
    await agent.setup()
    
    test_data = {
        "company_name": "Test Company",
        "contact_email": "test@testcompany.com",
        "website": "https://testcompany.com"
    }
    
    enriched_data = await agent.enrich_lead(test_data)
    
    # Check enrichment structure
    assert "enrichment_status" in enriched_data
    assert enriched_data["enrichment_status"] in ["completed", "partial"]
    assert "enrichment_data" in enriched_data
    
    # Check enrichment results
    enrichment_data = enriched_data["enrichment_data"]
    assert "enrichment_results" in enrichment_data
    assert "enrichment_summary" in enrichment_data
    
    # Verify summary statistics
    summary = enrichment_data["enrichment_summary"]
    assert "total_enrichments" in summary
    assert "successful_enrichments" in summary
    assert summary["total_enrichments"] > 0
    
    await agent.cleanup()
