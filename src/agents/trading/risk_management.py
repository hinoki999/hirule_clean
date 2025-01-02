from decimal import Decimal
from typing import Dict, Tuple
import logging
from dataclasses import dataclass

@dataclass
class PositionRisk:
   size: Decimal
   notional_value: Decimal
   unrealized_pnl: Decimal
   var: Decimal = Decimal("0")
   expected_shortfall: Decimal = Decimal("0")

@dataclass
class RiskLimits:
   position_limits: Dict[str, Decimal]
   notional_limits: Dict[str, Decimal] 
   risk_metrics: Dict[str, Decimal]
   volatility_scaling: Dict[str, bool | Decimal]

   @classmethod
   def from_parameters(cls, max_position_size: Decimal, max_notional: Decimal, max_drawdown: float):
       return cls(
           position_limits={"BTC/USD": max_position_size},
           notional_limits={"BTC/USD": max_notional},
           risk_metrics={
               "max_drawdown": Decimal(str(max_drawdown)),
               "max_leverage": Decimal("2.0"),
               "var_limit": Decimal("0.05"),
               "correlation_limit": Decimal("0.7")
           },
           volatility_scaling={
               "enabled": True,
               "target_vol": Decimal("0.2"),
               "max_scale": Decimal("2.0")
           }
       )

class RiskManager:
   def __init__(self, risk_limits: Dict):
       self.risk_limits = RiskLimits(**risk_limits) if isinstance(risk_limits, dict) else risk_limits
       self.positions: Dict[str, Decimal] = {}
       self.latest_prices: Dict[str, Decimal] = {}
       self.position_risks: Dict[str, PositionRisk] = {}
       self.total_equity = Decimal("0")
       self.logger = logging.getLogger(self.__class__.__name__)

   def update_position_risk(self, symbol: str, price: Decimal | float):
       price = Decimal(str(price)) if isinstance(price, float) else price
       if symbol in self.positions:
           self.latest_prices[symbol] = price
           self._update_position_risk(symbol)

   def _update_position_risk(self, symbol: str):
       if symbol not in self.positions or symbol not in self.latest_prices:
           return

       size = self.positions[symbol]  
       price = self.latest_prices[symbol]
       notional = abs(size * price)

       self.position_risks[symbol] = PositionRisk(
           size=size,
           notional_value=notional,
           unrealized_pnl=Decimal("0")
       )

   def can_place_order(self, symbol: str, size: Decimal, price: Decimal | float) -> Tuple[bool, str]:
       price = Decimal(str(price)) if isinstance(price, float) else price
       
       if not self.check_position_limits(symbol, size):
           return False, "Position limit exceeded"
          
       if not self.check_notional_limits(symbol, size, price):
           return False, "Notional limit exceeded"
          
       return True, ""

   def check_position_limits(self, symbol: str, size: Decimal) -> bool:
       if symbol not in self.risk_limits.position_limits:
           return False
          
       limit = self.risk_limits.position_limits[symbol]
       current_size = abs(self.positions.get(symbol, Decimal("0")))
       return (current_size + abs(size)) <= limit

   def check_notional_limits(self, symbol: str, size: Decimal, price: Decimal) -> bool:
       if symbol not in self.risk_limits.notional_limits:
           return False
          
       limit = self.risk_limits.notional_limits[symbol]
       notional = abs(size * price)
       current_notional = abs(self.positions.get(symbol, Decimal("0")) * 
                            self.latest_prices.get(symbol, price))
       return (current_notional + notional) <= limit

   def get_position_risk(self, symbol: str) -> PositionRisk:
       return self.position_risks.get(symbol)

   def add_position(self, symbol: str, size: Decimal, price: Decimal | float):
       price = Decimal(str(price)) if isinstance(price, float) else price
       self.positions[symbol] = size
       self.latest_prices[symbol] = price
       self._update_position_risk(symbol)
