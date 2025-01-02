from enum import Enum
from dataclasses import dataclass
from decimal import Decimal
from typing import Optional, Dict, Any
from datetime import datetime

class TradingMessageTypes(Enum):
    MARKET_DATA = "MARKET_DATA"
    ORDER = "ORDER"
    ORDER_UPDATE = "ORDER_UPDATE"
    TRADE = "TRADE"
    POSITION_UPDATE = "POSITION_UPDATE"
    BALANCE_UPDATE = "BALANCE_UPDATE"
    MARKET_REGIME = "MARKET_REGIME"
    RISK_UPDATE = "RISK_UPDATE"
    THRESHOLD_UPDATE = "THRESHOLD_UPDATE"

class OrderType(Enum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP = "STOP"
    STOP_LIMIT = "STOP_LIMIT"

class OrderSide(Enum):
    BUY = "BUY"
    SELL = "SELL"

class OrderStatus(Enum):
    NEW = "NEW"
    PENDING = "PENDING"
    OPEN = "OPEN"
    FILLED = "FILLED"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"

@dataclass
class Order:
    symbol: str
    side: OrderSide
    order_type: OrderType
    quantity: Decimal
    price: Optional[Decimal] = None
    status: OrderStatus = OrderStatus.NEW
    order_id: Optional[str] = None
    stop_price: Optional[Decimal] = None
    message_type: TradingMessageTypes = TradingMessageTypes.ORDER

@dataclass
class MarketData:
    symbol: str
    price: Decimal  # Renamed from last_price
    timestamp: float
    bid: Optional[Decimal] = None
    ask: Optional[Decimal] = None
    volume: Optional[Decimal] = None
    additional_info: Optional[Dict[str, Any]] = None
    message_type: TradingMessageTypes = TradingMessageTypes.MARKET_DATA
