<<<<<<< ours
import asyncio
from datetime import datetime
import psutil
import statistics
from typing import Dict, List, Optional

class SystemMonitor:
    def __init__(self):
        self.metrics_history: List[Dict] = []
        self.anomaly_thresholds = {
            'cpu_usage': 80.0,  # Percent
            'memory_usage': 85.0,  # Percent
            'message_latency': 100,  # ms
            'error_rate': 0.05  # 5% error threshold
        }

    async def collect_system_metrics(self) -> Dict:
        #"""Collect current system metrics#"""
        metrics = {
            'timestamp': datetime.now(),
            'cpu_usage': psutil.cpu_percent(),
            'memory_usage': psutil.virtual_memory().percent,
            'disk_usage': psutil.disk_usage('/').percent,
            'network_io': psutil.net_io_counters()._asdict()
        }
        self.metrics_history.append(metrics)
        if len(self.metrics_history) > 1000:  # Keep last 1000 readings
            self.metrics_history.pop(0)
        return metrics

    def predict_anomalies(self) -> Optional[Dict]:
        #"""Predict potential system issues using rolling averages#"""
        if len(self.metrics_history) < 10:
            return None

        recent_metrics = self.metrics_history[-10:]
        cpu_trend = statistics.mean([m['cpu_usage'] for m in recent_metrics])
        memory_trend = statistics.mean([m['memory_usage'] for m in recent_metrics])

        warnings = {}
        if cpu_trend > self.anomaly_thresholds['cpu_usage']:
            warnings['cpu'] = f"High CPU usage trend: {cpu_trend:.1f}%"
        if memory_trend > self.anomaly_thresholds['memory_usage']:
            warnings['memory'] = f"High memory usage trend: {memory_trend:.1f}%"

        return warnings if warnings else None

    async def monitor_health(self, callback):
        #"""Continuous health monitoring loop#"""
        while True:
            metrics = await self.collect_system_metrics()
            anomalies = self.predict_anomalies()
            if anomalies:
                await callback(anomalies)
            await asyncio.sleep(5)  # Check every 5 seconds


||||||| base
=======
import asyncio
from datetime import datetime
import psutil
import statistics
from typing import Dict, List, Optional

class SystemMonitor:
    def __init__(self):
        self.metrics_history: List[Dict] = []
        self.anomaly_thresholds = {
            'cpu_usage': 80.0,  # Percent
            'memory_usage': 85.0,  # Percent
            'message_latency': 100,  # ms
            'error_rate': 0.05  # 5% error threshold
        }
        
    async def collect_system_metrics(self) -> Dict:
        """Collect current system metrics"""
        metrics = {
            'timestamp': datetime.now(),
            'cpu_usage': psutil.cpu_percent(),
            'memory_usage': psutil.virtual_memory().percent,
            'disk_usage': psutil.disk_usage('/').percent,
            'network_io': psutil.net_io_counters()._asdict()
        }
        self.metrics_history.append(metrics)
        if len(self.metrics_history) > 1000:  # Keep last 1000 readings
            self.metrics_history.pop(0)
        return metrics
    
    def predict_anomalies(self) -> Optional[Dict]:
        """Predict potential system issues using rolling averages"""
        if len(self.metrics_history) < 10:
            return None
            
        recent_metrics = self.metrics_history[-10:]
        cpu_trend = statistics.mean([m['cpu_usage'] for m in recent_metrics])
        memory_trend = statistics.mean([m['memory_usage'] for m in recent_metrics])
        
        warnings = {}
        if cpu_trend > self.anomaly_thresholds['cpu_usage']:
            warnings['cpu'] = f"High CPU usage trend: {cpu_trend:.1f}%"
        if memory_trend > self.anomaly_thresholds['memory_usage']:
            warnings['memory'] = f"High memory usage trend: {memory_trend:.1f}%"
            
        return warnings if warnings else None
    
    async def monitor_health(self, callback):
        """Continuous health monitoring loop"""
        while True:
            metrics = await self.collect_system_metrics()
            anomalies = self.predict_anomalies()
            if anomalies:
                await callback(anomalies)
            await asyncio.sleep(5)  # Check every 5 seconds
>>>>>>> theirs
