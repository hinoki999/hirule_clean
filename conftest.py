import pytest
import asyncio
from unittest.mock import AsyncMock
from src.agents.trading.base_trading_agent import BaseTradingAgent
from src.config.trading_config import TradingConfig

@pytest.fixture(scope="session", autouse=True)
def configure_logging():
    pass

@pytest.fixture
async def trading_agent():
    config = TradingConfig()
    agent = BaseTradingAgent(config)
    agent.send_message = AsyncMock()
    await agent.setup()
    yield agent
    await agent.cleanup()
