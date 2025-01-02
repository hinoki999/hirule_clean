from typing import Dict, Optional
import numpy as np
from src.agents.trading.strategies.base_trading_strategy import BaseTradingStrategy, TradingStrategyError

class MarketMakingStrategy(BaseTradingStrategy):
    def __init__(self, config: Dict):
        super().__init__(config)
        self.spread = config.get("spread", 0.002)
        self.order_size = config.get("order_size", 0.1)
        self.depth = config.get("depth", 3)
        self.min_profit = config.get("min_profit", 0.001)
        self.orderbook = {}

    async def _generate_signal(self, market_data: Dict) -> Optional[Dict]:
        symbol = market_data["symbol"]
        self.orderbook[symbol] = {
            "bids": market_data.get("bids", []),
            "asks": market_data.get("asks", [])
        }
        
        mid_price = (float(market_data["bids"][0][0]) + float(market_data["asks"][0][0])) / 2
        spread = float(market_data["asks"][0][0]) - float(market_data["bids"][0][0])
        
        if spread > self.spread * mid_price:
            return {
                "symbol": symbol,
                "type": "limit",
                "orders": [
                    {
                        "side": "buy",
                        "price": mid_price * (1 - self.spread/2),
                        "size": self.order_size
                    },
                    {
                        "side": "sell",
                        "price": mid_price * (1 + self.spread/2),
                        "size": self.order_size
                    }
                ]
            }
        return None

    async def _create_order(self, signal: Dict) -> Dict:
        try:
            orders = []
            for order in signal["orders"]:
                executed_order = await self.exchange.create_order(
                    symbol=signal["symbol"],
                    type="limit",
                    side=order["side"],
                    amount=order["size"],
                    price=order["price"]
                )
                orders.append(executed_order)
            return {"orders": orders}
        except Exception as e:
            self.logger.error(f"Order creation failed: {str(e)}")
            raise TradingStrategyError(f"Order creation failed: {str(e)}")
