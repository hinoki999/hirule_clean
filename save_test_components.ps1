# Create needed directories
New-Item -ItemType Directory -Path ".\src\agents\trading\tests" -Force | Out-Null

# 1. Update conftest.py
$conftestContent = @"
import pytest
import asyncio
import logging
from datetime import datetime
from decimal import Decimal
from typing import Dict, Optional
from src.agents.trading.market_regime import MarketRegimeDetector
from src.agents.trading.smart_trading_thresholds import SmartTradingThresholds

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class TestTradingAgent:
    def __init__(self):
        """Initialize test trading agent with necessary components."""
        self.latest_prices: Dict[str, float] = {}
        self.positions: Dict[str, Decimal] = {}
        self.orders: Dict[str, Dict] = {}
        self.config = {
            'base_threshold': 0.001,
            'max_threshold': 0.01,
            'scaling_factor': 0.1
        }
        self.trading_thresholds = SmartTradingThresholds(self.config)
        self.regime_detector = self.trading_thresholds.regime_detector
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

        self.latest_prices[symbol] = last_price

        self.trading_thresholds.update_market_data(
            symbol=symbol,
            price=last_price,
            volume=volume,
            current_vol=volume,
            trade_cost=cost,
            timestamp=timestamp
        )

        logger.debug(f"[TEST_AGENT] Market data updated for symbol: {symbol}")

@pytest.fixture(scope="function")
async def trading_agent():
    """Fixture to provide a test trading agent."""
    agent = TestTradingAgent()
    await agent.setup()
    yield agent
    await agent.cleanup()
"@

# 2. Update market regime test
$marketRegimeTestContent = @"
import pytest
import asyncio
from datetime import datetime
from decimal import Decimal

@pytest.mark.asyncio
async def test_initial_state(trading_agent):
    """Test the initial state of the market regime detector."""
    symbol = "BTC/USD"
    
    # Provide 20 data points for regime detection
    for _ in range(20):
        await trading_agent.process_message({
            "type": "MARKET_DATA",
            "payload": {
                "symbol": symbol,
                "last_price": 50000.0,
                "volume": 1000.0,
                "cost": 0.001,
                "timestamp": datetime.now()
            }
        })
    
    # Allow processing time
    await asyncio.sleep(0.1)
    
    # Verify regime detection
    regime = trading_agent.regime_detector.detect_regime(symbol)
    assert regime is not None
    assert regime.volatility_regime == "normal"
    assert regime.liquidity_state == "good"
    
    # Verify confidence score
    confidence = trading_agent.regime_detector.get_regime_confidence(symbol)
    assert 0.0 <= confidence <= 1.0
"@

# 3. Update smart trading thresholds test
$thresholdsTestContent = @"
import pytest
import asyncio
from datetime import datetime
from decimal import Decimal

@pytest.mark.asyncio
async def test_threshold_adjustment(trading_agent):
    """Test threshold adjustment based on market regime."""
    symbol = "BTC/USD"
    trade_size = Decimal("1000.0")
    base_price = 50000.0
    
    # Initialize with required data points
    for _ in range(20):
        await trading_agent.process_message({
            "type": "MARKET_DATA",
            "payload": {
                "symbol": symbol,
                "last_price": base_price,
                "volume": 1000.0,
                "cost": 0.001,
                "timestamp": datetime.now()
            }
        })
    
    # Allow processing time
    await asyncio.sleep(0.1)
    
    # Calculate thresholds and sizing
    threshold, size_mult = trading_agent.trading_thresholds.calculate_thresholds_and_sizing(
        symbol, trade_size, base_price
    )
    
    # Verify calculated values
    assert 0.001 <= threshold <= 0.01
    assert 0.5 <= size_mult <= 1.0
    
    # Verify health status
    health = trading_agent.trading_thresholds.get_system_health(symbol)
    assert health['health_status'] == 'Good'
    assert not health['circuit_breaker_active']
    assert 0.0 <= health['regime_confidence'] <= 1.0
"@

# Save all test files
Set-Content ".\src\agents\trading\tests\conftest.py" $conftestContent
Set-Content ".\src\agents\trading\tests\test_market_regime.py" $marketRegimeTestContent
Set-Content ".\src\agents\trading\tests\test_smart_trading_thresholds.py" $thresholdsTestContent

Write-Host "Updated test implementations"
Write-Host "Running tests..."

# Run the tests
pytest -v src/agents/trading/tests/test_market_regime.py::test_initial_state src/agents/trading/tests/test_smart_trading_thresholds.py::test_threshold_adjustment
