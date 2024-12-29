# tests/integration/services/test_hunter.py

# Standard library imports
import asyncio

# Third-party imports
import pytest
import pytest_asyncio
import aiohttp
from unittest.mock import AsyncMock, MagicMock

# Local imports
from src.integrations.hunter import (
    HunterClient,
    HunterError,
    HunterNotFoundError,
    HunterInvalidError
)

# Configure Windows event loop policy (if necessary)
if asyncio.get_event_loop_policy().__class__.__name__ == 'WindowsProactorEventLoopPolicy':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())



# Fixture to mock aiohttp.ClientSession
@pytest_asyncio.fixture
async def mock_session():
    """Provide a mock aiohttp ClientSession."""
    session = AsyncMock(spec=aiohttp.ClientSession)
    session.closed = False
    session.close = AsyncMock()
    yield session
    if not session.closed:
        await session.close()

# Fixture to create a HunterClient instance with the mocked session
@pytest_asyncio.fixture
async def hunter_client(mock_session):
    """Provide a HunterClient instance with a mocked session."""
    client = HunterClient("test_key")
    client._session = mock_session
    yield client
    if client._session and not client._session.closed:
        await client.close()

# Test class containing all test methods
class TestHunterClient:
    @pytest.mark.asyncio
    async def test_domain_search_success(self, hunter_client, mock_session):
        """Test successful domain search."""
        test_data = {
            "data": {
                "domain": "test.com",
                "emails": [{"value": "test@test.com", "type": "personal"}]
            }
        }

        mock_response = MagicMock(spec=aiohttp.ClientResponse)
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value=test_data)
        mock_session.request = AsyncMock(return_value=mock_response)

        result = await hunter_client.domain_search("test.com")
        assert result == test_data

    @pytest.mark.asyncio
    async def test_domain_search_not_found(self, hunter_client, mock_session):
        """Test domain search with no results."""
        mock_response = MagicMock(spec=aiohttp.ClientResponse)
        mock_response.status = 404
        mock_session.request = AsyncMock(return_value=mock_response)

        with pytest.raises(HunterNotFoundError, match="No email patterns found for domain: test.com"):
            await hunter_client.domain_search("test.com")

    @pytest.mark.asyncio
    async def test_email_finder_success(self, hunter_client, mock_session):
        """Test successful email finder."""
        test_data = {
            "data": {
                "email": "john.doe@test.com",
                "score": 90
            }
        }

        mock_response = MagicMock(spec=aiohttp.ClientResponse)
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value=test_data)
        mock_session.request = AsyncMock(return_value=mock_response)

        result = await hunter_client.email_finder("test.com", "John", "Doe")
        assert result == test_data

    @pytest.mark.asyncio
    async def test_email_finder_invalid_input(self, hunter_client, mock_session):
        """Test email finder with invalid input."""
        mock_response = MagicMock(spec=aiohttp.ClientResponse)
        mock_response.status = 400
        mock_session.request = AsyncMock(return_value=mock_response)

        with pytest.raises(HunterInvalidError, match="Invalid input parameters"):
            await hunter_client.email_finder("", "John", "Doe")

    @pytest.mark.asyncio
    async def test_email_verifier_success(self, hunter_client, mock_session):
        """Test successful email verification."""
        test_data = {
            "data": {
                "status": "valid",
                "score": 95,
                "email": "test@test.com"
            }
        }

        mock_response = MagicMock(spec=aiohttp.ClientResponse)
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value=test_data)
        mock_session.request = AsyncMock(return_value=mock_response)

        result = await hunter_client.email_verifier("test@test.com")
        assert result == test_data

    @pytest.mark.asyncio
    async def test_rate_limit_handling(self, hunter_client, mock_session):
        """Test rate limit error handling."""
        mock_response = MagicMock(spec=aiohttp.ClientResponse)
        mock_response.status = 429
        mock_response.headers = {"Retry-After": "60"}
        mock_session.request = AsyncMock(return_value=mock_response)

        with pytest.raises(HunterError) as exc_info:
            await hunter_client.domain_search("test.com")
        assert str(exc_info.value) == "Rate limit exceeded. Retry after 60 seconds"
        assert exc_info.value.status_code == 429

    @pytest.mark.asyncio
    async def test_server_error_retry(self, hunter_client, mock_session):
        """Test retry behavior on server error."""
        error_response = MagicMock(spec=aiohttp.ClientResponse)
        error_response.status = 500

        success_response = MagicMock(spec=aiohttp.ClientResponse)
        success_response.status = 200
        success_response.json = AsyncMock(return_value={"data": {"result": "success"}})

        responses = [error_response, success_response]
        mock_session.request = AsyncMock(side_effect=lambda *args, **kwargs: responses.pop(0))

        result = await hunter_client.domain_search("test.com")
        assert result == {"data": {"result": "success"}}
