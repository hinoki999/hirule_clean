from dataclasses import dataclass
from datetime import datetime

@dataclass
class PositionMetrics:
    asset: str
    current_price: float
    size: float
    timestamp: datetime

class MetricsCalculator:
    def __init__(self):
        pass
