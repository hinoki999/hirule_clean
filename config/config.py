class Config:
    def __init__(self):
        # Initialize basic configuration
        self.thresholds = {
            "min_order_size": "0.0001",
            "max_order_size": "1.0",
            "min_price_increment": "0.01",
            "min_notional": "10.0"
        }
        self.trading = {
            "momentum_window": 20,
            "momentum_threshold": 0.02,
            "vol_window": 20,
            "trend_window": 14,
            "min_trend_strength": 0.05
        }
        self.risk = {
            "max_position_size": "1.0",
            "max_notional": "100000",
            "max_drawdown": 0.1
        }
