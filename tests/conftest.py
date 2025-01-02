<<<<<<< ours
"""
conftest.py -- Shared pytest fixtures for async tests using aiohttp
"""

import pytest
import pytest_asyncio
import aiohttp
import asyncio
from unittest.mock import AsyncMock

@pytest_asyncio.fixture
async def mock_session():
    """
    Creates a mock aiohttp.ClientSession for testing.

    Usage in a test:
        async def test_example(mock_session):
            mock_session.get.return_value = AsyncMock(...)  # or any mock
            ...
    """
    session = AsyncMock(spec=aiohttp.ClientSession)
    # By default, pretend we haven't closed the session yet:
    session.closed = False
    session.close = AsyncMock()  # So you can assert session.close.called
    return session

@pytest_asyncio.fixture(autouse=True)
async def cleanup_sessions():
    """
    Autouse fixture that runs after each test to allow any pending async tasks
    to complete, preventing leftover tasks from polluting subsequent tests.
    """
    yield
    # After the test finishes, give the event loop a chance to clean up tasks:
    await asyncio.sleep(0)


||||||| base
=======
# tests/conftest.py
import pytest
import asyncio
import logging

# Configure logging for tests
def pytest_configure(config):
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Set asyncio default loop scope
    config.option.asyncio_default_fixture_loop_scope = "function"

@pytest.fixture(scope="session", autouse=True)
def setup_test_env():
    """Setup test environment"""
    # Add any global test setup here
    yield
    # Add any global cleanup here
>>>>>>> theirs
