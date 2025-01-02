from typing import Dict, Any, Optional
from datetime import datetime
from .base import Goal, GoalStatus

class TradingGoals:
    @staticmethod
    def create_market_analysis_goal(market: str, timeframe: str) -> Goal:
        """Create a goal for analyzing market conditions"""
        return Goal(
            id=f'analysis_{market}_{timeframe}_{datetime.now().timestamp()}',
            type='market_analysis',
            parameters={
                'market': market,
                'timeframe': timeframe,
                'required_patterns': ['trend_reversal', 'breakout', 'consolidation'],
                'min_confidence': 0.6
            },
            status=GoalStatus.PENDING,
            priority=1,
            dependencies=[],
            created_at=datetime.now()
        )

    @staticmethod
    def create_position_entry_goal(market: str, direction: str, 
                                 analysis_goal_id: str) -> Goal:
        """Create a goal for entering a trading position"""
        return Goal(
            id=f'entry_{market}_{direction}_{datetime.now().timestamp()}',
            type='position_entry',
            parameters={
                'market': market,
                'direction': direction,
                'max_slippage': 0.001,
                'position_size': 0.1  # 10% of available capital
            },
            status=GoalStatus.PENDING,
            priority=2,
            dependencies=[analysis_goal_id],
            created_at=datetime.now()
        )

    @staticmethod
    def create_position_management_goal(market: str, position_id: str,
                                      entry_goal_id: str) -> Goal:
        """Create a goal for managing an open position"""
        return Goal(
            id=f'manage_{position_id}_{datetime.now().timestamp()}',
            type='position_management',
            parameters={
                'market': market,
                'position_id': position_id,
                'stop_loss': 0.02,  # 2% stop loss
                'take_profit': 0.05,  # 5% take profit
                'trailing_stop': True
            },
            status=GoalStatus.PENDING,
            priority=3,
            dependencies=[entry_goal_id],
            created_at=datetime.now()
        )

    @staticmethod
    def create_risk_assessment_goal(market: str) -> Goal:
        """Create a goal for assessing trading risks"""
        return Goal(
            id=f'risk_{market}_{datetime.now().timestamp()}',
            type='risk_assessment',
            parameters={
                'market': market,
                'max_position_size': 0.2,  # 20% max position size
                'max_daily_loss': 0.05,   # 5% max daily loss
                'correlation_markets': ['BTC', 'ETH', 'TOTAL']  # Markets to check correlation
            },
            status=GoalStatus.PENDING,
            priority=1,  # High priority for risk assessment
            dependencies=[],
            created_at=datetime.now()
        )

    @staticmethod
    def create_portfolio_rebalance_goal(target_weights: Dict[str, float]) -> Goal:
        """Create a goal for portfolio rebalancing"""
        return Goal(
            id=f'rebalance_{datetime.now().timestamp()}',
            type='portfolio_rebalance',
            parameters={
                'target_weights': target_weights,
                'max_deviation': 0.05,  # 5% maximum deviation from target
                'min_trade_size': 0.01  # Minimum 1% position size
            },
            status=GoalStatus.PENDING,
            priority=2,
            dependencies=[],
            created_at=datetime.now()
        )