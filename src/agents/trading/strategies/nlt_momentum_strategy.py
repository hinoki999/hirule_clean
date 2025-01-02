from typing import Dict, Optional, List
import numpy as np
from decimal import Decimal
from ...core.message_bus import MessageBus
from ...core.capabilities import Capability
from ..base_agent import BaseAgent

class MomentumTradingCapability(Capability):
    """Defines the momentum trading capability"""
    name = "momentum_trading"
    version = "1.0.0"
    
    def __init__(self):
        super().__init__()
        self.required_capabilities = ["market_data", "order_management"]

class NLTMomentumStrategy(BaseAgent):
    def __init__(self, config: Dict):
        super().__init__(config)
        self.lookback_period = config.get("lookback_period", 20)
        self.price_history: Dict[str, List[float]] = {}
        
        # Register capabilities
        self.register_capability(MomentumTradingCapability())
        
        # Set up message handlers
        self.message_bus.subscribe("market_data", self._handle_market_data)
        self.message_bus.subscribe("system_status", self._handle_system_status)
    
    async def _handle_market_data(self, message: Dict):
        """Handle incoming market data messages"""
        symbol = message.get("symbol")
        price = float(message.get("last_price", 0))
        volume = float(message.get("volume", 0))
        
        signal = await self._analyze_market(symbol, price, volume)
        if signal:
            await self.message_bus.publish("trade_signal", signal)
    
    async def _handle_system_status(self, message: Dict):
        """Handle system status messages"""
        # Implement system monitoring
        pass
    
    async def _analyze_market(self, symbol: str, price: float, volume: float) -> Optional[Dict]:
        """Internal market analysis logic"""
        if symbol not in self.price_history:
            self.price_history[symbol] = []
            
        self.price_history[symbol].append(price)
        self.price_history[symbol] = self.price_history[symbol][-self.lookback_period:]
        
        if len(self.price_history[symbol]) < self.lookback_period:
            return None
            
        momentum = self._calculate_momentum(symbol)
        
        # Get market regime through message bus
        regime_request = {"symbol": symbol, "price": price, "volume": volume}
        regime = await self.message_bus.request("market_regime", regime_request)
        
        return self._generate_signal(symbol, momentum, regime)
