from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from enum import Enum
import json
import statistics
from collections import defaultdict

class MetricType(Enum):
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"

@dataclass
class MetricPoint:
    timestamp: float
    value: float
    labels: Dict[str, str] = field(default_factory=dict)

class MetricsCollector:
    ###"""Collects and manages metrics for the lead enrichment system.###"""

    def __init__(self, max_history: int = 1000):
        self.max_history = max_history
        self._metrics: Dict[str, List[MetricPoint]] = defaultdict(list)
        self._metric_types: Dict[str, MetricType] = {}

    def record_metric(self, name: str, value: float, metric_type: MetricType, labels: Optional[Dict[str, str]] = None):
        ###"""Record a new metric point.###"""
        if labels is None:
            labels = {}

        metric_point = MetricPoint(
            timestamp=datetime.now().timestamp(),
            value=value,
            labels=labels
        )

        self._metric_types[name] = metric_type
        self._metrics[name].append(metric_point)

        # Maintain history limit
        if len(self._metrics[name]) > self.max_history:
            self._metrics[name] = self._metrics[name][-self.max_history:]

    def get_metric_summary(self, name: str, time_window: timedelta = timedelta(hours=1)) -> Dict:
        ###"""Get summary statistics for a metric within the time window.###"""
        if name not in self._metrics:
            return {"error": f"Metric {name} not found"}

        cutoff_time = datetime.now().timestamp() - time_window.total_seconds()
        recent_points = [
            point for point in self._metrics[name]
            if point.timestamp >= cutoff_time
        ]

        if not recent_points:
            return {"error": f"No data points found for {name} in the specified time window"}

        values = [point.value for point in recent_points]

        summary = {
            "metric_type": self._metric_types[name].value,
            "count": len(values),
            "current": values[-1],
            "min": min(values),
            "max": max(values),
            "mean": statistics.mean(values),
            "time_window_seconds": time_window.total_seconds()
        }

        # Add median and percentiles for histograms and summaries
        if self._metric_types[name] in [MetricType.HISTOGRAM, MetricType.SUMMARY]:
            summary.update({
                "median": statistics.median(values),
                "p95": statistics.quantiles(values, n=20)[18] if len(values) >= 20 else None,
                "p99": statistics.quantiles(values, n=100)[98] if len(values) >= 100 else None
            })

        return summary

    def get_all_metrics(self, time_window: timedelta = timedelta(hours=1)) -> Dict:
        ###"""Get summaries for all metrics.###"""
        return {
            name: self.get_metric_summary(name, time_window)
            for name in self._metrics.keys()
        }

    def export_metrics(self, time_window: timedelta = timedelta(hours=1)) -> str:
        ###"""Export metrics in JSON format.###"""
        return json.dumps(self.get_all_metrics(time_window), indent=2)


