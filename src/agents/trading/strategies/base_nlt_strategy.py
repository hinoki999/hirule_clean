from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Dict, Optional
from ..nlt_trading_agent import NLTTradingAgent

class BaseNLTStrategy(ABC):
    """Base class for NLT-specific trading strategies"""
    
    def __init__(self, agent: NLTTradingAgent):
        self.agent = agent
        self.active_trades: Dict[str, Dict] = {}
        
    @abstractmethod
    async def analyze_market(self, symbol: str, market_data: Dict) -> Optional[Dict]:
        """Analyze market data and return trading signals if any"""
        pass
        
    @abstractmethod
    async def generate_trade_parameters(self, signal: Dict) -> Dict:
        """Generate trade parameters based on the signal"""
        pass
        
    async def check_risk_limits(self, trade_params: Dict) -> bool:
        """Check if trade parameters comply with risk management rules"""
        symbol = trade_params["symbol"]
        amount = Decimal(str(trade_params["amount"]))
        
        # Check position limits
        current_position = self.agent.positions.get(symbol, Decimal("0"))
        total_exposure = current_position + amount
        
        if total_exposure > Decimal(self.agent.config.max_position_size):
            return False
            
        # Check minimum trade size
        if amount < Decimal(self.agent.config.min_trade_size):
            return False
            
        return True
