from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import Enum, auto
from typing import Optional, Dict, Any

class OrderType(Enum):
    MARKET = auto()
    LIMIT = auto()
    STOP = auto()
    STOP_LIMIT = auto()

class OrderSide(Enum):
    BUY = auto()
    SELL = auto()

class OrderStatus(Enum):
    NEW = auto()
    PENDING = auto()
    PARTIALLY_FILLED = auto()
    FILLED = auto()
    CANCELLED = auto()
    REJECTED = auto()

@dataclass
class MarketData:
    symbol: str
    timestamp: datetime
    bid: Decimal
    ask: Decimal
    last_price: Decimal
    volume: Decimal
    exchange: str

@dataclass
class Order:
    order_id: str
    symbol: str
    side: OrderSide
    order_type: OrderType
    quantity: Decimal
    price: Optional[Decimal]
    stop_price: Optional[Decimal]
    status: OrderStatus
    filled_quantity: Decimal = Decimal('0')
    remaining_quantity: Optional[Decimal] = None
    timestamp: datetime = None
    exchange: str = None
    
class TradingMessageTypes:
    # Market Data Messages
    MARKET_DATA = "market_data"
    ORDERBOOK_UPDATE = "orderbook_update"
    TRADE_UPDATE = "trade_update"
    
    # Order Related Messages
    ORDER_NEW = "order_new"
    ORDER_UPDATE = "order_update"
    ORDER_CANCEL = "order_cancel"
    ORDER_REJECT = "order_reject"
    ORDER_FILL = "order_fill"
    
    # Position and Risk Messages
    POSITION_UPDATE = "position_update"
    RISK_UPDATE = "risk_update"
    BALANCE_UPDATE = "balance_update"
    
    # Strategy Messages
    STRATEGY_SIGNAL = "strategy_signal"
    STRATEGY_UPDATE = "strategy_update"
    
    # System Messages
    TRADING_ERROR = "trading_error"
    EXCHANGE_STATUS = "exchange_status"

def create_market_data_message(market_data: MarketData) -> Dict[str, Any]:
    """Create a formatted market data message"""
    return {
        "type": TradingMessageTypes.MARKET_DATA,
        "data": {
            "symbol": market_data.symbol,
            "timestamp": market_data.timestamp.isoformat(),
            "bid": str(market_data.bid),
            "ask": str(market_data.ask),
            "last_price": str(market_data.last_price),
            "volume": str(market_data.volume),
            "exchange": market_data.exchange
        }
    }

def create_order_message(order: Order, message_type: str) -> Dict[str, Any]:
    """Create a formatted order message"""
    return {
        "type": message_type,
        "data": {
            "order_id": order.order_id,
            "symbol": order.symbol,
            "side": order.side.name,
            "order_type": order.order_type.name,
            "quantity": str(order.quantity),
            "price": str(order.price) if order.price else None,
            "stop_price": str(order.stop_price) if order.stop_price else None,
            "status": order.status.name,
            "filled_quantity": str(order.filled_quantity),
            "remaining_quantity": str(order.remaining_quantity) if order.remaining_quantity else None,
            "timestamp": order.timestamp.isoformat() if order.timestamp else None,
            "exchange": order.exchange
        }
    }