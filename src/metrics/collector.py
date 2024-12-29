from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import statistics
import json

@dataclass
class ProcessingMetric:
    """Stores processing time metrics for lead enrichment"""
    start_time: datetime
    end_time: Optional[datetime] = None
    success: bool = False
    validation_status: str = "pending"
    error_type: Optional[str] = None
    warning_count: int = 0

    def complete(self, success: bool, validation_status: str, error_type: Optional[str] = None, warning_count: int = 0):
        self.end_time = datetime.now()
        self.success = success
        self.validation_status = validation_status
        self.error_type = error_type
        self.warning_count = warning_count

    @property
    def processing_time(self) -> Optional[float]:
        """Returns processing time in milliseconds"""
        if self.end_time:
            return (self.end_time - self.start_time).total_seconds() * 1000
        return None

class MetricsCollector:
    """Collects and analyzes metrics for lead enrichment"""
    
    def __init__(self, window_size: timedelta = timedelta(hours=1)):
        self.window_size = window_size
        self.metrics: List[ProcessingMetric] = []
        self._cleanup_threshold = 1000  # Cleanup when more than 1000 metrics
        
    def start_processing(self) -> ProcessingMetric:
        """Start tracking a new lead processing operation"""
        metric = ProcessingMetric(start_time=datetime.now())
        self.metrics.append(metric)
        self._cleanup_old_metrics()
        return metric
        
    def _cleanup_old_metrics(self):
        """Remove old metrics and perform cleanup if needed"""
        if len(self.metrics) > self._cleanup_threshold:
            cutoff_time = datetime.now() - self.window_size
            self.metrics = [m for m in self.metrics if m.start_time > cutoff_time]
    
    def get_current_metrics(self) -> Dict:
        """Get current metrics summary"""
        current_window = [m for m in self.metrics 
                         if m.start_time > datetime.now() - self.window_size
                         and m.end_time is not None]
        
        if not current_window:
            return {
                "total_processed": 0,
                "success_rate": 0,
                "avg_processing_time_ms": 0,
                "error_count": 0,
                "warning_rate": 0,
                "timestamp": datetime.now().isoformat()
            }
        
        total = len(current_window)
        successful = len([m for m in current_window if m.success])
        processing_times = [m.processing_time for m in current_window if m.processing_time is not None]
        error_count = len([m for m in current_window if m.error_type is not None])
        warnings = sum(m.warning_count for m in current_window)
        
        return {
            "total_processed": total,
            "success_rate": (successful / total) * 100 if total > 0 else 0,
            "avg_processing_time_ms": statistics.mean(processing_times) if processing_times else 0,
            "error_count": error_count,
            "warning_rate": (warnings / total) if total > 0 else 0,
            "timestamp": datetime.now().isoformat()
        }

    def get_error_distribution(self) -> Dict[str, int]:
        """Get distribution of error types"""
        current_window = [m for m in self.metrics 
                         if m.start_time > datetime.now() - self.window_size
                         and m.error_type is not None]
        
        error_counts: Dict[str, int] = {}
        for metric in current_window:
            if metric.error_type:
                error_counts[metric.error_type] = error_counts.get(metric.error_type, 0) + 1
                
        return error_counts
