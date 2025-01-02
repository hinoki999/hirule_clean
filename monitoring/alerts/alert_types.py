from enum import Enum
from dataclasses import dataclass
from typing import Dict, Any
from datetime import datetime

class AlertSeverity(Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

@dataclass
class Alert:
    severity: AlertSeverity
    message: str
    timestamp: datetime
    source: str
    metrics: Dict[str, Any]
    alert_id: str


