from decimal import Decimal
from typing import Dict, List, Optional
from collections import defaultdict
import logging
import asyncio
from .strategy import TradingStrategy
from .messages import MarketData, Order, OrderType, OrderSide, OrderStatus

class MomentumStrategy(TradingStrategy):
    def __init__(self, symbols: List[str], risk_manager=None,
                 position_size: Decimal = Decimal("0.1"),
                 momentum_window: int = 20,
                 momentum_threshold: float = 0.02,
                 **kwargs):
        super().__init__(symbols=symbols, risk_manager=risk_manager, 
                        position_size=position_size, **kwargs)
        self.momentum_window = momentum_window
        self.momentum_threshold = momentum_threshold
        self.price_history = defaultdict(list)
        self.positions = defaultdict(Decimal)
        self.market_data: Dict[str, MarketData] = {}

    async def on_market_data(self, data: MarketData) -> Optional[Order]:
        """Process new market data and generate signals"""
        if data.symbol not in self.symbols:
            return None

        await self.update_market_data(data)
        return await self.generate_signal(data.symbol)

    async def update_market_data(self, data: MarketData):
        """Update market data and maintain price history"""
        self.market_data[data.symbol] = data
        self.price_history[data.symbol].append(float(data.price))
        
        if len(self.price_history[data.symbol]) > self.momentum_window:
            self.price_history[data.symbol].pop(0)

    async def on_order_fill(self, order: Order):
        """Handle order fill updates"""
        if order.status == OrderStatus.FILLED:
            current_position = self.positions.get(order.symbol, Decimal("0"))
            fill_size = order.quantity if order.side == OrderSide.BUY else -order.quantity
            self.positions[order.symbol] = current_position + fill_size

    async def generate_signal(self, symbol: str) -> Optional[Order]:
        prices = self.price_history[symbol]
        if len(prices) < self.momentum_window:
            return None
            
        momentum = (prices[-1] / prices[0]) - 1
        if abs(momentum) > self.momentum_threshold:
            side = OrderSide.BUY if momentum > 0 else OrderSide.SELL
            return Order(
                symbol=symbol,
                side=side,
                order_type=OrderType.MARKET,
                quantity=self.position_size
            )
        return None
