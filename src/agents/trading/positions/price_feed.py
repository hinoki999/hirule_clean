import asyncio
from typing import Dict, Optional, Set, Callable
from dataclasses import dataclass
from datetime import datetime

@dataclass
class PriceUpdate:
    asset: str
    price: float
    bid: Optional[float] = None
    ask: Optional[float] = None
    volume: Optional[float] = None
    timestamp: Optional[datetime] = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

class PriceFeed:
    def __init__(self):
        self._subscribers: Dict[str, Set[Callable]] = {}
        self._last_prices: Dict[str, PriceUpdate] = {}

    async def subscribe(self, asset: str, callback: Callable) -> None:
        """Subscribe to price updates for an asset."""
        if asset not in self._subscribers:
            self._subscribers[asset] = set()
        self._subscribers[asset].add(callback)

    async def unsubscribe(self, asset: str, callback: Callable) -> None:
        """Unsubscribe from price updates."""
        if asset in self._subscribers and callback in self._subscribers[asset]:
            self._subscribers[asset].remove(callback)
            if not self._subscribers[asset]:
                del self._subscribers[asset]

    async def publish_update(self, update: PriceUpdate) -> None:
        """Publish a price update to subscribers."""
        self._last_prices[update.asset] = update
        if update.asset in self._subscribers:
            # Create a copy of the subscribers set to safely iterate
            subscribers = self._subscribers[update.asset].copy()
            for callback in subscribers:
                try:
                    await callback(update)
                except Exception as e:
                    print(f"Error in price update callback: {e}")

    def get_last_price(self, asset: str) -> Optional[PriceUpdate]:
        """Get the last known price for an asset."""
        return self._last_prices.get(asset)
