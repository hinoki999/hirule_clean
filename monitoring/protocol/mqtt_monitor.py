<<<<<<< ours
from monitoring.base_monitor import BaseMonitor
from monitoring.advanced_health_monitor import AdvancedHealthMonitor
from monitoring.alerts import AlertSeverity
from typing import Dict, List
import time
import asyncio

class MQTTMonitor(BaseMonitor):
    def __init__(self):
        super().__init__()
        self.message_latencies = []
        self.connection_status = False
        self.advanced_monitor = AdvancedHealthMonitor()
        self.collection_interval = 60  # seconds
        asyncio.create_task(self.alert_manager.start())

    async def collect_metrics(self) -> Dict:
        # Collect basic metrics
        metrics = {
            'timestamp': time.time(),
            'message_latency': sum(self.message_latencies) / len(self.message_latencies) if self.message_latencies else 0,
            'connection_status': self.connection_status,
            'messages_processed': len(self.message_latencies),
            'throughput': await self.calculate_throughput(),
            'error_rate': await self.get_error_rate()
        }

         # Check metrics against thresholds
        await self.check_metrics_thresholds(metrics)

        # Store metrics history
        self.metrics_history.append(metrics)
        return metrics

    async def check_metrics_thresholds(self, metrics: Dict):
        # Check latency
        if metrics['message_latency'] > 1000:  # 1 second threshold
            await self.alert_manager.create_alert(
                severity=AlertSeverity.HIGH,
                message=f"High latency detected: {metrics['message_latency']}ms",
                source="MQTT_Monitor",
                metrics=metrics
            )

        # Check throughput
        if metrics['throughput'] < 0.1:  # Less than 0.1 messages per second
            await self.alert_manager.create_alert(
                severity=AlertSeverity.MEDIUM,
                message=f"Low throughput detected: {metrics['throughput']} msg/s",
                source="MQTT_Monitor",
                metrics=metrics
            )

        # Check error rate
        if metrics['error_rate'] > 0.05:  # 5% error rate threshold
            await self.alert_manager.create_alert(
                severity=AlertSeverity.CRITICAL,
                message=f"High error rate detected: {metrics['error_rate']*100}%",
                source="MQTT_Monitor",
                metrics=metrics
            )

        # Check connection status
        if not metrics['connection_status']:
            await self.alert_manager.create_alert(
                severity=AlertSeverity.CRITICAL,
                message="MQTT Connection lost",
                source="MQTT_Monitor",
                metrics=metrics
            )

    def calculate_average_latency(self) -> float:
        if not self.message_latencies:
            return 0.0
        return sum(self.message_latencies) / len(self.message_latencies)
        # Send to advanced monitor for analysis
        anomalies = await self.advanced_monitor.analyze_metrics(metrics)
        if anomalies:
            await self.handle_anomalies(anomalies)

        self.metrics_history.append(metrics)
        return metrics

    async def check_health(self) -> bool:
        if not self.connection_status:
            return False
        if self.message_latencies and sum(self.message_latencies) / len(self.message_latencies) > 1000:  # 1s threshold
            return False

        # Advanced health check using ML models
        health_status = await self.advanced_monitor.predict_health_status(self.metrics_history)
        return health_status

    def record_latency(self, latency_ms: float):
        self.message_latencies.append(latency_ms)
        if len(self.message_latencies) > 1000:
            self.message_latencies.pop(0)

    async def calculate_throughput(self) -> float:
        recent_messages = len([m for m in self.metrics_history
                             if time.time() - m['timestamp'] <= self.collection_interval])
        return recent_messages / self.collection_interval

    async def get_error_rate(self) -> float:
        if not self.metrics_history:
            return 0.0
        recent_metrics = [m for m in self.metrics_history
                         if time.time() - m['timestamp'] <= self.collection_interval]
        error_count = sum(1 for m in recent_metrics if not m['connection_status'])
        return error_count / len(recent_metrics) if recent_metrics else 0.0

    async def handle_anomalies(self, anomalies: List[Dict]):
        # Log anomalies
        for anomaly in anomalies:
            print(f"Detected anomaly: {anomaly['type']} - {anomaly['description']}")

        # Trigger alerts if needed
        if any(a['severity'] == 'critical' for a in anomalies):
            await self.trigger_alert(anomalies)

    async def trigger_alert(self, anomalies: List[Dict]):
        # Implement your alert system here
        pass


||||||| base
=======
from monitoring.base_monitor import BaseMonitor
from monitoring.advanced_health_monitor import AdvancedHealthMonitor
from typing import Dict, List
import time

class MQTTMonitor(BaseMonitor):
    def __init__(self):
        super().__init__()
        self.message_latencies = []
        self.connection_status = False
        self.advanced_monitor = AdvancedHealthMonitor()
        self.collection_interval = 60  # seconds
        
    async def collect_metrics(self) -> Dict:
        # Collect basic metrics
        metrics = {
            'timestamp': time.time(),
            'message_latency': sum(self.message_latencies) / len(self.message_latencies) if self.message_latencies else 0,
            'connection_status': self.connection_status,
            'messages_processed': len(self.message_latencies),
            'throughput': await self.calculate_throughput(),
            'error_rate': await self.get_error_rate()
        }
        
        # Send to advanced monitor for analysis
        anomalies = await self.advanced_monitor.analyze_metrics(metrics)
        if anomalies:
            await self.handle_anomalies(anomalies)
            
        self.metrics_history.append(metrics)
        return metrics
        
    async def check_health(self) -> bool:
        if not self.connection_status:
            return False
        if self.message_latencies and sum(self.message_latencies) / len(self.message_latencies) > 1000:  # 1s threshold
            return False
            
        # Advanced health check using ML models
        health_status = await self.advanced_monitor.predict_health_status(self.metrics_history)
        return health_status
        
    def record_latency(self, latency_ms: float):
        self.message_latencies.append(latency_ms)
        if len(self.message_latencies) > 1000:
            self.message_latencies.pop(0)
            
    async def calculate_throughput(self) -> float:
        recent_messages = len([m for m in self.metrics_history 
                             if time.time() - m['timestamp'] <= self.collection_interval])
        return recent_messages / self.collection_interval
        
    async def get_error_rate(self) -> float:
        if not self.metrics_history:
            return 0.0
        recent_metrics = [m for m in self.metrics_history 
                         if time.time() - m['timestamp'] <= self.collection_interval]
        error_count = sum(1 for m in recent_metrics if not m['connection_status'])
        return error_count / len(recent_metrics) if recent_metrics else 0.0
        
    async def handle_anomalies(self, anomalies: List[Dict]):
        # Log anomalies
        for anomaly in anomalies:
            print(f"Detected anomaly: {anomaly['type']} - {anomaly['description']}")
            
        # Trigger alerts if needed
        if any(a['severity'] == 'critical' for a in anomalies):
            await self.trigger_alert(anomalies)
            
    async def trigger_alert(self, anomalies: List[Dict]):
        # Implement your alert system here
        pass
>>>>>>> theirs
