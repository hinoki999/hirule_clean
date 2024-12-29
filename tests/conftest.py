import pytest
import pytest_asyncio
import aiohttp
import asyncio
from unittest.mock import AsyncMock

@pytest_asyncio.fixture
async def mock_session():
    """Creates a mock aiohttp ClientSession for testing"""
    session = AsyncMock(spec=aiohttp.ClientSession)
    session.closed = False
    session.close = AsyncMock()
    return session

@pytest_asyncio.fixture(autouse=True)
async def cleanup_sessions():
    """Cleanup any pending tasks after tests"""
    yield
    await asyncio.sleep(0)  # Allow any pending tasks to complete
