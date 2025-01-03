import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock
from src.enrichment.company_enrichment import CompanyEnrichmentService, EnrichmentResult
from src.integrations.clearbit import ClearbitNotFoundError
from src.integrations.hunter import HunterNotFoundError

@pytest_asyncio.fixture
async def enrichment_service(mock_session):
    service = CompanyEnrichmentService("clearbit_test_key", "hunter_test_key")
    service.clearbit_client._session = mock_session
    service.hunter_client._session = mock_session
    return service

class TestCompanyEnrichmentService:
    @pytest.mark.asyncio
    async def test_successful_enrichment(self, enrichment_service, mock_session):
        #"""Test successful enrichment with both services#"""
        # Mock Clearbit response
        clearbit_data = {
            "name": "Test Company",
            "domain": "test.com",
            "metrics": {"employees": 100}
        }

        # Mock Hunter response
        hunter_data = {
            "data": {
                "patterns": [{"pattern": "{first}{last}@test.com"}],
                "emails": [
                    {"value": "john.doe@test.com", "type": "personal"}
                ]
            }
        }

        # Setup mock responses
        mock_clearbit_response = MagicMock()
        mock_clearbit_response.status = 200
        mock_clearbit_response.json = AsyncMock(return_value=clearbit_data)

        mock_hunter_response = MagicMock()
        mock_hunter_response.status = 200
        mock_hunter_response.json = AsyncMock(return_value=hunter_data)

        # Setup request mock to return different responses for each service
        async def mock_request(*args, **kwargs):
            if "clearbit" in args[1]:
                return mock_clearbit_response
            return mock_hunter_response

        mock_session.request = AsyncMock(side_effect=mock_request)

        # Test the service
        async with enrichment_service as service:
            result = await service.enrich_company("test.com")

        assert result.company_info == clearbit_data
        assert result.email_patterns == hunter_data["data"]["patterns"]
        assert result.key_contacts == hunter_data["data"]["emails"]
        assert result.error is None

    @pytest.mark.asyncio
    async def test_clearbit_not_found(self, enrichment_service, mock_session):
        #"""Test behavior when Clearbit doesn't find the company#"""
        mock_response = MagicMock()
        mock_response.status = 404
        mock_session.request = AsyncMock(return_value=mock_response)

        async with enrichment_service as service:
            result = await service.enrich_company("unknown.com")

        assert result.company_info is None
        assert result.error == "Company not found in Clearbit: unknown.com"

    @pytest.mark.asyncio
    async def test_hunter_not_found(self, enrichment_service, mock_session):
        #"""Test behavior when Hunter doesn't find email patterns#"""
        # Mock successful Clearbit response
        clearbit_data = {"name": "Test Company"}
        mock_clearbit_response = MagicMock()
        mock_clearbit_response.status = 200
        mock_clearbit_response.json = AsyncMock(return_value=clearbit_data)

        # Mock Hunter 404 response
        mock_hunter_response = MagicMock()
        mock_hunter_response.status = 404

        async def mock_request(*args, **kwargs):
            if "clearbit" in args[1]:
                return mock_clearbit_response
            return mock_hunter_response

        mock_session.request = AsyncMock(side_effect=mock_request)

        async with enrichment_service as service:
            result = await service.enrich_company("test.com")

        assert result.company_info == clearbit_data
        assert result.email_patterns is None
        assert result.key_contacts is None
        assert result.error is None


