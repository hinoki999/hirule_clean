import asyncio
import logging
from typing import Dict, List, Optional
from datetime import datetime
from src.agents.trading.positions.metrics import MetricsCalculator
from src.agents.trading.positions.pnl_monitor import PnLMonitor, PnLAlert
from src.agents.trading.positions.risk_manager import RiskManager, RiskProfile
from src.agents.trading.positions.order_manager import OrderManager, Order, OrderType, OrderSide, OrderStatus

class TradingSystem:
    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.pnl_monitor = PnLMonitor(config.get("pnl_config", {}))
        self.order_manager = OrderManager(config.get("order_config", {}))
        self.risk_manager = RiskManager(config.get("risk_config", {}), self.pnl_monitor)
        
        # System state
        self.active_positions: Dict[str, Dict] = {}
        self.account_balance: float = config.get("initial_balance", 0.0)

    async def open_position(self, asset: str, side: OrderSide, price: float, attach_stops: bool = True) -> Optional[Order]:
        """Open a new position with risk-adjusted size."""
        try:
            # First check current portfolio risk
            risk_alerts = await self.risk_manager.check_portfolio_risk()
            if any(alert["type"] == "exposure_limit" for alert in risk_alerts):
                self.logger.warning(f"Cannot open position: Portfolio exposure limit reached")
                return None

            # Calculate risk-adjusted position size based on price
            size = await self.risk_manager.calculate_position_size(asset, price)
            if size <= 0:
                self.logger.warning("Position size calculation resulted in zero or negative size")
                return None
            
            # Create and execute market order
            order = await self.order_manager.create_market_order(
                asset=asset,
                side=side,
                size=size,
                attach_stops=attach_stops
            )
            
            # Set entry price and process fill
            order.entry_price = price
            order.status = OrderStatus.OPEN
            await self.order_manager.process_fill(order.id, price)
            
            # Update position tracking
            self.active_positions[asset] = {
                "order_id": order.id,
                "side": side,
                "size": size,
                "entry_price": price
            }
            
            # Update P&L monitoring
            await self.pnl_monitor.update_position(order, price)
            
            return order
            
        except Exception as e:
            self.logger.error(f"Error opening position: {str(e)}")
            return None

    async def close_position(self, asset: str, price: float) -> Optional[Order]:
        """Close an existing position."""
        if asset not in self.active_positions:
            return None
            
        try:
            position = self.active_positions[asset]
            close_side = OrderSide.SELL if position["side"] == OrderSide.BUY else OrderSide.BUY
            
            # Create and execute closing order
            order = await self.order_manager.create_market_order(
                asset=asset,
                side=close_side,
                size=position["size"],
                attach_stops=False
            )
            
            # Set entry price and process fill
            order.entry_price = position["entry_price"]
            order.status = OrderStatus.OPEN
            await self.order_manager.process_fill(order.id, price)
            
            # Cancel any existing stop orders
            for active_order in self.order_manager.get_active_orders(asset):
                if active_order.order_type in [OrderType.STOP_LOSS, OrderType.TAKE_PROFIT]:
                    await self.order_manager.cancel_order(active_order.id)
                    
            # Update position tracking
            del self.active_positions[asset]
            
            # Final P&L update
            await self.pnl_monitor.update_position(order, price)
            
            return order
            
        except Exception as e:
            self.logger.error(f"Error closing position: {str(e)}")
            return None
            
    async def update_position(self, asset: str, current_price: float) -> List[PnLAlert]:
        """Update position metrics and check for alerts."""
        if asset not in self.active_positions:
            return []
            
        position = self.active_positions[asset]
        order = self.order_manager.get_order(position["order_id"])
        
        if not order:
            return []
            
        # Update P&L and check for alerts
        alerts = await self.pnl_monitor.update_position(order, current_price)
        
        # Check for stop triggers
        if alerts:
            for alert in alerts:
                if alert.alert_type == "stop_loss":
                    # Close position immediately
                    close_order = await self.close_position(asset, current_price)
                    if close_order:
                        self.logger.info(f"Stop loss triggered for {asset} at {current_price}")
                    
        return alerts
        
    async def get_position_summary(self, asset: str) -> Dict:
        """Get comprehensive position summary."""
        if asset not in self.active_positions:
            return {}
            
        position = self.active_positions[asset]
        order = self.order_manager.get_order(position["order_id"])
        
        # Get summaries from each component
        pnl_summary = self.pnl_monitor.get_performance_summary(asset)
        risk_profile = await self.risk_manager.update_risk_profile(asset)
        active_orders = self.order_manager.get_active_orders(asset)
        
        return {
            "position": position,
            "performance": pnl_summary,
            "risk_profile": {
                "current_volatility": risk_profile.current_volatility,
                "risk_score": risk_profile.risk_score,
                "position_limit": risk_profile.position_limit
            },
            "active_orders": [
                {
                    "id": order.id,
                    "type": order.order_type,
                    "price": order.price,
                    "status": order.status
                }
                for order in active_orders
            ]
        }
        
    async def get_portfolio_summary(self) -> Dict:
        """Get overall portfolio summary."""
        portfolio_metrics = {
            "total_exposure": 0.0,
            "total_pnl": 0.0,
            "position_count": len(self.active_positions),
            "positions": {}
        }
        
        for asset in self.active_positions:
            summary = await self.get_position_summary(asset)
            portfolio_metrics["positions"][asset] = summary
            
            if "performance" in summary and summary["performance"]:
                portfolio_metrics["total_pnl"] += summary["performance"].get("current_pnl", 0)
                portfolio_metrics["total_exposure"] += summary["performance"].get("exposure", 0)
                
        return portfolio_metrics
