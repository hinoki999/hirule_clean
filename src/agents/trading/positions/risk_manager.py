from dataclasses import dataclass
from typing import Dict, List, Optional

@dataclass
class RiskProfile:
    current_volatility: float = 0.0
    risk_score: float = 0.0
    position_limit: float = 0.0

class RiskManager:
    def __init__(self, config: dict, pnl_monitor):
        self.config = config
        self.pnl_monitor = pnl_monitor
        self.risk_limits = config.get("risk_limits", {})
        self.position_size_config = config.get("position_size_config", {})
        self.risk_weights = config.get("risk_weights", {})

    async def calculate_position_size(self, asset: str, current_price: float) -> float:
        """Calculate position size based on risk parameters."""
        # Get risk limits
        max_position_size = self.risk_limits.get("max_position_size", float('inf'))
        max_exposure = self.risk_limits.get("max_portfolio_exposure", float('inf'))
        
        # Add a buffer for price movements (e.g., 2%)
        buffer_factor = 0.98  # This means we'll use 98% of the max exposure
        adjusted_max_exposure = max_exposure * buffer_factor
        
        # Calculate current portfolio exposure
        current_exposure = 0.0
        for pos in self.pnl_monitor.positions.values():
            current_exposure += pos.get("current_price", 0) * pos.get("size", 0)

        # Calculate remaining exposure capacity
        remaining_exposure = adjusted_max_exposure - current_exposure
        if remaining_exposure <= 0:
            return 0
            
        # Calculate size based on price and exposure limit
        # Apply additional buffer for potential price movements
        max_units = (remaining_exposure / current_price) * buffer_factor
        
        # Apply position size limit
        position_size = min(max_units, max_position_size)

        return position_size

    async def check_portfolio_risk(self) -> List[Dict]:
        """Check portfolio-wide risk metrics."""
        alerts = []
        total_exposure = 0.0

        # Calculate total exposure
        for metrics in self.pnl_monitor.positions.values():
            current_price = metrics.get("current_price", 0)
            size = metrics.get("size", 0)
            exposure = current_price * size
            total_exposure += exposure

        # Check exposure limits
        max_exposure = self.risk_limits.get("max_portfolio_exposure", float('inf'))
        if total_exposure >= max_exposure:
            alerts.append({
                "type": "exposure_limit",
                "message": f"Portfolio exposure {total_exposure:.2f} at or exceeds limit {max_exposure:.2f}"
            })

        return alerts
        
    async def update_risk_profile(self, asset: str) -> RiskProfile:
        """Update risk profile for an asset."""
        volatility = await self._get_asset_volatility(asset)
        
        # Calculate risk score based on various factors
        vol_weight = self.risk_weights.get("volatility", 0.6)
        correlation_weight = self.risk_weights.get("correlation", 0.4)
        
        # Get metrics for risk calculations
        metrics = self.pnl_monitor.get_performance_summary(asset)
        pnl_factor = 0.0
        if metrics:
            pnl_pct = metrics.get("pnl_percent", 0)
            # Add a penalty for negative PnL
            if pnl_pct < 0:
                pnl_factor = abs(pnl_pct) * 0.1  # Scale factor for negative PnL
        
        # Calculate composite risk score
        risk_score = (
            volatility * vol_weight +
            pnl_factor * correlation_weight
        )
        
        # Calculate position limit based on risk score
        max_size = self.risk_limits.get("max_position_size", float('inf'))
        # Higher risk score means lower position limit
        position_limit = max_size * (1 - risk_score)
        
        return RiskProfile(
            current_volatility=volatility,
            risk_score=risk_score,
            position_limit=position_limit
        )

    async def _get_asset_volatility(self, asset: str) -> float:
        """Get current volatility estimate for an asset."""
        base_vol = self.position_size_config.get("base_volatility", 0.02)
        
        # Get recent price data from PnL monitor
        metrics = self.pnl_monitor.get_performance_summary(asset)
        if metrics:
            pnl_volatility = abs(metrics.get("pnl_percent", 0)) / 100
            # Use the higher of base volatility or recent price movement
            return max(base_vol, pnl_volatility)
            
        return base_vol
