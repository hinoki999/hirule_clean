import asyncio
import logging
from typing import Dict, List, Optional, Set
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum

class OrderType(Enum):
    MARKET = "market"
    LIMIT = "limit"
    STOP_LOSS = "stop_loss"
    TAKE_PROFIT = "take_profit"

class OrderSide(Enum):
    BUY = "buy"
    SELL = "sell"

class OrderStatus(Enum):
    PENDING = "pending"
    OPEN = "open"
    FILLED = "filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"

@dataclass
class Order:
    id: str
    asset: str
    order_type: OrderType
    side: OrderSide
    size: float
    price: Optional[float]
    status: OrderStatus
    timestamp: datetime
    fill_price: Optional[float] = None
    fill_time: Optional[datetime] = None
    entry_price: Optional[float] = None
    related_orders: Set[str] = field(default_factory=set)

    def __post_init__(self):
        if self.order_type == OrderType.MARKET:
            self.entry_price = self.price


class OrderManager:
    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.orders: Dict[str, Order] = {}
        self.active_orders: Dict[str, Order] = {}
        self.fills: Dict[str, List[Dict]] = {}
        self.order_counter = 0

    def _generate_order_id(self) -> str:
        self.order_counter += 1
        return f"order_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{self.order_counter}"

    async def create_market_order(
        self,
        asset: str,
        side: OrderSide,
        size: float,
        attach_stops: bool = True
    ) -> Order:
        order_id = self._generate_order_id()
        order = Order(
            id=order_id,
            asset=asset,
            order_type=OrderType.MARKET,
            side=side,
            size=size,
            price=None,
            status=OrderStatus.PENDING,
            timestamp=datetime.now()
        )
        self.orders[order_id] = order
        self.active_orders[order_id] = order
        return order

    async def create_limit_order(
        self,
        asset: str,
        side: OrderSide,
        size: float,
        price: float
    ) -> Order:
        order_id = self._generate_order_id()
        order = Order(
            id=order_id,
            asset=asset,
            order_type=OrderType.LIMIT,
            side=side,
            size=size,
            price=price,
            status=OrderStatus.PENDING,
            timestamp=datetime.now()
        )
        self.orders[order_id] = order
        self.active_orders[order_id] = order
        return order

    async def create_stop_order(
        self,
        asset: str,
        side: OrderSide,
        size: float,
        stop_price: float,
        order_type: OrderType,
        parent_order_id: Optional[str] = None
    ) -> Order:
        order_id = self._generate_order_id()
        order = Order(
            id=order_id,
            asset=asset,
            order_type=order_type,
            side=side,
            size=size,
            price=stop_price,
            status=OrderStatus.PENDING,
            timestamp=datetime.now()
        )
        
        if parent_order_id:
            order.related_orders.add(parent_order_id)
            if parent_order_id in self.orders:
                self.orders[parent_order_id].related_orders.add(order_id)
        
        self.orders[order_id] = order
        self.active_orders[order_id] = order
        return order

    async def process_fill(
        self,
        order_id: str,
        fill_price: float,
        fill_time: Optional[datetime] = None
    ) -> bool:
        if order_id not in self.orders:
            return False
            
        order = self.orders[order_id]
        if order.status != OrderStatus.OPEN:
            return False
        
        order.status = OrderStatus.FILLED
        order.fill_price = fill_price
        order.fill_time = fill_time or datetime.now()
        self.active_orders.pop(order_id, None)
        
        if order_id not in self.fills:
            self.fills[order_id] = []
        
        self.fills[order_id].append({
            "price": fill_price,
            "time": order.fill_time,
            "size": order.size
        })
        
        if order.order_type == OrderType.MARKET:
            await self._attach_stop_orders(order)
        
        return True

    async def _attach_stop_orders(self, parent_order: Order) -> List[Order]:
        if not parent_order.fill_price:
            return []

        stops = []
        stop_loss_pct = self.config["stops"]["stop_loss_percent"]
        take_profit_pct = self.config["stops"]["take_profit_percent"]
        
        stop_loss_price = parent_order.fill_price * (1 - stop_loss_pct)
        take_profit_price = parent_order.fill_price * (1 + take_profit_pct)
        
        stop_loss = await self.create_stop_order(
            parent_order.asset,
            OrderSide.SELL,
            parent_order.size,
            stop_loss_price,
            OrderType.STOP_LOSS,
            parent_order.id
        )
        
        take_profit = await self.create_stop_order(
            parent_order.asset,
            OrderSide.SELL,
            parent_order.size,
            take_profit_price,
            OrderType.TAKE_PROFIT,
            parent_order.id
        )
        
        stop_loss.related_orders.add(take_profit.id)
        take_profit.related_orders.add(stop_loss.id)
        
        parent_order.related_orders.add(stop_loss.id)
        parent_order.related_orders.add(take_profit.id)
        
        stops.extend([stop_loss, take_profit])
        return stops

    async def cancel_order(self, order_id: str) -> bool:
        if order_id not in self.orders:
            return False
            
        order = self.orders[order_id]
        if order.status not in [OrderStatus.PENDING, OrderStatus.OPEN]:
            return False
        
        order.status = OrderStatus.CANCELLED
        self.active_orders.pop(order_id, None)
        
        for related_id in order.related_orders:
            if related_id in self.orders:
                related_order = self.orders[related_id]
                if related_order.status in [OrderStatus.PENDING, OrderStatus.OPEN]:
                    related_order.status = OrderStatus.CANCELLED
                    self.active_orders.pop(related_id, None)
        
        return True

    def get_order(self, order_id: str) -> Optional[Order]:
        return self.orders.get(order_id)

    def get_active_orders(self, asset: Optional[str] = None) -> List[Order]:
        orders = list(self.active_orders.values())
        if asset:
            orders = [o for o in orders if o.asset == asset]
        return orders

    def get_fills(self, order_id: str) -> List[Dict]:
        return self.fills.get(order_id, [])
