import asyncio
from datetime import datetime, timedelta
from collections import deque

class RateLimiter:
    def __init__(self, calls_per_minute):
        self.calls_per_minute = calls_per_minute
        self.window = timedelta(minutes=1)
        self.calls = deque()

    async def acquire(self) -> bool:
        now = datetime.now()

        # Remove expired timestamps
        while self.calls and now - self.calls[0] > self.window:
            self.calls.popleft()

        # Check if we can make another call
        if len(self.calls) < self.calls_per_minute:
            self.calls.append(now)
            return True

        return False


