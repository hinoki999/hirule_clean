import pytest
from unittest.mock import Mock, patch
import json
from src.integrations.hubspot.client import HubSpotClient
from src.integrations.hubspot.exceptions import RateLimitExceededError
from .mocks import (
    MockHubSpotClient,
    create_mock_company,
    MockApiException,
    MockUnauthorizedException
)

@pytest.fixture
def mock_company():
    return create_mock_company()

@pytest.fixture
def mock_api(mock_company):
    return MockHubSpotClient(results=[mock_company])

@pytest.fixture
def hubspot_client(mock_api):
    # Mock Redis client
    redis_mock = Mock()
    redis_mock.get.return_value = None

    # Patch the HubSpot client and exceptions
    with patch('src.integrations.hubspot.client.HubSpot', return_value=mock_api), 
         patch('hubspot.crm.companies.ApiException', MockApiException), 
         patch('hubspot.crm.companies.exceptions.UnauthorizedException', MockUnauthorizedException):
        client = HubSpotClient(
            access_token='test_token',
            redis_client=redis_mock
        )
        yield client

@pytest.mark.asyncio
async def test_get_company_data_basic(hubspot_client, mock_company):
    result = await hubspot_client.get_company_data('test.com')

    assert result is not None
    assert result['id'] == '123'
    assert result['properties']['name'] == 'Test Company'

@pytest.mark.asyncio
async def test_rate_limit_exceeded(hubspot_client):
    class MockRateLimiter:
        async def can_make_request(self):
            return False

    hubspot_client.rate_limiter = MockRateLimiter()

    with pytest.raises(RateLimitExceededError):
        await hubspot_client.get_company_data('test.com')

@pytest.mark.asyncio
async def test_cache_hit(hubspot_client):
    cached_data = {
        'id': '456',
        'properties': {
            'name': 'Cached Company',
            'domain': 'cached.com'
        }
    }

    hubspot_client.redis_client.get.return_value = json.dumps(cached_data).encode('utf-8')

    result = await hubspot_client.get_company_data('cached.com')

    assert result is not None
    assert result['id'] == '456'
    assert result['properties']['name'] == 'Cached Company'

    # Verify API wasn't called when using cache
    hubspot_client.client.crm.companies.search_api.do_search.assert_not_called()

@pytest.mark.asyncio
async def test_get_company_data_not_found(hubspot_client):
    # Replace the hubspot API with one that returns no results
    empty_api = MockHubSpotClient(results=[])

    with patch('src.integrations.hubspot.client.HubSpot', return_value=empty_api), 
         patch('hubspot.crm.companies.ApiException', MockApiException), 
         patch('hubspot.crm.companies.exceptions.UnauthorizedException', MockUnauthorizedException):
        client = HubSpotClient(
            access_token='test_token',
            redis_client=Mock(get=Mock(return_value=None))
        )

        result = await client.get_company_data('nonexistent.com')
        assert result is None


