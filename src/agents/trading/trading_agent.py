from src.agents.base import BaseAgent, AgentCapability
from src.agents.trading.messages import (
    TradingMessageTypes,
    MarketData,
    Order,
    OrderStatus
)
from decimal import Decimal
from typing import Dict
import asyncio
import logging
from datetime import datetime

from src.agents.trading.market_regime import MarketRegimeDetector
from src.agents.trading.smart_trading_thresholds import SmartTradingThresholds
from src.config.trading_config import TradingConfig

class BaseTradingAgent(BaseAgent):
    """
    Base class for trading agents that provides common trading functionality
    """

    def __init__(self, config: TradingConfig, **kwargs):
        super().__init__(**kwargs)
        self.capabilities.extend([
            AgentCapability.TRADING,
            AgentCapability.MARKET_DATA,
            AgentCapability.ORDER_MANAGEMENT
        ])

        # Trading state
        self.positions: Dict[str, Decimal] = {}
        self.orders: Dict[str, Order] = {}
        self.balances: Dict[str, Decimal] = {}

        # Market data state
        self.latest_prices: Dict[str, MarketData] = {}

        # Initialize Market Regime Detector and Smart Trading Thresholds
        self.market_regime_detector = MarketRegimeDetector(config)
        self.smart_trading_thresholds = SmartTradingThresholds(config, self.market_regime_detector)

        self.logger.debug("BaseTradingAgent initialized.")

    async def setup(self):
        """Set up trading agent message handlers and initial state"""
        # Register message handlers
        self.register_handler(TradingMessageTypes.MARKET_DATA.value, self._handle_market_data)
        self.register_handler(TradingMessageTypes.ORDER_UPDATE.value, self._handle_order_update)
        self.register_handler(TradingMessageTypes.ORDER_FILL.value, self._handle_order_fill)
        self.register_handler(TradingMessageTypes.BALANCE_UPDATE.value, self._handle_balance_update)

        # Initialize trading state
        await self._initialize_trading_state()

        # Initialize components
        await self.market_regime_detector.initialize()
        await self.smart_trading_thresholds.initialize()

    async def _initialize_trading_state(self):
        """Initialize trading state - override in subclasses if needed"""
        self.logger.debug("Initializing trading state.")

    async def _handle_market_data(self, message):
        """Process incoming market data"""
        try:
            payload = message.get("payload", {})
            market_data = MarketData(**payload)
            self.latest_prices[market_data.symbol] = market_data
            self.logger.debug(f"Received market data: {market_data}")
            await self.on_market_data(market_data)

            # Update market regime
            # For this example, we'll call "update_market_data" in MarketRegimeDetector asynchronously:
            await self.market_regime_detector.update_market_data(market_data)

            # Also update SmartTradingThresholds data
            self.smart_trading_thresholds.update_market_data(
                symbol=market_data.symbol,
                price=market_data.last_price,
                volume=market_data.volume,
                current_vol=market_data.volume,  # As a proxy for volatility
                trade_cost=market_data.cost,
                timestamp=datetime.fromisoformat(market_data.timestamp)
            )

            # (Optional) Demonstration: recalc thresholds with a placeholder trade_size of 1000.0
            self.smart_trading_thresholds.calculate_thresholds_and_sizing(
                symbol=market_data.symbol,
                trade_size=Decimal("1000.0"),
                base_price=market_data.last_price
            )

        except Exception as e:
            self.logger.error(f"Error processing market data: {str(e)}")

    async def _handle_order_update(self, message):
        """Process order status updates"""
        try:
            payload = message.get("payload", {})
            order = Order(**payload)
            self.orders[order.order_id] = order
            self.logger.debug(f"Received order update: {order}")
            await self.on_order_update(order)
        except Exception as e:
            self.logger.error(f"Error processing order update: {str(e)}")

    async def _handle_order_fill(self, message):
        """Process order fills"""
        try:
            payload = message.get("payload", {})
            order = Order(**payload)
            self.orders[order.order_id] = order
            self.logger.debug(f"Received order fill: {order}")

            # Update position
            if order.status == OrderStatus.FILLED:
                symbol = order.symbol
                fill_qty = order.filled_quantity
                if order.side.upper() == "SELL":
                    fill_qty = -fill_qty
                self.positions[symbol] = self.positions.get(symbol, Decimal("0")) + fill_qty
                self.logger.debug(f"Updated position for {symbol}: {self.positions[symbol]}")
            await self.on_order_fill(order)
        except Exception as e:
            self.logger.error(f"Error processing order fill: {str(e)}")

    async def _handle_balance_update(self, message):
        """Process balance updates"""
        try:
            payload = message.get("payload", {})
            for asset, balance in payload.items():
                self.balances[asset] = Decimal(str(balance))
            self.logger.debug(f"Updated balances: {self.balances}")
            await self.on_balance_update(self.balances)
        except Exception as e:
            self.logger.error(f"Error processing balance update: {str(e)}")

    # Trading Actions
    async def place_order(self, order: Order):
        """Place a new order"""
        try:
            message = {"order": order.__dict__}
            await self.send_message("exchange", TradingMessageTypes.ORDER_NEW.value, message)
            self.orders[order.order_id] = order
            self.logger.debug(f"Placed order: {order}")
        except Exception as e:
            self.logger.error(f"Error placing order: {str(e)}")

    async def cancel_order(self, order_id: str):
        """Cancel an existing order"""
        try:
            if order_id in self.orders:
                message = {"order_id": order_id}
                await self.send_message("exchange", TradingMessageTypes.ORDER_CANCEL.value, message)
                self.logger.debug(f"Cancelled order with ID: {order_id}")
            else:
                self.logger.warning(f"Attempted to cancel non-existent order ID: {order_id}")
        except Exception as e:
            self.logger.error(f"Error cancelling order: {str(e)}")

    # Override these methods in strategy implementations
    async def on_market_data(self, market_data: MarketData):
        """Called when new market data is received"""
        pass

    async def on_order_update(self, order: Order):
        """Called when an order status is updated"""
        pass

    async def on_order_fill(self, order: Order):
        """Called when an order is filled"""
        pass

    async def on_balance_update(self, balances: Dict[str, Decimal]):
        """Called when balances are updated"""
        pass



