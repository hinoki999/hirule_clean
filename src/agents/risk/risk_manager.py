from typing import Dict, Optional, List
import numpy as np
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta

@dataclass
class Position:
    asset: str
    size: float
    entry_price: float
    current_price: float
    timestamp: datetime
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None

class RiskMetrics:
    def __init__(self):
        self.var_95: float = 0.0  # 95% Value at Risk
        self.max_drawdown: float = 0.0
        self.sharpe_ratio: float = 0.0
        self.current_exposure: float = 0.0
        self.peak_exposure: float = 0.0

class RiskManagerError(Exception):
    pass

class RiskManager:
    def __init__(self, config: Dict):
        """
        Initialize RiskManager with configuration settings.
        
        Args:
            config: Dictionary containing:
                max_position_size: Maximum size for any single position
                max_total_exposure: Maximum total exposure across all positions
                risk_per_trade: Maximum risk per trade as percentage of portfolio
                max_drawdown: Maximum allowed drawdown percentage
                var_limit: Value at Risk limit
                position_timeout: Maximum position holding time in hours
        """
        self._validate_config(config)
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.positions: Dict[str, Position] = {}
        self.metrics = RiskMetrics()
        self.historical_prices: Dict[str, List[float]] = {}
        self.position_history: List[Position] = []

    def _validate_config(self, config: Dict) -> None:
        required_fields = [
            "max_position_size",
            "max_total_exposure",
            "risk_per_trade",
            "max_drawdown",
            "var_limit",
            "position_timeout"
        ]
        
        if not all(field in config for field in required_fields):
            raise RiskManagerError("Missing required configuration fields")
            
        if not (0 < config["risk_per_trade"] <= 0.1):  # Max 10% risk per trade
            raise RiskManagerError("Risk per trade must be between 0% and 10%")
            
        if not (0 < config["max_drawdown"] <= 0.3):  # Max 30% drawdown
            raise RiskManagerError("Max drawdown must be between 0% and 30%")

    def calculate_position_size(self, asset: str, entry_price: float, stop_loss: float) -> float:
        """Calculate safe position size based on risk parameters."""
        try:
            risk_amount = self.config["risk_per_trade"] * self._get_portfolio_value()
            price_risk = abs(entry_price - stop_loss) / entry_price
            position_size = risk_amount / (price_risk * entry_price)
            
            # Apply position size limits
            position_size = min(
                position_size,
                self.config["max_position_size"],
                self._get_remaining_exposure()
            )
            
            return position_size
            
        except Exception as e:
            self.logger.error(f"Error calculating position size: {str(e)}")
            raise RiskManagerError(f"Position size calculation failed: {str(e)}")

    async def check_risk_limits(self, trade_proposal: Dict) -> Dict:
        """
        Check if a proposed trade meets risk management criteria.
        
        Args:
            trade_proposal: Dictionary containing:
                asset: Asset identifier
                size: Proposed position size
                entry_price: Proposed entry price
                stop_loss: Stop loss price
                take_profit: Take profit price (optional)
        
        Returns:
            Dictionary with:
                approved: Boolean indicating if trade meets risk criteria
                adjusted_size: Adjusted position size if needed
                risk_metrics: Current risk metrics after hypothetical trade
                message: Explanation if trade is rejected
        """
        try:
            # Validate trade proposal
            required_fields = ["asset", "size", "entry_price", "stop_loss"]
            if not all(field in trade_proposal for field in required_fields):
                raise RiskManagerError("Invalid trade proposal format")

            # Calculate risk metrics with proposed position
            hypothetical_metrics = await self._calculate_risk_metrics(trade_proposal)
            
            # Check various risk limits
            checks = [
                (hypothetical_metrics.var_95 <= self.config["var_limit"], 
                 "VaR limit exceeded"),
                (hypothetical_metrics.max_drawdown <= self.config["max_drawdown"],
                 "Max drawdown limit exceeded"),
                (self._get_remaining_exposure() >= trade_proposal["size"] * trade_proposal["entry_price"],
                 "Exposure limit exceeded")
            ]
            
            # If any checks fail, return rejection
            for check_passed, message in checks:
                if not check_passed:
                    return {
                        "approved": False,
                        "adjusted_size": 0,
                        "risk_metrics": hypothetical_metrics,
                        "message": message
                    }
            
            # Calculate safe position size
            safe_size = self.calculate_position_size(
                trade_proposal["asset"],
                trade_proposal["entry_price"],
                trade_proposal["stop_loss"]
            )
            
            return {
                "approved": True,
                "adjusted_size": min(safe_size, trade_proposal["size"]),
                "risk_metrics": hypothetical_metrics,
                "message": "Trade approved"
            }
            
        except Exception as e:
            self.logger.error(f"Error checking risk limits: {str(e)}")
            raise RiskManagerError(f"Risk check failed: {str(e)}")

    async def _calculate_risk_metrics(self, trade_proposal: Dict) -> RiskMetrics:
        """Calculate risk metrics including hypothetical new position."""
        metrics = RiskMetrics()
        
        try:
            # Calculate Value at Risk (VaR)
            returns = self._calculate_historical_returns()
            current_portfolio_value = self._get_portfolio_value()
            
            # Add hypothetical position to calculation
            hypo_position_value = trade_proposal["size"] * trade_proposal["entry_price"]
            combined_value = current_portfolio_value + hypo_position_value
            
            # Calculate 95% VaR using historical simulation
            if returns:
                var_95 = np.percentile(returns, 5) * combined_value
                metrics.var_95 = abs(var_95)
            
            # Calculate exposure metrics
            metrics.current_exposure = self._calculate_total_exposure() + hypo_position_value
            metrics.peak_exposure = max(
                metrics.current_exposure,
                self.metrics.peak_exposure
            )
            
            # Calculate maximum drawdown
            metrics.max_drawdown = self._calculate_max_drawdown()
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error calculating risk metrics: {str(e)}")
            raise RiskManagerError(f"Risk metrics calculation failed: {str(e)}")

    def _calculate_historical_returns(self) -> List[float]:
        """Calculate historical returns for VaR calculation."""
        returns = []
        for asset, prices in self.historical_prices.items():
            if len(prices) > 1:
                asset_returns = np.diff(prices) / prices[:-1]
                returns.extend(asset_returns)
        return returns

    def _calculate_max_drawdown(self) -> float:
        """Calculate maximum drawdown from position history."""
        if not self.position_history:
            return 0.0
            
        peaks = np.maximum.accumulate([p.entry_price for p in self.position_history])
        drawdowns = (peaks - [p.current_price for p in self.position_history]) / peaks
        return float(np.max(drawdowns)) if drawdowns.size > 0 else 0.0

    def _get_portfolio_value(self) -> float:
        """Calculate total portfolio value."""
        return sum(pos.size * pos.current_price for pos in self.positions.values())

    def _calculate_total_exposure(self) -> float:
        """Calculate total current exposure."""
        return sum(pos.size * pos.current_price for pos in self.positions.values())

    def _get_remaining_exposure(self) -> float:
        """Calculate remaining allowed exposure."""
        return max(0, self.config["max_total_exposure"] - self._calculate_total_exposure())

    async def update_position(self, asset: str, current_price: float) -> None:
        """Update position with current price and check stop conditions."""
        if asset not in self.positions:
            return
            
        position = self.positions[asset]
        position.current_price = current_price
        
        # Check stop loss
        if position.stop_loss and current_price <= position.stop_loss:
            await self._handle_stop_loss(asset)
            
        # Check take profit
        if position.take_profit and current_price >= position.take_profit:
            await self._handle_take_profit(asset)
            
        # Check position timeout
        if datetime.now() - position.timestamp > timedelta(hours=self.config["position_timeout"]):
            await self._handle_timeout(asset)

    async def _handle_stop_loss(self, asset: str) -> None:
        """Handle stop loss trigger."""
        self.logger.warning(f"Stop loss triggered for {asset}")
        # Implementation for stop loss handling

    async def _handle_take_profit(self, asset: str) -> None:
        """Handle take profit trigger."""
        self.logger.info(f"Take profit triggered for {asset}")
        # Implementation for take profit handling

    async def _handle_timeout(self, asset: str) -> None:
        """Handle position timeout."""
        self.logger.warning(f"Position timeout triggered for {asset}")
        # Implementation for timeout handling
