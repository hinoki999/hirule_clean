from typing import Dict, Any, Optional
from datetime import datetime
from .base_agent import BaseAgent
from ..core.message_bus import MessageType, AgentMessage, MessageBus
from trading_system import TradingSystem

class TradingAgent(BaseAgent):
    def __init__(self, agent_id: str, message_bus: MessageBus, trading_system: TradingSystem):
        super().__init__(agent_id, message_bus)
        self.trading_system = trading_system
        self.active_trades: Dict[str, Dict] = {}
        
        # Subscribe to relevant message types
        self.message_bus.subscribe(MessageType.MARKET_DATA, self.handle_market_data)
        self.message_bus.subscribe(MessageType.TRADE_SIGNAL, self.handle_trade_signal)
        self.message_bus.subscribe(MessageType.ORDER_UPDATE, self.handle_order_update)
        
    async def handle_market_data(self, message: AgentMessage):
        """Process incoming market data"""
        await self.process_market_data(message.data)
        
    async def handle_trade_signal(self, message: AgentMessage):
        """Process incoming trade signals"""
        await self.evaluate_trade_signal(message.data)
        
    async def handle_order_update(self, message: AgentMessage):
        """Process order updates"""
        await self.update_trade_status(message.data)
        
    async def process_market_data(self, data: Dict):
        """Process and analyze market data"""
        # Implement market data processing logic
        analysis_result = await self.analyze_market_data(data)
        if analysis_result.get("generate_signal", False):
            await self.generate_trading_signals(analysis_result)
            
    async def analyze_market_data(self, data: Dict) -> Dict:
        """Analyze market data for trading opportunities"""
        # Implement market analysis logic
        return {"generate_signal": False}
        
    async def generate_trading_signals(self, analysis: Dict):
        """Generate trading signals based on analysis"""
        signal = {
            "timestamp": datetime.now(),
            "asset": analysis.get("asset"),
            "action": analysis.get("recommended_action"),
            "confidence": analysis.get("confidence", 0.0)
        }
        await self.send_message(MessageType.TRADE_SIGNAL, signal)
        
    async def evaluate_trade_signal(self, signal: Dict):
        """Evaluate and potentially act on trade signals"""
        if self.validate_signal(signal):
            await self.execute_trade(signal)
            
    def validate_signal(self, signal: Dict) -> bool:
        """Validate trading signals"""
        # Implement signal validation logic
        return True
        
    async def execute_trade(self, signal: Dict):
        """Execute trade based on signal"""
        try:
            order = await self.trading_system.open_position(
                asset=signal["asset"],
                side=signal["action"],
                price=signal.get("price"),
                attach_stops=True
            )
            if order:
                self.active_trades[order.id] = {
                    "signal": signal,
                    "order": order,
                    "status": "open"
                }
        except Exception as e:
            await self.send_message(
                MessageType.ORDER_UPDATE,
                {"error": str(e), "signal": signal}
            )
            
    async def update_trade_status(self, update: Dict):
        """Update status of active trades"""
        order_id = update.get("order_id")
        if order_id in self.active_trades:
            self.active_trades[order_id]["status"] = update.get("status")
            await self.learn_from_interaction(update)
