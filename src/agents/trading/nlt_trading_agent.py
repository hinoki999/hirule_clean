from decimal import Decimal
from typing import Dict, List
from .base_trading_agent import BaseTradingAgent
from .messages import TradingMessageTypes

class ThresholdConfig:
    def __init__(self, config: Dict):
        self.config = config

class TradingConfig:
    def __init__(self, 
                 min_trade_size: str,
                 max_position_size: str,
                 risk_per_trade: str,
                 slippage_tolerance: str,
                 threshold_config: Dict):
        self.min_trade_size = min_trade_size
        self.max_position_size = max_position_size
        self.risk_per_trade = risk_per_trade
        self.slippage_tolerance = slippage_tolerance
        self.thresholds = ThresholdConfig(threshold_config)

class NLTTradingAgent(BaseTradingAgent):
    """Trading agent specialized for NLT token operations"""
    
    def __init__(self, config: Dict, exchange_pairs: List[str], **kwargs):
        # Convert dict config to object
        trading_config = TradingConfig(
            min_trade_size=config["min_trade_size"],
            max_position_size=config["max_position_size"],
            risk_per_trade=config["risk_per_trade"],
            slippage_tolerance=config["slippage_tolerance"],
            threshold_config=config["thresholds"]["config"]
        )
        super().__init__(trading_config, **kwargs)
        self.exchange_pairs = exchange_pairs
        self.nlt_specific_thresholds = {}
