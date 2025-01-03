"""
Test suite for BaseTradingAgent and CCXT integration
"""
import pytest
import asyncio
from decimal import Decimal
from unittest.mock import MagicMock, patch
from src.agents.trading.trading_agent import BaseTradingAgent
from src.agents.trading.messages import MarketData, Order, OrderStatus
from src.config.trading_config import TradingConfig

class TestBaseTradingAgent:
    @pytest.fixture
    def config(self):
        """Create test configuration"""
        return TradingConfig(
            exchange="binance",
            symbols=["BTC/USDT"],
            api_key="test_key",
            api_secret="test_secret"
        )

    @pytest.fixture
    def trading_agent(self, config):
        """Create trading agent instance with mocked dependencies"""
        agent = BaseTradingAgent(config=config)
        return agent

    @pytest.mark.asyncio
    async def test_initialization(self, trading_agent):
        """Test agent initialization and state setup"""
        await trading_agent.setup()
        
        # Verify initial state
        assert isinstance(trading_agent.positions, dict)
        assert isinstance(trading_agent.orders, dict)
        assert isinstance(trading_agent.balances, dict)
        assert isinstance(trading_agent.latest_prices, dict)

    @pytest.mark.asyncio 
    async def test_market_data_handling(self, trading_agent):
        """Test market data message processing"""
        test_data = {
            "symbol": "BTC/USDT",
            "last_price": "50000",
            "volume": "100",
            "timestamp": "2025-01-03T10:00:00"
        }
        
        message = {
            "type": "MARKET_DATA",
            "payload": test_data
        }

        await trading_agent._handle_market_data(message)
        assert "BTC/USDT" in trading_agent.latest_prices

    @pytest.mark.asyncio
    async def test_order_handling(self, trading_agent):
        """Test order message processing"""
        test_order = {
            "order_id": "test1",
            "symbol": "BTC/USDT",
            "side": "BUY",
            "quantity": "1.0",
            "price": "50000",
            "status": "FILLED"
        }

        message = {
            "type": "ORDER_FILL",
            "payload": test_order
        }

        await trading_agent._handle_order_fill(message)
        assert "test1" in trading_agent.orders
        assert trading_agent.positions["BTC/USDT"] == Decimal("1.0")

    @pytest.mark.asyncio
    async def test_balance_updates(self, trading_agent):
        """Test balance update handling"""
        test_balances = {
            "BTC": "1.5",
            "USDT": "75000"
        }

        message = {
            "type": "BALANCE_UPDATE",
            "payload": test_balances
        }

        await trading_agent._handle_balance_update(message)
        assert trading_agent.balances["BTC"] == Decimal("1.5")
        assert trading_agent.balances["USDT"] == Decimal("75000")

    @pytest.mark.asyncio
    async def test_order_placement(self, trading_agent):
        """Test order placement functionality"""
        # Mock send_message method
        trading_agent.send_message = MagicMock()
        
        order = Order(
            order_id="test2",
            symbol="BTC/USDT",
            side="BUY",
            quantity=Decimal("1.0"),
            price=Decimal("50000")
        )

        await trading_agent.place_order(order)
        
        # Verify order was stored and message was sent
        assert "test2" in trading_agent.orders
        trading_agent.send_message.assert_called_once()
