import unittest
from datetime import datetime
import numpy as np
from src.analytics.risk_monitor import RiskMonitor, RiskAlert

class TestRiskMonitor(unittest.TestCase):
    def setUp(self):
        self.config = {
            'var_limit': 0.02,
            'drawdown_limit': 0.1,
            'leverage_limit': 2.0,
            'concentration_limit': 0.25,
            'position_limits': {
                'AAPL': 10000,
                'GOOGL': 15000
            }
        }
        self.risk_monitor = RiskMonitor(self.config)
        
    def test_position_risk_monitoring(self):
        positions = {
            'AAPL': {'value': 12000, 'leverage': 1.5},  # Exceeds position limit
            'GOOGL': {'value': 8000, 'leverage': 2.5}   # Exceeds leverage limit
        }
        
        alerts = self.risk_monitor.check_position_risk(positions)
        
        # Should have two alerts: one for position size, one for leverage
        self.assertEqual(len(alerts), 2)
        
        # Verify position size alert
        position_alert = next(a for a in alerts if a.alert_type == 'POSITION_SIZE')
        self.assertEqual(position_alert.severity, 'MEDIUM')
        self.assertEqual(position_alert.metric_value, 12000)
        
        # Verify leverage alert
        leverage_alert = next(a for a in alerts if a.alert_type == 'LEVERAGE')
        self.assertEqual(leverage_alert.severity, 'HIGH')
        self.assertEqual(leverage_alert.metric_value, 2.5)
        
    def test_portfolio_risk_monitoring(self):
        portfolio_value = 100000
        daily_returns = [-0.01, -0.02, -0.015, 0.01, -0.025]  # Significant losses
        positions = {
            'AAPL': {'value': 35000},  # 35% concentration
            'GOOGL': {'value': 25000}
        }
        
        alerts = self.risk_monitor.check_portfolio_risk(
            portfolio_value, daily_returns, positions
        )
        
        # Should have alerts for VaR, drawdown, and concentration
        self.assertGreaterEqual(len(alerts), 1)
        
        # Verify we get a concentration alert
        concentration_alert = next(
            (a for a in alerts if a.alert_type == 'CONCENTRATION'), None
        )
        self.assertIsNotNone(concentration_alert)
        self.assertEqual(concentration_alert.severity, 'MEDIUM')
        
    def test_market_risk_monitoring(self):
        volatility = 0.03  # 3% daily volatility
        correlation_matrix = np.array([
            [1.0, 0.5, 0.3],
            [0.5, 1.0, 0.4],
            [0.3, 0.4, 1.0]
        ])
        
        alerts = self.risk_monitor.check_market_risk(volatility, correlation_matrix)
        
        # Should have at least one alert for high volatility
        self.assertGreaterEqual(len(alerts), 1)
        
        volatility_alert = next(
            (a for a in alerts if a.alert_type == 'VOLATILITY'), None
        )
        self.assertIsNotNone(volatility_alert)
        self.assertEqual(volatility_alert.severity, 'HIGH')
        
    def test_alert_severity_filtering(self):
        # Create some test alerts
        test_alerts = [
            RiskAlert(
                timestamp=datetime.now(),
                alert_type='TEST',
                severity='LOW',
                message='Low severity alert',
                metric_value=1.0,
                threshold_value=1.0
            ),
            RiskAlert(
                timestamp=datetime.now(),
                alert_type='TEST',
                severity='HIGH',
                message='High severity alert',
                metric_value=2.0,
                threshold_value=1.0
            )
        ]
        
        self.risk_monitor.alerts = test_alerts
        
        # Filter for medium and above
        filtered_alerts = self.risk_monitor.get_active_alerts(min_severity='MEDIUM')
        self.assertEqual(len(filtered_alerts), 1)
        self.assertEqual(filtered_alerts[0].severity, 'HIGH')
        
    def test_clear_alerts(self):
        # Add some test alerts
        test_alert = RiskAlert(
            timestamp=datetime.now(),
            alert_type='TEST',
            severity='HIGH',
            message='Test alert',
            metric_value=1.0,
            threshold_value=1.0
        )
        self.risk_monitor.alerts = [test_alert]
        
        # Clear alerts
        self.risk_monitor.clear_alerts()
        self.assertEqual(len(self.risk_monitor.alerts), 0)
