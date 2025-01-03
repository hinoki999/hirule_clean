import pytest
import pytest_asyncio  # Add this import
import aiohttp
from aiohttp import ClientSession
import asyncio
from datetime import datetime
from unittest.mock import Mock, patch
from src.integrations.base import BaseAPIClient, APIConfig, RateLimiter
from src.integrations.clearbit import ClearbitClient  # Add imports
from src.integrations.hunter import HunterClient

@pytest.fixture
def api_config():
    return APIConfig(
        api_key="test_key",
        base_url="https://api.test.com",
        timeout=5,
        max_retries=2,
        rate_limit=10
    )

@pytest_asyncio.fixture  # Change to pytest_asyncio.fixture
def mock_response():
    class MockResponse:
        def __init__(self, status=200, json_data=None):
            self.status = status
            self._json_data = json_data or {}
            self.headers = {}

        async def json(self):
            return self._json_data

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            pass

        def raise_for_status(self):
            if self.status >= 400:
                raise aiohttp.ClientError(f"HTTP {self.status}")

    return MockResponse  # Return the class, not an instance

# Rest of the test code remains the same


