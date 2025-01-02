import pytest
import pytest_asyncio
import aiohttp
import asyncio
from unittest.mock import AsyncMock, MagicMock
from src.integrations.base import (
    BaseAPIClient,
    APIConfig,
    RateLimitError,
    AuthenticationError,
    ServerError
)

@pytest.fixture
def api_config():
    return APIConfig(
        api_key="test_key",
        base_url="https://api.test.com",
        timeout=5,
        max_retries=2,
        rate_limit=10
    )

@pytest_asyncio.fixture
async def mock_session():
    session = AsyncMock(spec=aiohttp.ClientSession)
    session.closed = False
    session.close = AsyncMock()
    return session

@pytest_asyncio.fixture(autouse=True)
async def cleanup_sessions():
    yield
    await asyncio.sleep(0)  # Allow any pending tasks to complete

# Rest of TestBaseAPIClient remains the same...


