from typing import Dict, Optional, Union, List
from dataclasses import dataclass
import logging
import numpy as np
import time
from src.agents.base import BaseAgent
from src.agents.capability import Capability
from src.communication.message_bus import MessageBus

@dataclass
class MarketData:
    symbol: str
    price: float
    volume: float
    timestamp: str

@dataclass
class SymbolData:
    last_update: float
    price_history: List[float]
    volume_history: List[float]

class MarketRegimeError(Exception):
    pass

class MessageBusError(MarketRegimeError):
    pass

class InvalidMarketDataError(MarketRegimeError):
    pass

MARKET_REGIMES = {
    "normal": "normal",
    "trending": "trending",
    "high_volatility": "high_volatility",
    "low_volume": "low_volume"
}

class MarketRegimeDetector(BaseAgent):
    def __init__(self, config: Dict):
        self._validate_config(config)
        super().__init__(config)
        
        self.volatility_window = config["volatility_window"]
        self.volume_window = config["volume_window"]
        self.price_change_threshold = config["price_change_threshold"]
        self.volume_change_threshold = config["volume_change_threshold"]
        
        self.max_symbols = config.get("max_symbols", 1000)
        self.cleanup_interval = config.get("cleanup_interval", 3600)
        self.symbol_timeout = config.get("symbol_timeout", 86400)
        
        self.symbols: Dict[str, SymbolData] = {}
        self.last_cleanup = time.time()
        
        self.capabilities = [Capability.ANOMALY_DETECTION]
        self.logger = logging.getLogger(__name__)

    def _validate_market_data(self, data: Dict) -> MarketData:
        try:
            required_fields = ["symbol", "last_price", "volume", "timestamp"]
            if not all(field in data for field in required_fields):
                raise InvalidMarketDataError("Missing required fields")
                
            try:
                price = float(data["last_price"])
                if price <= 0:
                    raise InvalidMarketDataError("Price must be positive")
            except ValueError:
                raise InvalidMarketDataError("Invalid price format")
                
            try:
                volume = float(data["volume"])
                if volume < 0:
                    raise InvalidMarketDataError("Volume cannot be negative")
            except ValueError:
                raise InvalidMarketDataError("Invalid volume format")
                
            return MarketData(
                symbol=str(data["symbol"]),
                price=price,
                volume=volume,
                timestamp=str(data["timestamp"])
            )
        except Exception as e:
            raise InvalidMarketDataError(f"Market data validation failed: {str(e)}")

    async def _cleanup_old_data(self):
        if self.symbol_timeout == 0:
            self.symbols.clear()
            return
            
        current_time = time.time()
        symbols_to_remove = [
            symbol for symbol, data in self.symbols.items()
            if current_time - data.last_update >= self.symbol_timeout
        ]
        
        for symbol in symbols_to_remove:
            del self.symbols[symbol]

    async def _update_history(self, symbol: str, price: float, volume: float):
        current_time = time.time()
        
        if symbol not in self.symbols:
            if len(self.symbols) >= self.max_symbols:
                raise MarketRegimeError("Maximum number of tracked symbols reached")
            self.symbols[symbol] = SymbolData(
                last_update=current_time,
                price_history=[],
                volume_history=[]
            )
        
        symbol_data = self.symbols[symbol]
        symbol_data.last_update = current_time
        symbol_data.price_history.append(price)
        symbol_data.volume_history.append(volume)
        symbol_data.price_history = symbol_data.price_history[-self.volatility_window:]
        symbol_data.volume_history = symbol_data.volume_history[-self.volume_window:]

    def _detect_regime(self, symbol: str) -> str:
        symbol_data = self.symbols[symbol]
        if len(symbol_data.price_history) < self.volatility_window:
            return MARKET_REGIMES["normal"]
            
        volatility = self._calculate_volatility(symbol)
        volume_change = self._calculate_volume_change(symbol)
        trend = self._calculate_trend(symbol)
        
        if volatility > self.price_change_threshold:
            return MARKET_REGIMES["high_volatility"]
        elif volume_change < -self.volume_change_threshold:
            return MARKET_REGIMES["low_volume"]
        elif abs(trend) > self.price_change_threshold:
            return MARKET_REGIMES["trending"]
        else:
            return MARKET_REGIMES["normal"]

    def _calculate_volatility(self, symbol: str) -> float:
        prices = np.array(self.symbols[symbol].price_history)
        returns = np.diff(prices) / prices[:-1]
        return float(np.std(returns))

    def _calculate_volume_change(self, symbol: str) -> float:
        volumes = np.array(self.symbols[symbol].volume_history)
        if len(volumes) < 2:
            return 0.0
        return float((volumes[-1] - volumes[0]) / volumes[0])

    def _calculate_trend(self, symbol: str) -> float:
        prices = np.array(self.symbols[symbol].price_history)
        return float((prices[-1] - prices[0]) / prices[0])

    async def setup(self):
        try:
            await self.message_bus.subscribe("market_data", self._handle_market_data)
        except Exception as e:
            raise MessageBusError(f"Setup failed: {str(e)}")

    async def _handle_market_data(self, message: Dict):
        try:
            validated_data = self._validate_market_data(message)
            await self._update_history(validated_data.symbol, validated_data.price, validated_data.volume)
            regime = self._detect_regime(validated_data.symbol)
            
            await self.publish("regime_update", {
                "symbol": validated_data.symbol,
                "regime": regime,
                "timestamp": validated_data.timestamp
            })
                
        except Exception as e:
            self.logger.error(f"Error handling market data: {str(e)}")
            raise

    def _validate_config(self, config: Dict) -> None:
        required_params = {
            "volatility_window": (int, lambda x: x > 0),
            "volume_window": (int, lambda x: x > 0),
            "price_change_threshold": (float, lambda x: 0 < x < 1),
            "volume_change_threshold": (float, lambda x: 0 < x < 1)
        }
        
        for param, (param_type, validator) in required_params.items():
            if param not in config:
                raise MarketRegimeError(f"Missing required parameter: {param}")
            try:
                value = config[param]
                if not isinstance(value, param_type):
                    raise MarketRegimeError(f"Invalid type for {param}")
                if not validator(value):
                    raise MarketRegimeError(f"Invalid value for {param}")
            except (TypeError, ValueError) as e:
                raise MarketRegimeError(f"Validation failed for {param}: {str(e)}")
