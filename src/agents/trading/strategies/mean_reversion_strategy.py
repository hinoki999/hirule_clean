from typing import Dict, Optional
import numpy as np
from src.agents.trading.strategies.base_trading_strategy import BaseTradingStrategy, TradingStrategyError

class MeanReversionStrategy(BaseTradingStrategy):
    def __init__(self, config: Dict):
        super().__init__(config)
        self.lookback_period = config.get("lookback_period", 20)
        self.entry_std = config.get("entry_std", 2.0)
        self.exit_std = config.get("exit_std", 0.5)
        self.price_history = {}

    def _validate_config(self, config: Dict) -> None:
        super()._validate_config(config)
        if config.get("lookback_period", 20) < 2:
            raise TradingStrategyError("Lookback period must be at least 2")

    async def _generate_signal(self, market_data: Dict) -> Optional[Dict]:
        symbol = market_data["symbol"]
        price = float(market_data["last_price"])
        
        if symbol not in self.price_history:
            self.price_history[symbol] = []
        
        self.price_history[symbol].append(price)
        self.price_history[symbol] = self.price_history[symbol][-self.lookback_period:]
        
        if len(self.price_history[symbol]) < self.lookback_period:
            return None
            
        mean = np.mean(self.price_history[symbol])
        std = np.std(self.price_history[symbol])
        z_score = (price - mean) / std
        
        current_position = self.positions.get(symbol, {"size": 0})["size"]
        
        if abs(z_score) > self.entry_std and current_position == 0:
            return {
                "symbol": symbol,
                "type": "market",
                "side": "sell" if z_score > 0 else "buy",
                "size": self.position_limits[symbol]["max_position"]
            }
        elif abs(z_score) < self.exit_std and current_position != 0:
            return {
                "symbol": symbol,
                "type": "market",
                "side": "buy" if current_position < 0 else "sell",
                "size": abs(current_position)
            }
            
        return None

    async def _create_order(self, signal: Dict) -> Dict:
        try:
            order = await self.exchange.create_order(
                symbol=signal["symbol"],
                type=signal["type"],
                side=signal["side"],
                amount=signal["size"]
            )
            return order
        except Exception as e:
            self.logger.error(f"Order creation failed: {str(e)}")
            raise TradingStrategyError(f"Order creation failed: {str(e)}")
