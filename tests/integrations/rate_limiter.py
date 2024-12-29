# src/integrations/rate_limiter.py

import asyncio
import time

class RateLimiter:
    """Simple rate limiter using asyncio locks and time stamps."""

    def __init__(self, rate_limit: int):
        """
        Initializes the RateLimiter.

        Args:
            rate_limit (int): Number of allowed requests per second.
        """
        self.rate_limit = rate_limit
        self.lock = asyncio.Lock()
        self.requests = []
        self.time_window = 1  # seconds

    async def acquire(self) -> bool:
        """Acquire permission to make a request based on the rate limit."""
        async with self.lock:
            current_time = time.time()
            # Remove requests that are outside the current time window
            self.requests = [req for req in self.requests if req > current_time - self.time_window]

            if len(self.requests) < self.rate_limit:
                self.requests.append(current_time)
                return True
            else:
                return False
