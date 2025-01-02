import asyncio
import logging
from typing import Any

class BaseAgent:
    def __init__(self, **kwargs):
        self.logger = logging.getLogger(self.__class__.__name__)

    async def setup(self):
        """Base setup method"""
        pass

    async def cleanup(self):
        """Base cleanup method"""
        pass

    async def process_message(self, message: Any):
        """Base message processing method"""
        pass
