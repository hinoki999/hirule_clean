from src.agents.BaseAgent import BaseAgent
from decimal import Decimal
from typing import Dict, Optional
from .messages import TradingMessageTypes
from .market_regime_detector import MarketRegimeDetector
from .smart_trading_thresholds import SmartTradingThresholds
import asyncio
import logging

class BaseTradingAgent(BaseAgent):
    def __init__(self, config, **kwargs):
        super().__init__(**kwargs)
        self.config = config
        self.positions: Dict[str, Decimal] = {}
        self.orders: Dict[str, Dict] = {}
        self.balances: Dict[str, Decimal] = {}
        self.latest_prices: Dict[str, float] = {}
        self.trade_history: Dict[str, Dict] = {}
        self.trading_thresholds = self.config.thresholds
        self.market_regime_detector = MarketRegimeDetector(self.trading_thresholds.config)
        self.smart_trading_thresholds = SmartTradingThresholds(self.trading_thresholds)

    async def setup(self):
        await super().setup()
        await self._initialize_trading_state()

    async def _initialize_trading_state(self):
        if not isinstance(self.positions, dict):
            self.positions = {}
        if not isinstance(self.orders, dict):
            self.orders = {}
        if not isinstance(self.balances, dict):
            self.balances = {}
        if not isinstance(self.trade_history, dict):
            self.trade_history = {}

    async def process_message(self, message: dict):
        """Process incoming messages"""
        message_type = message.get("type")
        payload = message.get("payload")
        
        if message_type == TradingMessageTypes.MARKET_DATA.value:
            await self._handle_market_data(payload)

    async def _handle_market_data(self, payload: dict):
        """Handle market data updates"""
        symbol = payload.get("symbol")
        price = payload.get("last_price")
        if symbol and price:
            self.latest_prices[symbol] = price
