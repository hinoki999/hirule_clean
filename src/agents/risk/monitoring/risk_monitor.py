from typing import Dict, List, Optional, Tuple
from enum import Enum
import logging
from dataclasses import dataclass
from datetime import datetime

class AlertSeverity(Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"

class AlertType(Enum):
    VAR_BREACH = "var_breach"
    DRAWDOWN_BREACH = "drawdown_breach"
    EXPOSURE_LIMIT = "exposure_limit"
    POSITION_LOSS = "position_loss"
    VOLATILITY_SPIKE = "volatility_spike"
    CORRELATION_SHIFT = "correlation_shift"
    LIQUIDITY_WARNING = "liquidity_warning"

@dataclass
class RiskAlert:
    alert_type: AlertType
    severity: AlertSeverity
    message: str
    timestamp: datetime
    metrics: Dict
    threshold: float
    current_value: float
    asset: Optional[str] = None

class RiskMonitor:
    def __init__(self, config: Dict):
        self._validate_config(config)
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.active_alerts: List[RiskAlert] = []
        self.alert_history: List[RiskAlert] = []
        self.last_alert_times: Dict[Tuple[AlertType, Optional[str]], datetime] = {}

    def _validate_config(self, config: Dict) -> None:
        required_fields = [
            "alert_thresholds",
            "alert_cooldown",
            "notification_endpoints"
        ]
        if not all(field in config for field in required_fields):
            raise ValueError("Missing required configuration fields")

    async def check_risk_metrics(self, metrics: Dict, positions: Dict) -> List[RiskAlert]:
        try:
            current_alerts = []
            thresholds = self.config["alert_thresholds"]
            
            # Check VaR
            if metrics["var_95"] > thresholds["var_limit"]:
                alert = await self._create_alert(
                    AlertType.VAR_BREACH,
                    AlertSeverity.CRITICAL,
                    f"VaR exceeds limit: {metrics['var_95']:,.2f} > {thresholds['var_limit']:,.2f}",
                    metrics,
                    thresholds["var_limit"],
                    metrics["var_95"]
                )
                if self._check_alert_cooldown(alert):
                    current_alerts.append(alert)
            
            # Check drawdown
            if metrics["max_drawdown"] > thresholds["max_drawdown"]:
                alert = await self._create_alert(
                    AlertType.DRAWDOWN_BREACH,
                    AlertSeverity.CRITICAL,
                    f"Drawdown exceeds limit: {metrics['max_drawdown']*100:.1f}% > {thresholds['max_drawdown']*100:.1f}%",
                    metrics,
                    thresholds["max_drawdown"],
                    metrics["max_drawdown"]
                )
                if self._check_alert_cooldown(alert):
                    current_alerts.append(alert)
            
            # Check position-specific risks
            for asset, position in positions.items():
                pnl_pct = (position.current_price - position.entry_price) / position.entry_price
                
                if pnl_pct < -thresholds["position_loss_limit"]:
                    alert = await self._create_alert(
                        AlertType.POSITION_LOSS,
                        AlertSeverity.WARNING,
                        f"Position {asset} loss exceeds limit: {pnl_pct*100:.1f}%",
                        metrics,
                        -thresholds["position_loss_limit"],
                        pnl_pct,
                        asset
                    )
                    if self._check_alert_cooldown(alert):
                        current_alerts.append(alert)
            
            # Process approved alerts
            if current_alerts:
                await self._process_alerts(current_alerts)
            return current_alerts
            
        except Exception as e:
            self.logger.error(f"Error checking risk metrics: {str(e)}")
            raise

    def _check_alert_cooldown(self, alert: RiskAlert) -> bool:
        cooldown_key = (alert.alert_type, alert.asset)
        
        if cooldown_key not in self.last_alert_times:
            return True
            
        time_since_last = datetime.now() - self.last_alert_times[cooldown_key]
        return time_since_last.total_seconds() >= self.config["alert_cooldown"]

    async def _create_alert(
        self,
        alert_type: AlertType,
        severity: AlertSeverity,
        message: str,
        metrics: Dict,
        threshold: float,
        current_value: float,
        asset: Optional[str] = None
    ) -> RiskAlert:
        return RiskAlert(
            alert_type=alert_type,
            severity=severity,
            message=message,
            timestamp=datetime.now(),
            metrics=metrics,
            threshold=threshold,
            current_value=current_value,
            asset=asset
        )

    async def _process_alerts(self, alerts: List[RiskAlert]) -> None:
        try:
            for alert in alerts:
                # Add to active alerts and history
                self.active_alerts.append(alert)
                self.alert_history.append(alert)
                
                # Update last alert time
                self.last_alert_times[(alert.alert_type, alert.asset)] = alert.timestamp
                
                # Log alert
                log_message = f"{alert.severity.value.upper()}: {alert.message}"
                if alert.severity == AlertSeverity.CRITICAL:
                    self.logger.critical(log_message)
                elif alert.severity == AlertSeverity.WARNING:
                    self.logger.warning(log_message)
                else:
                    self.logger.info(log_message)
                
                # Dispatch notifications
                await self._dispatch_alert(alert)
                
        except Exception as e:
            self.logger.error(f"Error processing alerts: {str(e)}")
            raise

    async def _dispatch_alert(self, alert: RiskAlert) -> None:
        try:
            notification = {
                "type": alert.alert_type.value,
                "severity": alert.severity.value,
                "message": alert.message,
                "timestamp": alert.timestamp.isoformat(),
                "metrics": alert.metrics,
                "threshold": alert.threshold,
                "current_value": alert.current_value
            }
            
            if alert.asset:
                notification["asset"] = alert.asset
            
            for endpoint in self.config["notification_endpoints"]:
                try:
                    self.logger.info(f"Would dispatch to endpoint: {endpoint}")
                except Exception as e:
                    self.logger.error(f"Failed to dispatch to endpoint {endpoint}: {str(e)}")
            
        except Exception as e:
            self.logger.error(f"Error dispatching alert: {str(e)}")
            raise

    async def clear_alert(self, alert_id: str) -> None:
        self.active_alerts = [a for a in self.active_alerts if str(id(a)) != alert_id]

    def get_active_alerts(self, severity: Optional[AlertSeverity] = None) -> List[RiskAlert]:
        if severity:
            return [a for a in self.active_alerts if a.severity == severity]
        return self.active_alerts.copy()

    def get_alert_history(
        self,
        alert_type: Optional[AlertType] = None,
        severity: Optional[AlertSeverity] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[RiskAlert]:
        alerts = self.alert_history.copy()
        
        if alert_type:
            alerts = [a for a in alerts if a.alert_type == alert_type]
        if severity:
            alerts = [a for a in alerts if a.severity == severity]
        if start_time:
            alerts = [a for a in alerts if a.timestamp >= start_time]
        if end_time:
            alerts = [a for a in alerts if a.timestamp <= end_time]
            
        return alerts
