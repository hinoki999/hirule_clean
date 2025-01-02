
from abc import ABC, abstractmethod
import asyncio
from datetime import datetime
import psutil
import statistics
from typing import Dict, List, Optional, Union
from enum import Enum
from dataclasses import dataclass
from .advanced_health_monitor import AdvancedHealthMonitor

class MetricType(Enum):
    GAUGE = "gauge"
    COUNTER = "counter"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"

@dataclass
class MetricDefinition:
    name: str
    type: MetricType
    description: str
    unit: str
    thresholds: Dict[str, float]

class BaseMonitor(ABC):
    def __init__(self):
        # Core monitoring components
        self.advanced_monitor = AdvancedHealthMonitor()
        self.metrics_history = []
        self._running = False

        # Metric storage and definitions
        self.metrics = {}  # Dict[str, List[Dict]]
        self.metric_definitions = {}  # Dict[str, MetricDefinition]
        self._counter_values = {}  # Store running counter values

        # Monitoring configuration
        self.alert_manager = None
        self.collection_interval = 5
        self._collection_task = None
        self._system_metrics_enabled = True
        self._tasks = set()
        self._lock = asyncio.Lock()
    @property
    def _is_monitoring(self):
     #"""Check if monitoring is active#"""
     return self._running

async def start_monitoring(self, callback):
    #"""Start monitoring with callback support and enhanced system metrics#"""
    async with self._lock:
        if self._running:
            return

        self._running = True
        self._collection_task = asyncio.create_task(self._monitoring_loop(callback))
        self._tasks.add(self._collection_task)
        self._collection_task.add_done_callback(self._tasks.discard)

        # Wait a moment to ensure the monitoring loop has started
        await asyncio.sleep(0.1)

    @abstractmethod
    async def collect_metrics(self) -> Dict:
        #"""Collect metrics specific to agent type#"""
        pass

    @abstractmethod
    async def check_health(self) -> bool:
        #"""Check health specific to agent type#"""
        pass

    async def collect_system_metrics(self) -> Dict[str, float]:
        #"""Collect system-level metrics#"""
        if not self._system_metrics_enabled:
            return {}

        try:
            system_metrics = {}

            # CPU metrics
            system_metrics["system.cpu.percent"] = psutil.cpu_percent(interval=1)
            cpu_times = psutil.cpu_times()
            system_metrics["system.cpu.user"] = cpu_times.user
            system_metrics["system.cpu.system"] = cpu_times.system

            # Memory metrics
            memory = psutil.virtual_memory()
            system_metrics["system.memory.total"] = memory.total
            system_metrics["system.memory.available"] = memory.available
            system_metrics["system.memory.percent"] = memory.percent

            # Disk metrics
            disk = psutil.disk_usage('/')
            system_metrics["system.disk.total"] = disk.total
            system_metrics["system.disk.used"] = disk.used
            system_metrics["system.disk.free"] = disk.free
            system_metrics["system.disk.percent"] = disk.percent

            # Network metrics (as counters)
            net_io = psutil.net_io_counters()
            system_metrics["system.network.bytes_sent"] = net_io.bytes_sent
            system_metrics["system.network.bytes_recv"] = net_io.bytes_recv

            return system_metrics
        except Exception as e:
            await self.handle_collection_error(e)
            return {}
    async def start_monitoring(self, callback):
        #"""Start monitoring with callback support and enhanced system metrics#"""
        if self._running:
            return

        self._running = True
        self._collection_task = asyncio.create_task(self._monitoring_loop(callback))
        self._tasks.add(self._collection_task)
        self._collection_task.add_done_callback(self._tasks.discard)
        self._collection_task.add_done_callback(self._tasks.discard)

        await asyncio.sleep(0.1)

async def _monitoring_loop(self, callback):
    #"""Internal monitoring loop#"""
    while self._running:
        try:
            metrics = await self.collect_metrics()

            if self._system_metrics_enabled:
                system_metrics = await self.collect_system_metrics()
                metrics.update(system_metrics)

            await self.process_metrics(metrics)
            health_status = await self.check_health()

            await callback(metrics, health_status)

        except Exception as error:
            await self.handle_collection_error(error)

        await asyncio.sleep(self.collection_interval)

    async def stop_monitoring(self):
     #"""Stop all monitoring activities#"""
    async with self._lock:
        self._running = False
        if self._collection_task and not self._collection_task.done():
            self._collection_task.cancel()
            try:
                await self._collection_task
            except asyncio.CancelledError:
                pass

        # Wait for any remaining tasks to complete
        if self._tasks:
            await asyncio.gather(*self._tasks, return_exceptions=True)

    async def process_metrics(self, metrics: Dict):
        #"""Process and store collected metrics with enhanced storage and threshold checking#"""
        try:
            timestamp = datetime.utcnow()

            # Store in original metrics_history
            self.metrics_history.append({
                'timestamp': timestamp,
                **metrics
            })

            # Process and store metrics with type-specific handling
            for metric_name, value in metrics.items():
                if metric_name not in self.metrics:
                    self.metrics[metric_name] = []

                metric_data = {
                    'timestamp': timestamp,
                    'value': value
                }

                # Handle counter metrics
                if metric_name in self.metric_definitions:
                    metric_type = self.metric_definitions[metric_name].type
                    if metric_type == MetricType.COUNTER:
                        if metric_name not in self._counter_values:
                            self._counter_values[metric_name] = 0
                        self._counter_values[metric_name] += float(value)
                        metric_data['cumulative_value'] = self._counter_values[metric_name]

                self.metrics[metric_name].append(metric_data)

            # Check thresholds after processing all metrics
            await self.check_thresholds(metrics)

        except Exception as e:
            await self.handle_collection_error(e)

    async def check_thresholds(self, metrics: Dict):
     #"""Check metrics against defined thresholds and trigger alerts#"""
    if not self.alert_manager:
        return

    async with self._lock:
        try:
            for metric_name, value in metrics.items():
                if metric_name in self.metric_definitions:
                    definition = self.metric_definitions[metric_name]
                    for severity, threshold in definition.thresholds.items():
                        exceeded = await self._check_threshold_async(float(value), threshold, definition.type)
                        if exceeded:
                            await self.alert_manager.create_alert(
                                severity=severity,
                                message=f"{metric_name} exceeded {severity} threshold: {value} (threshold: {threshold})",
                                source=self.__class__.__name__,
                                metrics={metric_name: value}
                            )
        except Exception as e:
            await self.handle_collection_error(e)

async def _check_threshold_async(self, value: float, threshold: float, metric_type: MetricType) -> bool:
    #"""Async version of threshold checking#"""
    try:
        if metric_type == MetricType.GAUGE:
            return float(value) > float(threshold)
        elif metric_type == MetricType.COUNTER:
            return float(value) >= float(threshold)
        elif metric_type in (MetricType.HISTOGRAM, MetricType.SUMMARY):
            return float(value) > float(threshold)
        return False
    except (ValueError, TypeError) as e:
        print(f"Error comparing values: {e}")
        return False

    def _threshold_exceeded(self, value: float, threshold: float, metric_type: MetricType) -> bool:
        #"""Check if a threshold has been exceeded based on metric type#"""
        try:
            if metric_type == MetricType.GAUGE:
                return float(value) > float(threshold)
            elif metric_type == MetricType.COUNTER:
                return float(value) >= float(threshold)
            elif metric_type in (MetricType.HISTOGRAM, MetricType.SUMMARY):
                return float(value) > float(threshold)
            return False
        except (ValueError, TypeError) as e:
            # Log error but don't raise to prevent monitoring interruption
            print(f"Error comparing values: {e}")
            return False

    def get_metric_statistics(self, metric_name: str,
                         start_time: Optional[datetime] = None,
                         end_time: Optional[datetime] = None) -> Dict:
        #"""Calculate statistics for a specific metric#"""
        if metric_name not in self.metrics:
            return {}

        try:
            metrics = self.metrics[metric_name]
            if start_time:
                metrics = [m for m in metrics if m['timestamp'] >= start_time]
            if end_time:
                metrics = [m for m in metrics if m['timestamp'] <= end_time]

            if not metrics:
                return {}

            values = [m['value'] for m in metrics]

            stats = {
                "count": len(values),
                "last_value": values[-1],
                "min": min(values),
                "max": max(values),
                "mean": statistics.mean(values)
            }

            if metric_name in self.metric_definitions:
                metric_type = self.metric_definitions[metric_name].type
                if metric_type in [MetricType.HISTOGRAM, MetricType.SUMMARY]:
                    sorted_values = sorted(values)
                    stats.update({
                        "median": statistics.median(sorted_values),
                        "p90": sorted_values[int(0.9 * len(sorted_values))],
                        "p95": sorted_values[int(0.95 * len(sorted_values))],
                        "p99": sorted_values[int(0.99 * len(sorted_values))]
                    })
                    if len(values) > 1:
                        stats["stddev"] = statistics.stdev(values)

            return stats
        except Exception as e:
         self.handle_collection_error(e)
         return {}

    def enable_system_metrics(self, enabled: bool = True):
        #"""Enable or disable system metrics collection#"""
        self._system_metrics_enabled = enabled

    def register_system_metrics(self):
        #"""Register default system metrics with definitions#"""
        system_metrics = {
            "system.cpu.percent": (MetricType.GAUGE, "CPU utilization percentage", "%"),
            "system.memory.percent": (MetricType.GAUGE, "Memory usage percentage", "%"),
            "system.disk.percent": (MetricType.GAUGE, "Disk usage percentage", "%"),
            "system.network.bytes_sent": (MetricType.COUNTER, "Total bytes sent", "bytes"),
            "system.network.bytes_recv": (MetricType.COUNTER, "Total bytes received", "bytes")
        }

        for name, (metric_type, description, unit) in system_metrics.items():
            self.register_metric(
                name=name,
                metric_type=metric_type,
                description=description,
                unit=unit,
                thresholds={}  # Default to no thresholds
            )

    def register_metric(self,
                   name: str,
                   metric_type: MetricType,
                   description: str,
                   unit: str,
                   thresholds: Dict[str, float]):
      #"""Register a new metric with its definition and thresholds#"""
    # Validate inputs
    if not name or not isinstance(name, str):
        raise ValueError("Metric name must be a non-empty string")
    if not isinstance(metric_type, MetricType):
        raise ValueError("Invalid metric type")
    if not description or not isinstance(description, str):
        raise ValueError("Description must be a non-empty string")
    if not isinstance(unit, str):
        raise ValueError("Unit must be a string")
    if not isinstance(thresholds, dict):
        raise ValueError("Thresholds must be a dictionary")

    # Create metric definition
    self.metric_definitions[name] = MetricDefinition(
        name=name,
        type=metric_type,
        description=description,
        unit=unit,
        thresholds=thresholds
    )

    async def get_metric_history(self,
                               metric_name: str,
                               limit: Optional[int] = None) -> List[Dict]:
        #"""Get historical values for a specific metric#"""
        if metric_name not in self.metrics:
            return []
        history = self.metrics[metric_name]
        if limit:
            return history[-limit:]
        return history

    async def handle_collection_error(self, error: Exception):
        #"""Handle errors during metric collection#"""
        if self.alert_manager:
            await self.alert_manager.create_alert(
                severity="HIGH",
                message=f"Metric collection error: {str(error)}",
                source=self.__class__.__name__,
                metrics={"error": str(error)}
)

class MetricType(Enum):
    GAUGE = "gauge"
    COUNTER = "counter"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"

@dataclass
class MetricDefinition:
    name: str
    type: MetricType
    description: str
    unit: str
    thresholds: Dict[str, float]

class BaseMonitor(ABC):
    def __init__(self):
        # Core monitoring components
        self.advanced_monitor = AdvancedHealthMonitor()
        self.metrics_history = []
        self._running = False

        # Metric storage and definitions
        self.metrics = {}  # Dict[str, List[Dict]]
        self.metric_definitions = {}  # Dict[str, MetricDefinition]
        self._counter_values = {}  # Store running counter values

        # Monitoring configuration
        self.alert_manager = None
        self.collection_interval = 5
        self._collection_task = None
        self._system_metrics_enabled = True

    @abstractmethod
    async def collect_metrics(self) -> Dict:
        #"""Collect metrics specific to agent type#"""
        pass

    @abstractmethod
    async def check_health(self) -> bool:
        #"""Check health specific to agent type#"""
        pass

    async def collect_system_metrics(self) -> Dict[str, float]:
        #"""Collect system-level metrics#"""
        if not self._system_metrics_enabled:
            return {}

        try:
            system_metrics = {}

            # CPU metrics
            system_metrics["system.cpu.percent"] = psutil.cpu_percent(interval=1)
            cpu_times = psutil.cpu_times()
            system_metrics["system.cpu.user"] = cpu_times.user
            system_metrics["system.cpu.system"] = cpu_times.system

            # Memory metrics
            memory = psutil.virtual_memory()
            system_metrics["system.memory.total"] = memory.total
            system_metrics["system.memory.available"] = memory.available
            system_metrics["system.memory.percent"] = memory.percent

            # Disk metrics
            disk = psutil.disk_usage('/')
            system_metrics["system.disk.total"] = disk.total
            system_metrics["system.disk.used"] = disk.used
            system_metrics["system.disk.free"] = disk.free
            system_metrics["system.disk.percent"] = disk.percent

            # Network metrics (as counters)
            net_io = psutil.net_io_counters()
            system_metrics["system.network.bytes_sent"] = net_io.bytes_sent
            system_metrics["system.network.bytes_recv"] = net_io.bytes_recv

            return system_metrics
        except Exception as e:
            await self.handle_collection_error(e)
            return {}

    async def start_monitoring(self, callback):
        #"""Start monitoring with callback support and enhanced system metrics#"""
        self._running = True
        while self._running:
            try:
                # Collect custom metrics
                metrics = await self.collect_metrics()

                # Collect system metrics if enabled
                if self._system_metrics_enabled:
                    system_metrics = await self.collect_system_metrics()
                    metrics.update(system_metrics)

                # Process metrics and check health
                await self.process_metrics(metrics)
                health_status = await self.check_health()

                # Execute callback with results
                await callback(metrics, health_status)

            except Exception as error:
                await self.handle_collection_error(error)

            await asyncio.sleep(self.collection_interval)

    async def stop_monitoring(self):
        #"""Stop all monitoring activities#"""
        self._running = False
        if self._collection_task:
            self._collection_task.cancel()
            try:
                await self._collection_task
            except asyncio.CancelledError:
                pass

    async def process_metrics(self, metrics: Dict):
        #"""Process and store collected metrics with enhanced storage and threshold checking#"""
        try:
            timestamp = datetime.utcnow()

            # Store in original metrics_history
            self.metrics_history.append({
                'timestamp': timestamp,
                **metrics
            })

            # Process and store metrics with type-specific handling
            for metric_name, value in metrics.items():
                if metric_name not in self.metrics:
                    self.metrics[metric_name] = []

                metric_data = {
                    'timestamp': timestamp,
                    'value': value
                }

                # Handle counter metrics
                if metric_name in self.metric_definitions:
                    metric_type = self.metric_definitions[metric_name].type
                    if metric_type == MetricType.COUNTER:
                        if metric_name not in self._counter_values:
                            self._counter_values[metric_name] = 0
                        self._counter_values[metric_name] += float(value)
                        metric_data['cumulative_value'] = self._counter_values[metric_name]

                self.metrics[metric_name].append(metric_data)

            # Check thresholds after processing all metrics
            await self.check_thresholds(metrics)

        except Exception as e:
            await self.handle_collection_error(e)

    async def check_thresholds(self, metrics: Dict):
        #"""Check metrics against defined thresholds and trigger alerts#"""
        if not self.alert_manager:
            return

        try:
            for metric_name, value in metrics.items():
                if metric_name in self.metric_definitions:
                    definition = self.metric_definitions[metric_name]
                    for severity, threshold in definition.thresholds.items():
                        if self._threshold_exceeded(float(value), threshold, definition.type):
                            await self.alert_manager.create_alert(
                                severity=severity,
                                message=f"{metric_name} exceeded {severity} threshold: {value} (threshold: {threshold})",
                                source=self.__class__.__name__,
                                metrics={metric_name: value}
                            )
        except Exception as e:
            await self.handle_collection_error(e)

    def _threshold_exceeded(self, value: float, threshold: float, metric_type: MetricType) -> bool:
        #"""Check if a threshold has been exceeded based on metric type#"""
        try:
            if metric_type == MetricType.GAUGE:
                return float(value) > float(threshold)
            elif metric_type == MetricType.COUNTER:
                return float(value) >= float(threshold)
            elif metric_type in (MetricType.HISTOGRAM, MetricType.SUMMARY):
                return float(value) > float(threshold)
            return False
        except (ValueError, TypeError) as e:
            # Log error but don't raise to prevent monitoring interruption
            print(f"Error comparing values: {e}")
            return False

    def get_metric_statistics(self, metric_name: str,
                            start_time: Optional[datetime] = None,
                            end_time: Optional[datetime] = None) -> Dict:
        #"""Calculate statistics for a specific metric#"""
        if metric_name not in self.metrics:
            return {}

        # Filter metrics by time range if specified
        metrics = self.metrics[metric_name]
        if start_time:
            metrics = [m for m in metrics if m['timestamp'] >= start_time]
        if end_time:
            metrics = [m for m in metrics if m['timestamp'] <= end_time]

        if not metrics:
            return {}

        values = [m['value'] for m in metrics]

        # Calculate basic statistics
        stats = {
            "count": len(values),
            "last_value": values[-1],
            "min": min(values),
            "max": max(values),
            "mean": statistics.mean(values)
        }

        # Add additional statistics based on metric type
        if metric_name in self.metric_definitions:
            metric_type = self.metric_definitions[metric_name].type
            if metric_type in [MetricType.HISTOGRAM, MetricType.SUMMARY]:
                sorted_values = sorted(values)
                stats.update({
                    "median": statistics.median(sorted_values),
                    "p90": sorted_values[int(0.9 * len(sorted_values))],
                    "p95": sorted_values[int(0.95 * len(sorted_values))],
                    "p99": sorted_values[int(0.99 * len(sorted_values))]
                })
                if len(values) > 1:
                    stats["stddev"] = statistics.stdev(values)

        return stats

    def enable_system_metrics(self, enabled: bool = True):
        #"""Enable or disable system metrics collection#"""
        self._system_metrics_enabled = enabled

    def register_system_metrics(self):
        #"""Register default system metrics with definitions#"""
        system_metrics = {
            "system.cpu.percent": (MetricType.GAUGE, "CPU utilization percentage", "%"),
            "system.memory.percent": (MetricType.GAUGE, "Memory usage percentage", "%"),
            "system.disk.percent": (MetricType.GAUGE, "Disk usage percentage", "%"),
            "system.network.bytes_sent": (MetricType.COUNTER, "Total bytes sent", "bytes"),
            "system.network.bytes_recv": (MetricType.COUNTER, "Total bytes received", "bytes")
        }

        for name, (metric_type, description, unit) in system_metrics.items():
            self.register_metric(
                name=name,
                metric_type=metric_type,
                description=description,
                unit=unit,
                thresholds={}  # Default to no thresholds
            )

    def register_metric(self,
                   name: str,
                   metric_type: MetricType,
                   description: str,
                   unit: str,
                   thresholds: Dict[str, float]):
        #"""Register a new metric with its definition and thresholds#"""
        if not name or not isinstance(name, str):
            raise ValueError("Metric name must be a non-empty string")

        if not isinstance(metric_type, MetricType):
            raise ValueError("Invalid metric type")

        if not description or not isinstance(description, str):
            raise ValueError("Description must be a non-empty string")

        if not isinstance(unit, str):
            raise ValueError("Unit must be a string")

        if not isinstance(thresholds, dict):
            raise ValueError("Thresholds must be a dictionary")

        self.metric_definitions[name] = MetricDefinition(
        name=name,
        type=metric_type,
        description=description,
        unit=unit,
        thresholds=thresholds
    )

    async def get_metric_history(self,
                               metric_name: str,
                               limit: Optional[int] = None) -> List[Dict]:
        #"""Get historical values for a specific metric#"""
        if metric_name not in self.metrics:
            return []
        history = self.metrics[metric_name]
        if limit:
            return history[-limit:]
        return history

    async def handle_collection_error(self, error: Exception):
        #"""Handle errors during metric collection#"""
        if self.alert_manager:
            await self.alert_manager.create_alert(
                severity="HIGH",
                message=f"Metric collection error: {str(error)}",
                source=self.__class__.__name__,
                metrics={"error": str(error)}
            )


