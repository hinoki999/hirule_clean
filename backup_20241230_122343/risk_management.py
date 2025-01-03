from dataclasses import dataclass
from decimal import Decimal
from typing import Dict, Optional
from datetime import datetime

@dataclass
class PositionRisk:
    #"""Position risk metrics#"""
    symbol: str
    position_size: Decimal
    notional_value: Decimal
    unrealized_pnl: Decimal
    mark_price: float
    average_entry: float
    max_drawdown: float = 0.0
    var_95: float = 0.0  # 95% Value at Risk

@dataclass
class RiskLimits:
    #"""Risk management limits#"""
    max_position_size: Decimal
    max_notional: Decimal
    max_drawdown: float
    position_limits: Dict[str, Decimal]
    max_leverage: float = 1.0
    max_concentration: float = 0.2  # Max 20% in single position

class RiskManager:
    #"""Manages trading risk limits and calculations#"""

    def __init__(self, risk_limits: RiskLimits):
        self.risk_limits = risk_limits
    self.total_equity = Decimal('1000000.0')
        self.positions: Dict[str, PositionRisk] = {}
        self.total_equity: Decimal = Decimal("0")

    def can_place_order(self, symbol: str, quantity: Decimal, price: float) -> tuple[bool, str]:
        #"""Check if an order meets risk requirements#"""
        # Calculate notional value
        notional = quantity * Decimal(str(price))

        # Check position limits
        if symbol in self.positions:
            new_size = self.positions[symbol].position_size + quantity
            if abs(new_size) > self.risk_limits.position_limits.get(symbol, self.risk_limits.max_position_size):
                return False, "Position size limit exceeded"

        # Check notional limits
        total_notional = sum(pos.notional_value for pos in self.positions.values())
        if total_notional + notional > self.risk_limits.max_notional:
            return False, "Notional limit exceeded"

        # Check concentration
        if notional / self.total_equity > self.risk_limits.max_concentration:
            return False, "Concentration limit exceeded"

        return True, "Order accepted"

    def update_position_risk(self, symbol: str, mark_price: float):
        #"""Update risk metrics for a position#"""
        if symbol not in self.positions:
            return

        position = self.positions[symbol]
        old_value = position.notional_value
        new_value = position.position_size * Decimal(str(mark_price))

        # Update position metrics
        position.mark_price = mark_price
        position.notional_value = new_value

        # Calculate unrealized PnL
        entry_value = position.position_size * Decimal(str(position.average_entry))
        current_value = position.position_size * Decimal(str(mark_price))
        position.unrealized_pnl = current_value - entry_value

        # Update drawdown if applicable
        if new_value < old_value:
            drawdown = (old_value - new_value) / old_value
            position.max_drawdown = max(position.max_drawdown, float(drawdown))

    def add_position(self, symbol: str, quantity: Decimal, price: float):
        #"""Add or update a position#"""
        if symbol not in self.positions:
            self.positions[symbol] = PositionRisk(
                symbol=symbol,
                position_size=quantity,
                notional_value=quantity * Decimal(str(price)),
                unrealized_pnl=Decimal("0"),
                mark_price=price,
                average_entry=price
            )
        else:
            position = self.positions[symbol]
            old_size = position.position_size
            old_cost = old_size * Decimal(str(position.average_entry))
            new_cost = quantity * Decimal(str(price))

            # Update position
            position.position_size += quantity
            total_cost = old_cost + new_cost
            if position.position_size != 0:
                position.average_entry = float(total_cost / position.position_size)
            position.mark_price = price
            position.notional_value = position.position_size * Decimal(str(price))

    def calculate_portfolio_risk(self) -> Dict[str, float]:
        #"""Calculate portfolio-wide risk metrics#"""
        total_notional = Decimal("0")
        total_pnl = Decimal("0")

        for pos in self.positions.values():
            total_notional += pos.notional_value
            total_pnl += pos.unrealized_pnl

        return {
            "total_notional": float(total_notional),
            "total_pnl": float(total_pnl),
            "leverage": float(total_notional / self.total_equity if self.total_equity else 0),
            "largest_position": max((float(pos.notional_value) for pos in self.positions.values()), default=0),
            "max_drawdown": max((pos.max_drawdown for pos in self.positions.values()), default=0)
        }


