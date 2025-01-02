from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import numpy as np

@dataclass
class RiskAlert:
    timestamp: datetime
    alert_type: str
    severity: str  # 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL'
    message: str
    metric_value: float
    threshold_value: float

class RiskMonitor:
    def __init__(self, config: Dict[str, float]):
        self.config = config
        self.alerts: List[RiskAlert] = []
        self.position_limits = config.get('position_limits', {})
        self.value_at_risk_limit = config.get('var_limit', 0.02)  # 2% default
        self.drawdown_limit = config.get('drawdown_limit', 0.1)  # 10% default
        self.leverage_limit = config.get('leverage_limit', 2.0)
        self.concentration_limit = config.get('concentration_limit', 0.25)  # 25% default
        
    def check_position_risk(self, positions: Dict[str, Dict]) -> List[RiskAlert]:
        """Monitor position-specific risks"""
        alerts = []
        total_value = sum(abs(pos['value']) for pos in positions.values())
        
        for symbol, position in positions.items():
            # Check position size against limits
            size = abs(position['value'])
            limit = self.position_limits.get(symbol, total_value * self.concentration_limit)
            
            if size > limit:
                alerts.append(RiskAlert(
                    timestamp=datetime.now(),
                    alert_type='POSITION_SIZE',
                    severity='HIGH' if size > limit * 1.5 else 'MEDIUM',
                    message=f'Position size for {symbol} exceeds limit',
                    metric_value=size,
                    threshold_value=limit
                ))
                
            # Check leverage
            leverage = position.get('leverage', 1.0)
            if leverage > self.leverage_limit:
                alerts.append(RiskAlert(
                    timestamp=datetime.now(),
                    alert_type='LEVERAGE',
                    severity='HIGH' if leverage > self.leverage_limit * 1.5 else 'MEDIUM',
                    message=f'Leverage for {symbol} exceeds limit',
                    metric_value=leverage,
                    threshold_value=self.leverage_limit
                ))
                
        return alerts
    
    def check_portfolio_risk(self, 
                           portfolio_value: float,
                           daily_returns: List[float],
                           positions: Dict[str, Dict]) -> List[RiskAlert]:
        """Monitor portfolio-level risks"""
        alerts = []
        
        # Check Value at Risk
        var = self._calculate_var(daily_returns)
        if abs(var) > self.value_at_risk_limit:
            alerts.append(RiskAlert(
                timestamp=datetime.now(),
                alert_type='VAR',
                severity='HIGH' if abs(var) > self.value_at_risk_limit * 1.5 else 'MEDIUM',
                message='Portfolio VaR exceeds limit',
                metric_value=abs(var),
                threshold_value=self.value_at_risk_limit
            ))
        
        # Check Maximum Drawdown
        drawdown = self._calculate_drawdown(daily_returns)
        if drawdown > self.drawdown_limit:
            alerts.append(RiskAlert(
                timestamp=datetime.now(),
                alert_type='DRAWDOWN',
                severity='HIGH' if drawdown > self.drawdown_limit * 1.5 else 'MEDIUM',
                message='Portfolio drawdown exceeds limit',
                metric_value=drawdown,
                threshold_value=self.drawdown_limit
            ))
        
        # Check Portfolio Concentration
        concentration = self._calculate_concentration(positions)
        if concentration > self.concentration_limit:
            alerts.append(RiskAlert(
                timestamp=datetime.now(),
                alert_type='CONCENTRATION',
                severity='MEDIUM',
                message='Portfolio concentration exceeds limit',
                metric_value=concentration,
                threshold_value=self.concentration_limit
            ))
            
        return alerts
    
    def check_market_risk(self, 
                         volatility: float,
                         correlation_matrix: Optional[np.ndarray] = None) -> List[RiskAlert]:
        """Monitor market-related risks"""
        alerts = []
        vol_limit = self.config.get('volatility_limit', 0.02)  # 2% daily
        
        if volatility > vol_limit:
            alerts.append(RiskAlert(
                timestamp=datetime.now(),
                alert_type='VOLATILITY',
                severity='HIGH' if volatility > vol_limit * 1.5 else 'MEDIUM',
                message='Market volatility exceeds limit',
                metric_value=volatility,
                threshold_value=vol_limit
            ))
            
        if correlation_matrix is not None:
            # Check for correlation breakdown
            correlation_change = self._analyze_correlation_changes(correlation_matrix)
            corr_limit = self.config.get('correlation_change_limit', 0.3)
            
            if abs(correlation_change) > corr_limit:
                alerts.append(RiskAlert(
                    timestamp=datetime.now(),
                    alert_type='CORRELATION',
                    severity='MEDIUM',
                    message='Significant correlation regime change detected',
                    metric_value=abs(correlation_change),
                    threshold_value=corr_limit
                ))
                
        return alerts
    
    def _calculate_var(self, returns: List[float], confidence: float = 0.95) -> float:
        """Calculate Value at Risk"""
        if not returns:
            return 0.0
        return float(np.percentile(returns, (1 - confidence) * 100))
    
    def _calculate_drawdown(self, returns: List[float]) -> float:
        """Calculate current drawdown"""
        if not returns:
            return 0.0
        cumulative = np.cumprod(1 + np.array(returns))
        peak = np.maximum.accumulate(cumulative)
        drawdown = (cumulative - peak) / peak
        return abs(float(min(drawdown, default=0)))
    
    def _calculate_concentration(self, positions: Dict[str, Dict]) -> float:
        """Calculate portfolio concentration (Herfindahl index)"""
        if not positions:
            return 0.0
        total_value = sum(abs(pos['value']) for pos in positions.values())
        weights = [abs(pos['value']) / total_value for pos in positions.values()]
        return sum(w * w for w in weights)
    
    def _analyze_correlation_changes(self, correlation_matrix: np.ndarray) -> float:
        """Analyze changes in correlation structure"""
        # This is a simplified measure - could be enhanced with more sophisticated methods
        if not hasattr(self, '_last_correlation'):
            self._last_correlation = correlation_matrix
            return 0.0
            
        change = np.mean(np.abs(correlation_matrix - self._last_correlation))
        self._last_correlation = correlation_matrix
        return change
    
    def get_active_alerts(self, min_severity: str = 'MEDIUM') -> List[RiskAlert]:
        """Get all active alerts above specified severity"""
        severity_levels = {'LOW': 0, 'MEDIUM': 1, 'HIGH': 2, 'CRITICAL': 3}
        min_level = severity_levels[min_severity]
        
        return [alert for alert in self.alerts 
                if severity_levels[alert.severity] >= min_level]
    
    def clear_alerts(self) -> None:
        """Clear all alerts"""
        self.alerts = []
