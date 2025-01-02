from typing import Dict, Optional, List
import numpy as np
from src.agents.trading.strategies.base_trading_strategy import BaseTradingStrategy, TradingStrategyError
from src.agents.trading.strategies.market_making_strategy import MarketMakingStrategy
from src.agents.trading.strategies.arbitrage_strategy import ArbitrageStrategy

class NLTTradingStrategy(BaseTradingStrategy):
    def __init__(self, config: Dict):
        super().__init__(config)
        self.market_maker = MarketMakingStrategy(config)
        self.arbitrage = ArbitrageStrategy(config)
        self.min_profit = config.get("min_profit", 0.001)
        self.max_slippage = config.get("max_slippage", 0.002)
        self.treasury_threshold = config.get("treasury_threshold", 1000000)

    async def _generate_signal(self, market_data: Dict) -> Optional[Dict]:
        try:
            # Get signals from each sub-strategy
            arb_signal = await self.arbitrage._generate_signal(market_data)
            mm_signal = await self.market_maker._generate_signal(market_data)
            
            # Get treasury data
            treasury_balance = await self._get_treasury_balance()
            
            if treasury_balance < self.treasury_threshold:
                return self._generate_conservative_signal(market_data, mm_signal, arb_signal)
            else:
                return self._generate_normal_signal(market_data, mm_signal, arb_signal)
                
        except Exception as e:
            self.logger.error(f"Error generating NLT trading signal: {str(e)}")
            raise TradingStrategyError(f"Failed to generate NLT trading signal: {str(e)}")

    async def _get_treasury_balance(self) -> int:
        try:
            response = await self.message_bus.request(
                "token_operation",
                {
                    "operation": "balance",
                    "address": self.config["treasury_address"]
                }
            )
            return response["balance"]
        except Exception as e:
            self.logger.error(f"Error getting treasury balance: {str(e)}")
            raise TradingStrategyError(f"Failed to get treasury balance: {str(e)}")

    def _generate_conservative_signal(
        self,
        market_data: Dict,
        mm_signal: Optional[Dict],
        arb_signal: Optional[Dict]
    ) -> Optional[Dict]:
        """Conservative strategy when treasury is below threshold"""
        if arb_signal and arb_signal["expected_profit"] > self.min_profit * 2:
            return {
                "type": "arbitrage",
                "priority": "high",
                "data": arb_signal
            }
        
        if mm_signal and mm_signal["side"] == "buy" and mm_signal["confidence"] > 0.8:
            return {
                "type": "market_making",
                "priority": "medium",
                "data": mm_signal
            }
            
        return None

    def _generate_normal_signal(
        self,
        market_data: Dict,
        mm_signal: Optional[Dict],
        arb_signal: Optional[Dict]
    ) -> Optional[Dict]:
        """Normal strategy when treasury is healthy"""
        signals = []
        
        if arb_signal and arb_signal["expected_profit"] > self.min_profit:
            signals.append({
                "type": "arbitrage",
                "priority": "medium",
                "data": arb_signal,
                "score": arb_signal["expected_profit"]
            })
            
        if mm_signal and mm_signal["confidence"] > 0.6:
            signals.append({
                "type": "market_making",
                "priority": "low",
                "data": mm_signal,
                "score": mm_signal["confidence"]
            })
            
        if not signals:
            return None
            
        return max(signals, key=lambda x: x["score"])
