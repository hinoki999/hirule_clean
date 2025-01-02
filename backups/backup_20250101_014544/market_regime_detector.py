from typing import Dict, Optional, Union, List
from dataclasses import dataclass
from decimal import Decimal
import logging
import numpy as np
from src.agents.base import BaseAgent
from src.agents.capability import Capability
from src.communication.message_bus import MessageBus

@dataclass
class MarketData:
    """Validated market data structure"""
    symbol: str
    price: float
    volume: float
    timestamp: str

# Define exceptions hierarchy
class MarketRegimeError(Exception):
    """Base exception for market regime detector"""
    pass

class MessageBusError(MarketRegimeError):
    """Raised when message bus operations fail"""
    pass

class InvalidMarketDataError(MarketRegimeError):
    """Raised when market data is invalid"""
    pass

# Define market regime types
MARKET_REGIMES = {
    "normal": "normal",
    "trending": "trending",
    "high_volatility": "high_volatility",
    "low_volume": "low_volume"
}

class MarketRegimeDetector(BaseAgent):
    """Agent for detecting market regimes based on price and volume data"""
    
    def __init__(self, config: Dict):
        # First validate config before calling super().__init__
        self._validate_config(config)
        super().__init__(config)
        
        # Configuration
        self.volatility_window = config["volatility_window"]
        self.volume_window = config["volume_window"]
        self.price_change_threshold = config["price_change_threshold"]
        self.volume_change_threshold = config["volume_change_threshold"]
        
        # State
        self.price_history: Dict[str, List[float]] = {}
        self.volume_history: Dict[str, List[float]] = {}
        
        # Register capability
        self.capabilities = [Capability.ANOMALY_DETECTION]
        
        # Set up logging
        self.logger = logging.getLogger(__name__)

    def _validate_config(self, config: Dict) -> None:
        """Validate configuration parameters"""
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
                    raise MarketRegimeError(f"Invalid type for {param}. Expected {param_type}")
                if not validator(value):
                    raise MarketRegimeError(f"Invalid value for {param}")
            except (TypeError, ValueError) as e:
                raise MarketRegimeError(f"Validation failed for {param}: {str(e)}")

    def _validate_market_data(self, data: Dict) -> MarketData:
        """Validate incoming market data"""
        try:
            # Validate required fields
            required_fields = ["symbol", "last_price", "volume", "timestamp"]
            if not all(field in data for field in required_fields):
                raise InvalidMarketDataError(f"Missing required fields. Required: {required_fields}")
                
            # Convert and validate price
            try:
                price = float(data["last_price"])
                if price <= 0:
                    raise InvalidMarketDataError("Price must be positive")
            except ValueError:
                raise InvalidMarketDataError("Invalid price format")
                
            # Convert and validate volume
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
        except InvalidMarketDataError:
            raise
        except Exception as e:
            self.logger.error(f"Market data validation failed: {str(e)}")
            raise InvalidMarketDataError(f"Market data validation failed: {str(e)}")

    async def setup(self):
        """Setup message handlers"""
        try:
            await self.message_bus.subscribe("market_data", self._handle_market_data)
            await self.message_bus.subscribe("regime_request", self._handle_regime_request)
        except Exception as e:
            self.logger.error(f"Failed to setup message handlers: {str(e)}")
            raise MessageBusError(f"Setup failed: {str(e)}")

    async def _handle_market_data(self, message: Dict):
        """Handle incoming market data updates"""
        try:
            validated_data = self._validate_market_data(message)
            await self._update_history(validated_data.symbol, validated_data.price, validated_data.volume)
            regime = self._detect_regime(validated_data.symbol)
            
            try:
                await self.publish("regime_update", {
                    "symbol": validated_data.symbol,
                    "regime": regime,
                    "timestamp": validated_data.timestamp
                })
            except Exception as e:
                self.logger.error(f"Message bus publish failed: {str(e)}")
                raise MessageBusError(f"Failed to publish regime update: {str(e)}")
                
        except (InvalidMarketDataError, MessageBusError):
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error in market data handling: {str(e)}")
            raise MarketRegimeError(f"Unexpected error in market data handling: {str(e)}")

    async def _handle_regime_request(self, message: Dict):
        """Handle direct regime detection requests"""
        validated_data = self._validate_market_data(message)
        await self._update_history(validated_data.symbol, validated_data.price, validated_data.volume)
        regime = self._detect_regime(validated_data.symbol)
        return {
            "symbol": validated_data.symbol,
            "regime": regime
        }

    async def _update_history(self, symbol: str, price: float, volume: float):
        """Update price and volume history"""
        if symbol not in self.price_history:
            self.price_history[symbol] = []
            self.volume_history[symbol] = []
            
        self.price_history[symbol].append(price)
        self.volume_history[symbol].append(volume)
        
        # Keep only window size
        self.price_history[symbol] = self.price_history[symbol][-self.volatility_window:]
        self.volume_history[symbol] = self.volume_history[symbol][-self.volume_window:]

    def _detect_regime(self, symbol: str) -> str:
        """Detect current market regime"""
        if len(self.price_history[symbol]) < self.volatility_window:
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
        """Calculate price volatility"""
        prices = np.array(self.price_history[symbol])
        returns = np.diff(prices) / prices[:-1]
        return float(np.std(returns))

    def _calculate_volume_change(self, symbol: str) -> float:
        """Calculate volume change"""
        volumes = np.array(self.volume_history[symbol])
        if len(volumes) < 2:
            return 0.0
        return float((volumes[-1] - volumes[0]) / volumes[0])

    def _calculate_trend(self, symbol: str) -> float:
        """Calculate price trend"""
        prices = np.array(self.price_history[symbol])
        return float((prices[-1] - prices[0]) / prices[0])
