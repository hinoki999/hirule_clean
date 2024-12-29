import pytest
import pytest_asyncio
import aiohttp
import asyncio  # Added this import
from unittest.mock import AsyncMock, MagicMock
from src.integrations.clearbit import (
    ClearbitClient,
    ClearbitError,
    ClearbitNotFoundError
)
from src.integrations.base import RateLimitError  # Added this import

@pytest_asyncio.fixture
async def mock_session():
    session = AsyncMock(spec=aiohttp.ClientSession)
    session.closed = False
    session.close = AsyncMock()
    return session

@pytest_asyncio.fixture
async def clearbit_client(mock_session):
    client = ClearbitClient("test_key")
    client._session = mock_session
    yield client
    await client.close()

@pytest_asyncio.fixture(autouse=True)
async def cleanup_sessions():
    yield
    await asyncio.sleep(0)

class TestClearbitClient:
    @pytest.mark.asyncio
    async def test_enrich_company_success(self, clearbit_client, mock_session):
        """Test successful company enrichment"""
        test_data = {
            "name": "Test Company",
            "domain": "test.com",
            "metrics": {"employees": 100},
            "industry": "Technology"
        }

        mock_response = MagicMock(spec=aiohttp.ClientResponse)
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value=test_data)
        mock_session.request = AsyncMock(return_value=mock_response)

        result = await clearbit_client.enrich_company("test.com")
        assert result == test_data

    @pytest.mark.asyncio
    async def test_enrich_company_not_found(self, clearbit_client, mock_session):
        """Test company enrichment when company is not found"""
        mock_response = MagicMock(spec=aiohttp.ClientResponse)
        mock_response.status = 404
        mock_session.request = AsyncMock(return_value=mock_response)

        with pytest.raises(ClearbitNotFoundError, match="No company data found for domain: test.com"):
            await clearbit_client.enrich_company("test.com")

    @pytest.mark.asyncio
    async def test_enrich_company_quota_exceeded(self, clearbit_client, mock_session):
        """Test handling of exceeded query quota"""
        mock_response = MagicMock(spec=aiohttp.ClientResponse)
        mock_response.status = 402
        mock_session.request = AsyncMock(return_value=mock_response)

        with pytest.raises(ClearbitError, match="Query limit exceeded or payment required"):
            await clearbit_client.enrich_company("test.com")

    @pytest.mark.asyncio
    async def test_enrich_person_success(self, clearbit_client, mock_session):
        """Test successful person enrichment"""
        test_data = {
            "name": {
                "givenName": "John",
                "familyName": "Doe"
            },
            "email": "john@test.com",
            "employment": {
                "title": "Software Engineer",
                "company": "Test Company"
            }
        }

        mock_response = MagicMock(spec=aiohttp.ClientResponse)
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value=test_data)
        mock_session.request = AsyncMock(return_value=mock_response)

        result = await clearbit_client.enrich_person("john@test.com")
        assert result == test_data

    @pytest.mark.asyncio
    async def test_enrich_person_not_found(self, clearbit_client, mock_session):
        """Test person enrichment when person is not found"""
        mock_response = MagicMock(spec=aiohttp.ClientResponse)
        mock_response.status = 404
        mock_session.request = AsyncMock(return_value=mock_response)

        with pytest.raises(ClearbitNotFoundError, match="No person data found for email: test@unknown.com"):
            await clearbit_client.enrich_person("test@unknown.com")

    @pytest.mark.asyncio
    async def test_validation_error(self, clearbit_client, mock_session):
        """Test handling of validation errors"""
        mock_response = MagicMock(spec=aiohttp.ClientResponse)
        mock_response.status = 422
        mock_session.request = AsyncMock(return_value=mock_response)

        with pytest.raises(ClearbitError, match="Validation failed - check input parameters"):
            await clearbit_client.enrich_person("invalid-email")

    @pytest.mark.asyncio
    async def test_server_error_retry(self, clearbit_client, mock_session):
        """Test retry behavior on server error"""
        error_response = MagicMock(spec=aiohttp.ClientResponse)
        error_response.status = 500

        success_response = MagicMock(spec=aiohttp.ClientResponse)
        success_response.status = 200
        success_response.json = AsyncMock(return_value={"success": True})

        responses = [error_response, success_response]
        mock_session.request = AsyncMock(side_effect=lambda *args, **kwargs: responses.pop(0))

        result = await clearbit_client.enrich_company("test.com")
        assert result == {"success": True}

    @pytest.mark.asyncio
    async def test_rate_limit_handling(self, clearbit_client, mock_session):
        """Test rate limit handling"""
        mock_response = MagicMock(spec=aiohttp.ClientResponse)
        mock_response.status = 429
        mock_session.request = AsyncMock(return_value=mock_response)

        with pytest.raises(RateLimitError) as exc_info:  # Changed from ClearbitError to RateLimitError
            await clearbit_client.enrich_company("test.com")
        assert exc_info.value.status_code == 429