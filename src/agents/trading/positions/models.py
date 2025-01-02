from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Position:
    asset: str
    size: float
    entry_price: float
    current_price: float
    timestamp: datetime
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None

@dataclass
class PositionUpdate:
    asset: str
    current_price: float
    timestamp: datetime
    volume: Optional[float] = None
    bid: Optional[float] = None
    ask: Optional[float] = None
