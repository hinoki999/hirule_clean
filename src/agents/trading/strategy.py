from decimal import Decimal
from typing import Dict, Optional, List
import asyncio
import logging

from .messages import Order, OrderType, OrderSide, OrderStatus, MarketData

class TradingStrategy:
    def __init__(self, symbols: List[str], risk_manager=None, position_size: Decimal = Decimal("0.1"), **kwargs):
        self.symbols = symbols
        self.risk_manager = risk_manager
        self.position_size = position_size
        self.logger = logging.getLogger(self.__class__.__name__)
        self.positions: Dict[str, Decimal] = {}
        self.latest_prices: Dict[str, MarketData] = {}
        
    async def process_market_data(self, data: MarketData) -> Optional[Order]:
        """Process new market data and optionally generate orders"""
        self.latest_prices[data.symbol] = data
        return None
        
    async def handle_order_update(self, order: Order):
        """Handle updates to order status"""
        pass

    def get_position(self, symbol: str) -> Decimal:
        """Get current position for a symbol"""
        return self.positions.get(symbol, Decimal('0'))
