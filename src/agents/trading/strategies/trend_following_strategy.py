from typing import Dict, Optional
import numpy as np
from src.agents.trading.strategies.base_trading_strategy import BaseTradingStrategy, TradingStrategyError

class TrendFollowingStrategy(BaseTradingStrategy):
    def __init__(self, config: Dict):
        super().__init__(config)
        self.short_period = config.get("short_period", 10)
        self.long_period = config.get("long_period", 20)
        self.price_history = {}
        
    def _validate_config(self, config: Dict) -> None:
        super()._validate_config(config)
        if config.get("short_period", 10) >= config.get("long_period", 20):
            raise TradingStrategyError("Short period must be less than long period")

    def calculate_ema(self, data: list, period: int) -> float:
        return np.average(data[-period:], 
                         weights=[1 + i for i in range(period)])

    async def _generate_signal(self, market_data: Dict) -> Optional[Dict]:
        symbol = market_data["symbol"]
        price = float(market_data["last_price"])
        
        if symbol not in self.price_history:
            self.price_history[symbol] = []
            
        self.price_history[symbol].append(price)
        
        if len(self.price_history[symbol]) < self.long_period:
            return None
            
        short_ema = self.calculate_ema(self.price_history[symbol], self.short_period)
        long_ema = self.calculate_ema(self.price_history[symbol], self.long_period)
        
        current_position = self.positions.get(symbol, {"size": 0})["size"]
        
        if short_ema > long_ema and current_position <= 0:
            return {
                "symbol": symbol,
                "type": "market",
                "side": "buy",
                "size": self.position_limits[symbol]["max_position"]
            }
        elif short_ema < long_ema and current_position >= 0:
            return {
                "symbol": symbol,
                "type": "market",
                "side": "sell",
                "size": self.position_limits[symbol]["max_position"]
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
