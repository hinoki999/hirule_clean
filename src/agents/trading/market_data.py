from dataclasses import dataclass
from decimal import Decimal
from typing import Dict, Any, Optional

@dataclass
class MarketData:
    symbol: str
    price: Decimal
    timestamp: float
    volume: Optional[Decimal] = None
    additional_info: Optional[Dict[str, Any]] = None

    @property
    def last_price(self) -> Decimal:
        """Alias for price to maintain compatibility"""
        return self.price
