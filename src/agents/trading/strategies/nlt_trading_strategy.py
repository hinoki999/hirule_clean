from typing import Dict, Optional, List
import logging
from src.agents.trading.strategies.base_trading_strategy import BaseTradingStrategy, TradingStrategyError
from src.agents.trading.strategies.market_making_strategy import MarketMakingStrategy
from src.agents.trading.strategies.arbitrage_strategy import ArbitrageStrategy
from src.agents.risk.risk_manager import RiskManager, Position

class NLTTradingStrategy(BaseTradingStrategy):
    def __init__(self, config: Dict):
        super().__init__(config)
        self.market_maker = MarketMakingStrategy(config)
        self.arbitrage = ArbitrageStrategy(config)
        self.min_profit = config.get("min_profit", 0.001)
        self.max_slippage = config.get("max_slippage", 0.002)
        self.treasury_threshold = config.get("treasury_threshold", 1000000)
        self.logger = logging.getLogger(__name__)
        
        # Initialize risk manager with risk config
        risk_config = {
            "max_position_size": config.get("max_position_size", 1000000),
            "max_total_exposure": config.get("max_total_exposure", 5000000),
            "risk_per_trade": config.get("risk_per_trade", 0.02),
            "max_drawdown": config.get("max_drawdown", 0.15),
            "var_limit": config.get("var_limit", 500000),
            "position_timeout": config.get("position_timeout", 24)
        }
        self.risk_manager = RiskManager(risk_config)

    def _generate_conservative_signal(
        self,
        market_data: Dict,
        mm_signal: Optional[Dict],
        arb_signal: Optional[Dict]
    ) -> Optional[Dict]:
        """Conservative strategy when treasury is below threshold"""
        if arb_signal and arb_signal.get("expected_profit", 0) > self.min_profit * 2:
            self.logger.debug(f"Found profitable arbitrage: {arb_signal['expected_profit']}")
            return {
                "type": "arbitrage",
                "priority": "high",
                "data": arb_signal
            }
        
        if mm_signal and mm_signal.get("side") == "buy" and mm_signal.get("confidence", 0) > 0.8:
            self.logger.debug("Found high-confidence market making opportunity")
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
        
        if arb_signal and arb_signal.get("expected_profit", 0) > self.min_profit:
            signals.append({
                "type": "arbitrage",
                "priority": "medium",
                "data": arb_signal,
                "score": arb_signal["expected_profit"]
            })
            
        if mm_signal and mm_signal.get("confidence", 0) > 0.6:
            signals.append({
                "type": "market_making",
                "priority": "low",
                "data": mm_signal,
                "score": mm_signal["confidence"]
            })
            
        if not signals:
            return None
            
        return max(signals, key=lambda x: x["score"])

    async def _generate_signal(self, market_data: Dict) -> Optional[Dict]:
        try:
            # Get signals from each sub-strategy
            arb_signal = await self.arbitrage._generate_signal(market_data)
            mm_signal = await self.market_maker._generate_signal(market_data)
            
            # Get treasury data
            treasury_balance = await self._get_treasury_balance()
            
            # Get initial trading signal
            if treasury_balance < self.treasury_threshold:
                signal = self._generate_conservative_signal(market_data, mm_signal, arb_signal)
            else:
                signal = self._generate_normal_signal(market_data, mm_signal, arb_signal)
                
            if not signal:
                return None
                
            # Convert trading signal to risk proposal
            trade_proposal = await self._create_risk_proposal(signal, market_data)
            
            # Check risk limits
            risk_check = await self.risk_manager.check_risk_limits(trade_proposal)
            
            if not risk_check["approved"]:
                self.logger.warning(f"Trade rejected by risk manager: {risk_check['message']}")
                return None
                
            # Adjust signal with risk-approved size
            adjusted_signal = signal.copy()
            adjusted_signal["size"] = risk_check["adjusted_size"]
            adjusted_signal["risk_metrics"] = risk_check["risk_metrics"]
            
            return adjusted_signal
                
        except Exception as e:
            self.logger.error(f"Error generating NLT trading signal: {str(e)}")
            raise TradingStrategyError(f"Failed to generate NLT trading signal: {str(e)}")

    async def _create_risk_proposal(self, signal: Dict, market_data: Dict) -> Dict:
        """Convert trading signal to risk proposal format."""
        try:
            asset = market_data["symbol"]
            price_data = market_data["exchanges"][signal["data"].get("exchange", list(market_data["exchanges"].keys())[0])]
            
            proposal = {
                "asset": asset,
                "size": signal["data"].get("size", 0),
                "entry_price": price_data.get("ask" if signal["type"] == "buy" else "bid", 0),
            }
            
            # Calculate stop loss and take profit levels
            if signal["type"] == "arbitrage":
                # For arbitrage, use the profit threshold as the stop distance
                stop_distance = self.min_profit
                profit_distance = signal["data"]["expected_profit"]
            else:
                # For market making, use volatility-based stops
                volatility = self._calculate_volatility(market_data)
                stop_distance = max(volatility * 2, self.min_profit)
                profit_distance = stop_distance * 1.5
            
            proposal["stop_loss"] = proposal["entry_price"] * (1 - stop_distance)
            proposal["take_profit"] = proposal["entry_price"] * (1 + profit_distance)
            
            return proposal
            
        except Exception as e:
            self.logger.error(f"Error creating risk proposal: {str(e)}")
            raise TradingStrategyError(f"Failed to create risk proposal: {str(e)}")

    def _calculate_volatility(self, market_data: Dict) -> float:
        """Calculate recent price volatility."""
        try:
            # Implementation depends on available historical data
            return self.max_slippage  # Fallback to max slippage if no historical data
        except Exception as e:
            self.logger.error(f"Error calculating volatility: {str(e)}")
            return self.max_slippage

    async def execute_signal(self, signal: Dict) -> None:
        """Execute trading signal with position tracking."""
        try:
            # Execute the trade
            order_result = await self._create_order(signal)
            
            if order_result.get("status") == "filled":
                # Create position object for tracking
                position = Position(
                    asset=signal["asset"],
                    size=signal["size"],
                    entry_price=order_result["fill_price"],
                    current_price=order_result["fill_price"],
                    timestamp=order_result["timestamp"],
                    stop_loss=signal.get("stop_loss"),
                    take_profit=signal.get("take_profit")
                )
                
                # Add to risk manager's tracked positions
                self.risk_manager.positions[signal["asset"]] = position
                
                # Publish position update
                await self.message_bus.publish(
                    "position_update",
                    {
                        "type": "new_position",
                        "position": position.__dict__,
                        "risk_metrics": signal["risk_metrics"].__dict__
                    }
                )
                
        except Exception as e:
            self.logger.error(f"Error executing signal: {str(e)}")
            raise TradingStrategyError(f"Failed to execute signal: {str(e)}")

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
