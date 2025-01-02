from typing import Dict, Any, List
from ..enhanced_base import EnhancedBaseAgent
from ...core.types import TradeSignal, MarketData
from ...analysis.pattern_recognition import PatternRecognizer, Pattern

class MemoryEnhancedTrader(EnhancedBaseAgent):
    def __init__(self, agent_id: str, config: Dict[str, Any]):
        super().__init__(agent_id, config)
        self.pattern_recognizer = PatternRecognizer(
            window_size=config.get('pattern_window', 20)
        )
        self.market_patterns = {}
        self.trade_history = []

    async def process_market_data(self, data: MarketData) -> None:
        """Process and store market data with pattern recognition"""
        patterns = self.pattern_recognizer.identify_patterns(data)
        if patterns:
            # Store patterns with timestamp for future reference
            await self.remember(f'patterns_{data.timestamp}', patterns)
            self.market_patterns[data.timestamp] = patterns
            
            # Update market context
            await self.update_context({
                'current_price': data.price_history[-1],
                'current_patterns': patterns,
                'current_time': data.timestamp
            })

    async def generate_trade_signal(self) -> TradeSignal:
        """Generate trade signal based on historical patterns and current context"""
        recent_patterns = await self._get_recent_patterns()
        current_context = await self.load_context()
        
        signal = await self._analyze_patterns_and_context(recent_patterns, current_context)
        await self.remember('last_signal', signal)
        
        return signal

    async def update_trade_history(self, trade: Dict[str, Any]) -> None:
        """Update trade history in memory"""
        self.trade_history.append(trade)
        await self.remember('trade_history', self.trade_history)
        
        # Update performance metrics
        await self._update_performance_metrics(trade)

    async def _get_recent_patterns(self, limit: int = 10) -> List[List[Pattern]]:
        """Retrieve recent market patterns from memory"""
        patterns = []
        for timestamp in sorted(self.market_patterns.keys(), reverse=True)[:limit]:
            stored_patterns = await self.recall(f'patterns_{timestamp}')
            if stored_patterns:
                patterns.append(stored_patterns)
        return patterns

    async def _analyze_patterns_and_context(self, 
                                          patterns: List[List[Pattern]], 
                                          context: Dict[str, Any]) -> TradeSignal:
        """Analyze patterns and context to generate trade signal"""
        if not patterns or not context:
            return TradeSignal(type='HOLD', confidence=0.0, timestamp=context.get('current_time'))

        # Analyze current patterns
        current_patterns = patterns[0] if patterns else []
        pattern_signals = []
        
        for pattern in current_patterns:
            if pattern.type == 'trend_reversal':
                if pattern.indicators['rsi'] > 70:
                    pattern_signals.append(('SELL', pattern.confidence))
                elif pattern.indicators['rsi'] < 30:
                    pattern_signals.append(('BUY', pattern.confidence))
                    
            elif pattern.type == 'breakout':
                current_price = context['current_price']
                if current_price > pattern.resistance_level:
                    pattern_signals.append(('BUY', pattern.confidence))
                elif current_price < pattern.support_level:
                    pattern_signals.append(('SELL', pattern.confidence))
                    
            elif pattern.type == 'consolidation':
                # In consolidation, wait for clearer signals
                pattern_signals.append(('HOLD', pattern.confidence))

        # Combine signals with weights
        if not pattern_signals:
            return TradeSignal(type='HOLD', confidence=0.0, timestamp=context.get('current_time'))

        # Weight signals by confidence and combine
        signal_weights = {'BUY': 0.0, 'SELL': 0.0, 'HOLD': 0.0}
        total_confidence = 0.0

        for signal_type, confidence in pattern_signals:
            signal_weights[signal_type] += confidence
            total_confidence += confidence

        # Normalize weights
        if total_confidence > 0:
            for signal_type in signal_weights:
                signal_weights[signal_type] /= total_confidence

        # Select signal with highest weight
        final_signal_type = max(signal_weights.items(), key=lambda x: x[1])[0]
        final_confidence = signal_weights[final_signal_type]

        return TradeSignal(
            type=final_signal_type,
            confidence=final_confidence,
            timestamp=context.get('current_time')
        )

    async def _update_performance_metrics(self, trade: Dict[str, Any]) -> None:
        """Update agent's performance metrics"""
        metrics = await self.recall('performance_metrics') or {
            'total_trades': 0,
            'successful_trades': 0,
            'total_profit': 0.0,
            'win_rate': 0.0
        }
        
        metrics['total_trades'] += 1
        if trade.get('profit', 0) > 0:
            metrics['successful_trades'] += 1
        metrics['total_profit'] += trade.get('profit', 0)
        metrics['win_rate'] = metrics['successful_trades'] / metrics['total_trades']
        
        await self.remember('performance_metrics', metrics)