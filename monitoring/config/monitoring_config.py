# monitoring/config/monitoring_config.py

from dataclasses import dataclass
from typing import Dict

@dataclass
class MonitoringThresholds:
    LATENCY_THRESHOLDS = {
        'CRITICAL': 2000,  # ms
        'HIGH': 1000,      # ms
        'MEDIUM': 500,     # ms
        'LOW': 200        # ms
    }
    
    THROUGHPUT_THRESHOLDS = {
        'CRITICAL': 0.1,   # msgs/sec
        'HIGH': 0.5,       # msgs/sec
        'MEDIUM': 1.0,     # msgs/sec
        'LOW': 2.0        # msgs/sec
    }
    
    ERROR_RATE_THRESHOLDS = {
        'CRITICAL': 0.05,  # 5%
        'HIGH': 0.03,      # 3%
        'MEDIUM': 0.01,    # 1%
        'LOW': 0.005      # 0.5%
    }