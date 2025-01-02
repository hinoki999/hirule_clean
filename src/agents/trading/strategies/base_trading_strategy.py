from typing import Dict, Optional
import logging

class TradingStrategyError(Exception):
    pass

class BaseTradingStrategy:
    def __init__(self, config: Dict):
        self.config = config
        self._validate_config(config)
        self.logger = logging.getLogger(self.__class__.__name__)

    def _validate_config(self, config: Dict) -> None:
        # Check for either single exchange config or multiple exchanges
        if "exchanges" not in config and not all(field in config for field in ["exchange", "api_key", "api_secret"]):
            raise TradingStrategyError("Missing required configuration fields. Need either 'exchanges' list or single exchange config.")
        
        # If using multiple exchanges, validate each one
        if "exchanges" in config:
            for exchange_config in config["exchanges"]:
                if not all(field in exchange_config for field in ["id", "api_key", "api_secret"]):
                    raise TradingStrategyError(f"Invalid exchange configuration: {exchange_config}")

    async def _generate_signal(self, market_data: Dict) -> Optional[Dict]:
        raise NotImplementedError("_generate_signal must be implemented by subclass")

    async def _create_order(self, signal: Dict) -> Dict:
        raise NotImplementedError("_create_order must be implemented by subclass")
