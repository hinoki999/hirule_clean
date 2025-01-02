import pytest
import pytest_asyncio
import asyncio
import platform
import socket
import json
from aiohttp import web
from datetime import datetime, timedelta
from src.message_system.core.message_bus import MessageBus, MessageType
from src.message_system.integration.market_data import MarketDataIntegration

# Set up event loop policy for Windows
if platform.system() == "Windows":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Mock data for testing
MOCK_KLINES_DATA = [
    [
        int(datetime.now().timestamp() * 1000),  # Open time
        "1800.50",  # Open
        "1805.20",  # High
        "1798.30",  # Low
        "1803.40",  # Close
        "156.78",   # Volume
        int((datetime.now() + timedelta(minutes=1)).timestamp() * 1000),  # Close time
        "282518.25", # Quote asset volume
        150,        # Number of trades
        "78.39",    # Taker buy base asset volume
        "141259.13",# Taker buy quote asset volume
        "0"         # Ignore
    ]
]

class MockServer:
    def __init__(self):
        self.app = web.Application()
        self.app.router.add_get('/api/v3/time', self.handle_time)
        self.app.router.add_get('/api/v3/klines', self.handle_klines)
        self.runner = None

    async def handle_time(self, request):
        return web.json_response({"serverTime": int(datetime.now().timestamp() * 1000)})

    async def handle_klines(self, request):
        return web.json_response(MOCK_KLINES_DATA)

    async def start(self):
        self.runner = web.AppRunner(self.app)
        await self.runner.setup()
        self.site = web.TCPSite(self.runner, 'localhost', 8080)
        await self.site.start()
        return "http://localhost:8080/api/v3"

    async def cleanup(self):
        if self.runner:
            await self.runner.cleanup()

@pytest_asyncio.fixture(scope="function")
async def mock_server():
    """Start and stop mock server"""
    server = MockServer()
    base_url = await server.start()
    print(f"Mock server started at {base_url}")
    yield base_url
    await server.cleanup()
    print("Mock server stopped")

@pytest.mark.asyncio
async def test_market_data_integration(mock_server):
    """Test market data integration using mock server"""
    message_bus = MessageBus()
    print(f"Using mock server URL: {mock_server}")
    market_data = MarketDataIntegration(message_bus, base_url=mock_server)
    
    try:
        print("\nTesting historical data fetching...")
        historical_data = await market_data.get_historical_data("ETHUSDT")
        
        print(f"Got historical data length: {len(historical_data)}")
        if len(historical_data) > 0:
            print(f"First candle: {historical_data[0]}")
        
        assert len(historical_data) > 0, "No historical data received"
        first_candle = historical_data[0]
        print(f"First candle keys: {first_candle.keys()}")
        assert all(key in first_candle for key in ["timestamp", "open", "close", "high", "low", "volume"]), \
            f"Missing keys in data. Got keys: {first_candle.keys()}"
            
    except Exception as e:
        import traceback
        print(f"Test failed with error: {str(e)}")
        print(traceback.format_exc())
        pytest.fail(f"Test failed with error: {str(e)}")
