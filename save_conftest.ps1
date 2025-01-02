# Create backup directory
$backupDir = ".\backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
New-Item -ItemType Directory -Path $backupDir -Force | Out-Null

# Create conftest.py
$conftestContent = @"
import pytest
import asyncio
import logging
from datetime import datetime
from decimal import Decimal
from typing import Dict, Optional

from src.agents.trading.market_regime import MarketRegimeDetector
from src.agents.trading.smart_trading_thresholds import SmartTradingThresholds

logger = logging.getLogger(__name__)

class TestTradingAgent:
    def __init__(self):
        self.latest_prices: Dict[str, float] = {}
        self.positions: Dict[str, Decimal] = {}
        self.trading_thresholds = SmartTradingThresholds()
        self.regime_detector = MarketRegimeDetector({})
        logger.debug("[TEST_AGENT] Initialized test trading agent")

    async def setup(self):
        """Set up the test agent."""
        logger.debug("[TEST_AGENT] Agent setup completed.")

    async def cleanup(self):
        """Clean up the test agent."""
        logger.debug("[TEST_AGENT] Agent cleanup completed.")

    async def process_message(self, message: Dict):
        """Process incoming messages."""
        msg_type = message.get("type")
        
        if msg_type == "MARKET_DATA":
            await self._handle_market_data(message)

    async def _handle_market_data(self, message):
        """Handle market data messages."""
        payload = message.get("payload", {})
        symbol = payload.get("symbol")
        last_price = payload.get("last_price")
        volume = payload.get("volume", 1000.0)
        cost = payload.get("cost", 0.001)
        timestamp = payload.get("timestamp", datetime.now())

        # Update latest prices
        self.latest_prices[symbol] = last_price

        # Update trading thresholds with new market data
        self.trading_thresholds.update_market_data(
            symbol=symbol,
            price=last_price,
            volume=volume,
            current_vol=volume,
            trade_cost=cost,
            timestamp=timestamp
        )

        logger.debug(f"[TEST_AGENT] Market data updated for symbol: {symbol}")

@pytest.fixture
async def trading_agent():
    """Fixture to provide a test trading agent."""
    agent = TestTradingAgent()
    await agent.setup()
    
    yield agent
    
    await agent.cleanup()
"@

# Save the conftest implementation
Set-Content ".\src\agents\trading\tests\conftest.py" $conftestContent

Write-Host "Updated conftest implementation"
Write-Host "Running tests..."

# Run the failing tests
pytest -v src/agents/trading/tests/test_market_regime.py::test_initial_state src/agents/trading/tests/test_smart_trading_thresholds.py::test_threshold_adjustment
