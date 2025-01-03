<<<<<<< ours
import logging
import sys
from typing import Optional
import json
from datetime import datetime

def setup_logging(log_file: Optional[str] = None, level: int = logging.INFO):
    ###"""Setup logging configuration.###"""
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    handlers = [logging.StreamHandler(sys.stdout)]
    if log_file:
        handlers.append(logging.FileHandler(log_file))

    for handler in handlers:
        handler.setFormatter(formatter)

    logging.basicConfig(
        level=level,
        handlers=handlers
    )

class SystemMetrics:
    ###"""System-wide metrics tracking.###"""

    def __init__(self):
        self.metrics = {}
        self.start_time = datetime.now()

    def record_metric(self, name: str, value: float):
        ###"""Record a metric value.###"""
        if name not in self.metrics:
            self.metrics[name] = []
        self.metrics[name].append({
            'timestamp': datetime.now().timestamp(),
            'value': value
        })

    def get_metric(self, name: str) -> list:
        ###"""Get all records for a metric.###"""
        return self.metrics.get(name, [])

    def get_latest(self, name: str) -> Optional[float]:
        ###"""Get latest value for a metric.###"""
        values = self.metrics.get(name, [])
        return values[-1]['value'] if values else None

    def export_metrics(self, file_path: str):
        ###"""Export metrics to JSON file.###"""
        with open(file_path, 'w') as f:
            json.dump(self.metrics, f, indent=4)


||||||| base
=======
import logging
import sys
from typing import Optional
import json
from datetime import datetime

def setup_logging(log_file: Optional[str] = None, level: int = logging.INFO):
    """Setup logging configuration."""
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    handlers = [logging.StreamHandler(sys.stdout)]
    if log_file:
        handlers.append(logging.FileHandler(log_file))
    
    for handler in handlers:
        handler.setFormatter(formatter)
        
    logging.basicConfig(
        level=level,
        handlers=handlers
    )

class SystemMetrics:
    """System-wide metrics tracking."""
    
    def __init__(self):
        self.metrics = {}
        self.start_time = datetime.now()
    
    def record_metric(self, name: str, value: float):
        """Record a metric value."""
        if name not in self.metrics:
            self.metrics[name] = []
        self.metrics[name].append({
            'timestamp': datetime.now().timestamp(),
            'value': value
        })
    
    def get_metric(self, name: str) -> list:
        """Get all records for a metric."""
        return self.metrics.get(name, [])
    
    def get_latest(self, name: str) -> Optional[float]:
        """Get latest value for a metric."""
        values = self.metrics.get(name, [])
        return values[-1]['value'] if values else None
    
    def export_metrics(self, file_path: str):
        """Export metrics to JSON file."""
        with open(file_path, 'w') as f:
            json.dump(self.metrics, f, indent=4)
>>>>>>> theirs
