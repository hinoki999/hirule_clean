from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional

@dataclass
class PnLAlert:
    alert_type: str
    message: str

class PnLMonitor:
    def __init__(self, config: dict):
        self.config = config
        self.positions: Dict[str, Dict] = {}

    async def update_position(self, order, current_price) -> List[PnLAlert]:
        alerts = []
        
        # Store position data
        self.positions[order.asset] = {
            "entry_price": order.entry_price,
            "current_price": current_price,
            "size": order.size,
            "side": order.side
        }
        
        # Calculate P&L
        if order.entry_price:
            pnl_pct = (current_price - order.entry_price) / order.entry_price
            if order.side.value == "sell":
                pnl_pct = -pnl_pct
                
            thresholds = self.config.get("alert_thresholds", {})
            
            # Check for alerts
            if pnl_pct <= -thresholds.get("stop_loss", 0.01):
                alerts.append(PnLAlert(
                    alert_type="stop_loss",
                    message=f"Stop loss triggered at {pnl_pct:.2%}"
                ))
            elif pnl_pct >= thresholds.get("profit_target", 0.02):
                alerts.append(PnLAlert(
                    alert_type="take_profit",
                    message=f"Take profit triggered at {pnl_pct:.2%}"
                ))
        
        return alerts

    def get_performance_summary(self, asset: str) -> Dict:
        """Get performance metrics for a position."""
        if asset not in self.positions:
            return {}
            
        position = self.positions[asset]
        entry_price = position["entry_price"]
        current_price = position["current_price"]
        size = position["size"]
        
        # Calculate metrics
        price_change = current_price - entry_price
        if position["side"].value == "sell":
            price_change = -price_change
            
        pnl = price_change * size
        pnl_pct = (price_change / entry_price) * 100
        exposure = current_price * size
        
        return {
            "current_pnl": pnl,
            "pnl_percent": pnl_pct,
            "exposure": exposure
        }
