from typing import Dict, Any, List, Optional
from datetime import datetime
from ..enhanced_base import EnhancedBaseAgent
from ...core.types import TradeSignal, MarketData
from ...analysis.pattern_recognition import PatternRecognizer, Pattern
from ...goals.base import GoalManager, Goal, GoalStatus
from ...goals.trading import TradingGoals

class GoalEnhancedTrader(EnhancedBaseAgent):
    def __init__(self, agent_id: str, config: Dict[str, Any]):
        super().__init__(agent_id, config)
        self.pattern_recognizer = PatternRecognizer(
            window_size=config.get('pattern_window', 20)
        )
        self.goal_manager = GoalManager()
        self.market_patterns = {}
        self.trade_history = []
        self.active_positions: Dict[str, Dict[str, Any]] = {}

    async def initialize(self) -> None:
        """Initialize the agent with basic goals"""
        # Create initial risk assessment goal
        risk_goal = TradingGoals.create_risk_assessment_goal(
            market=self.config['market']
        )
        await self.goal_manager.add_goal(risk_goal)

        # Create initial market analysis goal
        analysis_goal = TradingGoals.create_market_analysis_goal(
            market=self.config['market'],
            timeframe=self.config['timeframe']
        )
        await self.goal_manager.add_goal(analysis_goal)

    async def process_market_data(self, data: MarketData) -> None:
        """Process market data and update relevant goals"""
        # Identify patterns
        patterns = self.pattern_recognizer.identify_patterns(data)
        if patterns:
            await self.remember(f'patterns_{data.timestamp}', patterns)
            self.market_patterns[data.timestamp] = patterns
            
            # Update market context
            await self.update_context({
                'current_price': data.price_history[-1],
                'current_patterns': patterns,
                'current_time': data.timestamp
            })

        # Update market analysis goals
        await self._update_analysis_goals(patterns, data)
        
        # Update position management goals
        await self._update_position_goals(data)

    async def _update_analysis_goals(self, patterns: List[Pattern], data: MarketData) -> None:
        """Update progress of market analysis goals"""
        for goal in self.goal_manager.get_active_goals():
            if goal.type == 'market_analysis':
                required_patterns = goal.parameters['required_patterns']
                min_confidence = goal.parameters['min_confidence']
                
                # Check if we have all required patterns with sufficient confidence
                found_patterns = {p.type: p.confidence for p in patterns}
                required_found = all(
                    pattern in found_patterns and 
                    found_patterns[pattern] >= min_confidence
                    for pattern in required_patterns
                )
                
                if required_found:
                    await self.goal_manager.update_goal_progress(
                        goal.id,
                        1.0,
                        {'patterns': [p.__dict__ for p in patterns]}
                    )

    async def _update_position_goals(self, data: MarketData) -> None:
        """Update position management goals based on current market data"""
        for goal in self.goal_manager.get_active_goals():
            if goal.type == 'position_management':
                position_id = goal.parameters['position_id']
                if position_id in self.active_positions:
                    position = self.active_positions[position_id]
                    await self._check_position_conditions(position, goal, data)

    async def _check_position_conditions(self, position: Dict[str, Any], 
                                       goal: Goal, data: MarketData) -> None:
        """Check if position meets its exit conditions"""
        current_price = data.price_history[-1]
        entry_price = position['entry_price']
        
        # Calculate current P&L
        if position['direction'] == 'BUY':
            pnl = (current_price - entry_price) / entry_price
        else:
            pnl = (entry_price - current_price) / entry_price

        # Check stop loss
        if abs(pnl) >= goal.parameters['stop_loss']:
            await self._close_position(position['id'], 'stop_loss', pnl)
            await self.goal_manager.update_goal_progress(
                goal.id, 1.0, {'reason': 'stop_loss', 'pnl': pnl}
            )

        # Check take profit
        elif pnl >= goal.parameters['take_profit']:
            await self._close_position(position['id'], 'take_profit', pnl)
            await self.goal_manager.update_goal_progress(
                goal.id, 1.0, {'reason': 'take_profit', 'pnl': pnl}
            )

        # Update trailing stop if enabled
        elif goal.parameters.get('trailing_stop') and pnl > 0:
            new_stop = current_price * (1 - goal.parameters['stop_loss'])
            if new_stop > position.get('trailing_stop', 0):
                position['trailing_stop'] = new_stop

    async def _close_position(self, position_id: str, reason: str, pnl: float) -> None:
        """Close a trading position"""
        position = self.active_positions.pop(position_id)
        trade_result = {
            'position_id': position_id,
            'market': position['market'],
            'direction': position['direction'],
            'entry_price': position['entry_price'],
            'exit_price': position['current_price'],
            'pnl': pnl,
            'reason': reason,
            'timestamp': datetime.now().timestamp()
        }
        
        await self.update_trade_history(trade_result)

    async def generate_trade_signal(self) -> TradeSignal:
        """Generate trade signal based on completed analysis goals"""
        active_goals = self.goal_manager.get_active_goals()
        completed_analyses = [
            goal for goal in self.goal_manager.goals.values()
            if goal.type == 'market_analysis' and 
            goal.status == GoalStatus.COMPLETED
        ]

        if not completed_analyses:
            return TradeSignal(type='HOLD', confidence=0.0, 
                             timestamp=datetime.now().timestamp())

        # Use most recent analysis
        latest_analysis = max(completed_analyses, key=lambda g: g.created_at)
        patterns = latest_analysis.result['patterns']

        # Generate signal based on patterns
        return await self._analyze_patterns_for_signal(patterns)

    async def _analyze_patterns_for_signal(self, patterns: List[Dict[str, Any]]) -> TradeSignal:
        """Analyze patterns to generate a trade signal"""
        signal_weights = {'BUY': 0.0, 'SELL': 0.0, 'HOLD': 0.0}
        total_confidence = 0.0

        for pattern in patterns:
            if pattern['type'] == 'trend_reversal':
                if pattern['indicators']['rsi'] > 70:
                    signal_weights['SELL'] += pattern['confidence']
                elif pattern['indicators']['rsi'] < 30:
                    signal_weights['BUY'] += pattern['confidence']
                total_confidence += pattern['confidence']

            elif pattern['type'] == 'breakout':
                if pattern.get('resistance_level') and \
                   self.context['current_price'] > pattern['resistance_level']:
                    signal_weights['BUY'] += pattern['confidence']
                elif pattern.get('support_level') and \
                     self.context['current_price'] < pattern['support_level']:
                    signal_weights['SELL'] += pattern['confidence']
                total_confidence += pattern['confidence']

        if total_confidence == 0:
            return TradeSignal(type='HOLD', confidence=0.0, 
                             timestamp=self.context['current_time'])

        # Normalize weights
        for signal_type in signal_weights:
            signal_weights[signal_type] /= total_confidence

        # Select signal with highest weight
        signal_type = max(signal_weights.items(), key=lambda x: x[1])[0]
        
        return TradeSignal(
            type=signal_type,
            confidence=signal_weights[signal_type],
            timestamp=self.context['current_time']
        )