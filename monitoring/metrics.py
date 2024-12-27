from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union
import statistics

class MetricType(Enum):
    GAUGE = "gauge"         # Point-in-time value (e.g., memory usage)
    COUNTER = "counter"     # Cumulative value (e.g., total requests)
    HISTOGRAM = "histogram" # Distribution of values (e.g., request durations)
    SUMMARY = "summary"     # Statistical summary of values

@dataclass
class MetricValue:
    timestamp: datetime
    value: Union[float, int, List[float]]
    metric_type: MetricType
    labels: Dict[str, str] = None

class MetricCollector:
    """Handles collection and processing of different metric types"""
    
    def __init__(self):
        self._metrics: Dict[str, List[MetricValue]] = {}
        self._counters: Dict[str, float] = {}  # Store running counter values
    
    def record_metric(self, name: str, value: Union[float, int, List[float]], 
                     metric_type: MetricType, labels: Dict[str, str] = None) -> None:
        """Record a new metric value"""
        if name not in self._metrics:
            self._metrics[name] = []
            
        metric = MetricValue(
            timestamp=datetime.utcnow(),
            value=value,
            metric_type=metric_type,
            labels=labels or {}
        )
        
        if metric_type == MetricType.COUNTER:
            # For counters, we store the cumulative value
            if name not in self._counters:
                self._counters[name] = 0
            self._counters[name] += float(value)
            metric.value = self._counters[name]
            
        self._metrics[name].append(metric)
        
    def get_metric_history(self, name: str, 
                          start_time: Optional[datetime] = None,
                          end_time: Optional[datetime] = None) -> List[MetricValue]:
        """Get historical values for a metric within the specified time range"""
        if name not in self._metrics:
            return []
            
        metrics = self._metrics[name]
        if start_time:
            metrics = [m for m in metrics if m.timestamp >= start_time]
        if end_time:
            metrics = [m for m in metrics if m.timestamp <= end_time]
        return metrics
    
    def get_metric_statistics(self, name: str, 
                            start_time: Optional[datetime] = None,
                            end_time: Optional[datetime] = None) -> Dict[str, float]:
        """Calculate statistics for a metric within the specified time range"""
        metrics = self.get_metric_history(name, start_time, end_time)
        if not metrics:
            return {}
            
        values = [m.value for m in metrics]
        metric_type = metrics[0].metric_type
        
        stats = {
            "count": len(values),
            "last_value": values[-1]
        }
        
        if metric_type in [MetricType.GAUGE, MetricType.COUNTER]:
            try:
                stats.update({
                    "min": min(values),
                    "max": max(values),
                    "mean": statistics.mean(values),
                    "median": statistics.median(values)
                })
                if len(values) > 1:
                    stats["stddev"] = statistics.stdev(values)
            except TypeError:
                pass  # Handle non-numeric values gracefully
                
        elif metric_type == MetricType.HISTOGRAM:
            # For histograms, calculate percentiles
            sorted_values = sorted(values)
            stats.update({
                "p50": statistics.median(sorted_values),
                "p90": sorted_values[int(0.9 * len(sorted_values))],
                "p95": sorted_values[int(0.95 * len(sorted_values))],
                "p99": sorted_values[int(0.99 * len(sorted_values))]
            })
            
        return stats
    
    def clear_old_metrics(self, retention_time: datetime) -> None:
        """Remove metrics older than retention_time"""
        for name in self._metrics:
            self._metrics[name] = [
                m for m in self._metrics[name] 
                if m.timestamp >= retention_time
            ]