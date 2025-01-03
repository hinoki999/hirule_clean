# src/agents/trading/ma_crossover_agent.py

from src.agents.trading.base_trading_agent import BaseTradingAgent
from src.agents.trading.messages import MarketData, Order, OrderType, OrderSide
from decimal import Decimal
from collections import deque
import uuid

class MovingAverageCrossoverAgent(BaseTradingAgent):
    ###"""
    Implementation of a simple MA crossover strategy
    ###"""

    def __init__(self, symbol: str, fast_period: int = 10, slow_period: int = 20, **kwargs):
        super().__init__(**kwargs)
        self.symbol = symbol
        self.fast_period = fast_period
        self.slow_period = slow_period

        # Price history
        self.price_history = deque(maxlen=slow_period)
        self.position_size = Decimal('0.1')  # Standard position size

    async def _initialize_trading_state(self):
        ###"""Initialize strategy-specific state###"""
        self.current_position = Decimal('0')
        self.fast_ma = None
        self.slow_ma = None

    async def on_market_data(self, market_data: MarketData):
        ###"""Process new market data and execute strategy###"""
        if market_data.symbol != self.symbol:
            return

        # Update price history and calculate MAs
        self.price_history.append(market_data.last_price)

        if len(self.price_history) >= self.slow_period:
            self.fast_ma = sum(list(self.price_history)[-self.fast_period:]) / self.fast_period
            self.slow_ma = sum(list(self.price_history)) / self.slow_period

            # Generate trading signals
            await self._check_signals(market_data)

    async def _check_signals(self, market_data: MarketData):
        ###"""Check for and execute trading signals###"""
        if self.fast_ma is None or self.slow_ma is None:
            return

        # Golden cross - fast MA crosses above slow MA
        if self.fast_ma > self.slow_ma and self.current_position <= 0:
            await self._enter_long(market_data)

        # Death cross - fast MA crosses below slow MA
        elif self.fast_ma < self.slow_ma and self.current_position >= 0:
            await self._enter_short(market_data)

    async def _enter_long(self, market_data: MarketData):
        ###"""Enter a long position###"""
        order = Order(
            order_id=str(uuid.uuid4()),
            symbol=self.symbol,
            side=OrderSide.BUY,
            order_type=OrderType.MARKET,
            quantity=self.position_size,
            price=None,
            stop_price=None,
            status=OrderStatus.NEW
        )
        await self.place_order(order)

    async def _enter_short(self, market_data: MarketData):
        ###"""Enter a short position###"""
        order = Order(
            order_id=str(uuid.uuid4()),
            symbol=self.symbol,
            side=OrderSide.SELL,
            order_type=OrderType.MARKET,
            quantity=self.position_size,
            price=None,
            stop_price=None,
            status=OrderStatus.NEW
        )
        await self.place_order(order)



