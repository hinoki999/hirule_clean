import asyncio
import logging
from typing import Dict, Optional, Set
from datetime import datetime
from .models import Position, PositionUpdate
from .price_feed import PriceFeed, PriceUpdate

class PositionTracker:
    def __init__(self, config: Dict, risk_monitor, price_feed: Optional[PriceFeed] = None):
        self.config = config
        self.risk_monitor = risk_monitor
        self.logger = logging.getLogger(__name__)
        self.positions: Dict[str, Position] = {}
        self.position_pnl: Dict[str, float] = {}
        self.price_feed = price_feed or PriceFeed()

    async def add_position(self, position: Position) -> None:
        """Add a new position and subscribe to price updates."""
        self.positions[position.asset] = position
        self.position_pnl[position.asset] = 0.0
        
        # Subscribe to price updates for this asset
        await self.price_feed.subscribe(
            position.asset,
            self._handle_price_update
        )
        
        self.logger.info(
            f"Added position: {position.asset}, "
            f"Size: {position.size}, "
            f"Entry: {position.entry_price:.4f}"
        )

    async def remove_position(self, asset: str) -> None:
        """Remove a position and unsubscribe from price updates."""
        if asset in self.positions:
            position = self.positions.pop(asset)
            final_pnl = self.position_pnl.pop(asset, 0.0)
            
            # Unsubscribe from price updates
            await self.price_feed.unsubscribe(
                asset,
                self._handle_price_update
            )
            
            self.logger.info(
                f"Removed position: {asset}, "
                f"Final P&L: {final_pnl:.2f}%"
            )

    async def _handle_price_update(self, update: PriceUpdate) -> None:
        """Handle incoming price updates."""
        if update.asset in self.positions:
            position = self.positions[update.asset]
            
            # Update position price
            position.current_price = update.price
            
            # Calculate and update P&L
            pnl = self._calculate_pnl(position)
            self.position_pnl[position.asset] = pnl
            
            # Check stop conditions
            if position.stop_loss and update.price <= position.stop_loss:
                self.logger.warning(f"Stop loss triggered for {position.asset}")
                await self.remove_position(position.asset)
                return
                
            if position.take_profit and update.price >= position.take_profit:
                self.logger.info(f"Take profit triggered for {position.asset}")
                await self.remove_position(position.asset)
                return
            
            # Log significant price moves
            if abs(update.price - position.entry_price) / position.entry_price > 0.001:
                self.logger.info(
                    f"Price update for {position.asset}: "
                    f"{position.entry_price:.4f} -> {update.price:.4f} "
                    f"(P&L: {pnl:.2f}%)"
                )

    def _calculate_pnl(self, position: Position) -> float:
        """Calculate position P&L as percentage."""
        return ((position.current_price - position.entry_price) / position.entry_price) * 100

    def get_position_summary(self) -> Dict:
        """Get summary of all tracked positions."""
        summary = {
            "positions": [],
            "total_positions": len(self.positions),
            "total_value": 0.0,
            "average_pnl": 0.0
        }
        
        total_value = 0.0
        total_pnl = 0.0
        
        for asset, position in self.positions.items():
            pos_value = position.size * position.current_price
            pnl = self.position_pnl.get(asset, 0.0)
            
            total_value += pos_value
            total_pnl += pnl
            
            summary["positions"].append({
                "asset": asset,
                "size": position.size,
                "entry_price": position.entry_price,
                "current_price": position.current_price,
                "value": pos_value,
                "pnl_percent": pnl,
                "has_stop_loss": position.stop_loss is not None,
                "has_take_profit": position.take_profit is not None
            })
        
        if summary["total_positions"] > 0:
            summary["total_value"] = total_value
            summary["average_pnl"] = total_pnl / summary["total_positions"]
            
        return summary
