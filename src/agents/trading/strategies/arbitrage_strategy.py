from typing import Dict, Optional, List
import numpy as np
import ccxt
from src.agents.trading.strategies.base_trading_strategy import BaseTradingStrategy, TradingStrategyError

class ArbitrageStrategy(BaseTradingStrategy):
    def __init__(self, config: Dict):
        super().__init__(config)
        self.min_spread = config.get("min_spread", 0.001)  # 0.1% minimum spread
        self.execution_delay = config.get("execution_delay", 0.1)  # 100ms default
        self.max_position_value = config.get("max_position_value", 100000)
        self.exchanges = self._initialize_exchanges(config)

    def _initialize_exchanges(self, config: Dict) -> Dict:
        try:
            exchange_configs = config.get("exchanges", [])
            if not exchange_configs:
                raise TradingStrategyError("No exchanges configured")
                
            exchanges = {}
            for ex_config in exchange_configs:
                exchange_id = ex_config["id"]
                exchange_class = getattr(ccxt, exchange_id)
                exchanges[exchange_id] = exchange_class({
                    "apiKey": ex_config["api_key"],
                    "secret": ex_config["api_secret"],
                    "enableRateLimit": True,
                    "options": ex_config.get("options", {})
                })
            return exchanges
        except Exception as e:
            raise TradingStrategyError(f"Failed to initialize exchanges: {str(e)}")

    async def _generate_signal(self, market_data: Dict) -> Optional[Dict]:
        try:
            symbol = market_data["symbol"]
            opportunities = await self._find_opportunities(symbol)
            
            if not opportunities:
                return None
                
            best_opportunity = max(opportunities, 
                                 key=lambda x: x["expected_profit"])
                                 
            if best_opportunity["expected_profit"] > self.min_spread:
                return {
                    "type": "arbitrage",
                    "symbol": symbol,
                    "buy_exchange": best_opportunity["buy_exchange"],
                    "sell_exchange": best_opportunity["sell_exchange"],
                    "buy_price": best_opportunity["buy_price"],
                    "sell_price": best_opportunity["sell_price"],
                    "size": best_opportunity["size"]
                }
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error generating arbitrage signal: {str(e)}")
            raise

    async def _find_opportunities(self, symbol: str) -> List[Dict]:
        opportunities = []
        exchanges = list(self.exchanges.keys())
        
        orderbooks = {}
        for exchange_id in exchanges:
            try:
                orderbook = await self.exchanges[exchange_id].fetch_order_book(symbol)
                orderbooks[exchange_id] = {
                    "bids": orderbook["bids"],
                    "asks": orderbook["asks"]
                }
            except Exception as e:
                self.logger.warning(f"Failed to fetch orderbook from {exchange_id}: {str(e)}")
                continue
        
        for i, ex1 in enumerate(exchanges):
            for j, ex2 in enumerate(exchanges[i+1:], i+1):
                if ex1 not in orderbooks or ex2 not in orderbooks:
                    continue
                    
                buy_price = orderbooks[ex1]["asks"][0][0]
                sell_price = orderbooks[ex2]["bids"][0][0]
                
                if sell_price > buy_price:
                    size = min(
                        orderbooks[ex1]["asks"][0][1],
                        orderbooks[ex2]["bids"][0][1],
                        self.max_position_value / buy_price
                    )
                    
                    opportunities.append({
                        "buy_exchange": ex1,
                        "sell_exchange": ex2,
                        "buy_price": buy_price,
                        "sell_price": sell_price,
                        "size": size,
                        "expected_profit": (sell_price - buy_price) * size
                    })
                
                # Check reverse direction
                buy_price = orderbooks[ex2]["asks"][0][0]
                sell_price = orderbooks[ex1]["bids"][0][0]
                
                if sell_price > buy_price:
                    size = min(
                        orderbooks[ex2]["asks"][0][1],
                        orderbooks[ex1]["bids"][0][1],
                        self.max_position_value / buy_price
                    )
                    
                    opportunities.append({
                        "buy_exchange": ex2,
                        "sell_exchange": ex1,
                        "buy_price": buy_price,
                        "sell_price": sell_price,
                        "size": size,
                        "expected_profit": (sell_price - buy_price) * size
                    })
        
        return opportunities

    async def _create_order(self, signal: Dict) -> Dict:
        try:
            orders = []
            
            # Place buy order
            buy_order = await self.exchanges[signal["buy_exchange"]].create_order(
                symbol=signal["symbol"],
                type="limit",
                side="buy",
                amount=signal["size"],
                price=signal["buy_price"]
            )
            orders.append(buy_order)
            
            # Place sell order
            sell_order = await self.exchanges[signal["sell_exchange"]].create_order(
                symbol=signal["symbol"],
                type="limit",
                side="sell",
                amount=signal["size"],
                price=signal["sell_price"]
            )
            orders.append(sell_order)
            
            return {"orders": orders}
            
        except Exception as e:
            self.logger.error(f"Arbitrage order creation failed: {str(e)}")
            raise TradingStrategyError(f"Arbitrage order creation failed: {str(e)}")
