import pytest
import asyncio
from datetime import datetime
from src.integrations.base import RateLimiter

class TestRateLimiter:
    @pytest.mark.asyncio
    async def test_rate_limiting(self):
        """Test rate limiter behavior with a small waiting period"""
        limiter = RateLimiter(calls_per_minute=2)
        
        # First two calls should succeed immediately
        assert await limiter.acquire() is True
        assert await limiter.acquire() is True
        
        # Third call should fail
        assert await limiter.acquire() is False
        
        # Wait a short period and try again
        await asyncio.sleep(0.1)
        assert await limiter.acquire() is False
