from typing import Dict, Any, Optional, List
from datetime import datetime
from ..agents.trading.goal_enhanced_trader import GoalEnhancedTrader
from ..execution.trade_executor import TradeExecutor
from ..core.types import MarketData, TradeSignal
from ..goals.trading import TradingGoals

class TradingCoordinator:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.traders: Dict[str, GoalEnhancedTrader] = {}
        self.executor = TradeExecutor(config['exchange'])
        self.active_trades: Dict[str, Dict[str, Any]] = {}
        
        # Initialize traders for each market
        for market_config in config['markets']:
            trader = GoalEnhancedTrader(
                agent_id=f"trader_{market_config['market']}",
                config=market_config
            )
            self.traders[market_config['market']] = trader

    async def initialize(self) -> None:
        """Initialize all components"""
        # Initialize traders
        for trader in self.traders.values():
            await trader.initialize()

    async def process_market_update(self, market: str, data: MarketData) -> None:
        """Process market data update"""
        if market not in self.traders:
            return

        trader = self.traders[market]
        await trader.process_market_data(data)

        # Generate and process trading signals
        signal = await trader.generate_trade_signal()
        if signal:
            await self._process_trading_signal(market, signal)

    async def _process_trading_signal(self, market: str, signal: TradeSignal) -> None:
        """Process trading signals and execute trades"""
        if signal.type == 'HOLD':
            return

        # Execute trade
        trade_result = await self.executor.execute_trade(
            signal=signal,
            market=market,
            size=self.config['markets'][market].get('position_size', 0.1)
        )

        if trade_result:
            # Store trade information
            self.active_trades[trade_result['order']['id']] = trade_result
            
            # Create position management goal
            trader = self.traders[market]
            management_goal = TradingGoals.create_position_management_goal(
                market=market,
                position_id=trade_result['order']['id'],
                entry_goal_id=None  # No entry goal for now
            )
            await trader.goal_manager.add_goal(management_goal)

    async def update_positions(self) -> None:
        """Update status of all active positions"""
        for order_id in list(self.active_trades.keys()):
            order_info = await self.executor.update_order_status(order_id)
            
            if order_info['status'] == 'closed':
                # Move to position tracking
                self.active_trades.pop(order_id)
                
                # Update trader's state
                market = order_info['market']
                trader = self.traders[market]
                await trader.update_trade_history(order_info)

    async def check_position_exits(self) -> None:
        """Check and process position exits"""
        for trader in self.traders.values():
            active_goals = trader.goal_manager.get_active_goals()
            
            for goal in active_goals:
                if goal.type == 'position_management':
                    position_id = goal.parameters['position_id']
                    
                    if position_id in self.executor.position_cache:
                        position = self.executor.position_cache[position_id]
                        
                        # Check exit conditions
                        if self._should_exit_position(position, goal):
                            await self.executor.close_position(
                                position_id,
                                reason='goal_triggered'
                            )

    def _should_exit_position(self, position: Dict[str, Any], 
                            goal: Dict[str, Any]) -> bool:
        """Check if position should be exited based on goal parameters"""
        current_price = position.get('current_price')
        entry_price = position.get('entry_price')
        
        if not (current_price and entry_price):
            return False

        # Calculate current P&L
        if position['signal'].type == 'BUY':
            pnl = (current_price - entry_price) / entry_price
        else:
            pnl = (entry_price - current_price) / entry_price

        # Check stop loss
        if abs(pnl) >= goal.parameters.get('stop_loss', float('inf')):
            return True

        # Check take profit
        if pnl >= goal.parameters.get('take_profit', float('inf')):
            return True

        return False

    async def get_portfolio_status(self) -> Dict[str, Any]:
        """Get current portfolio status"""
        status = {
            'active_trades': len(self.active_trades),
            'positions': len(self.executor.position_cache),
            'markets': {}
        }

        for market, trader in self.traders.items():
            market_status = {
                'active_goals': len(trader.goal_manager.get_active_goals()),
                'trade_history': len(trader.trade_history),
                'patterns': len(trader.market_patterns)
            }
            status['markets'][market] = market_status

        return status

    async def get_market_analysis(self, market: str) -> Optional[Dict[str, Any]]:
        """Get current market analysis"""
        if market not in self.traders:
            return None

        trader = self.traders[market]
        context = await trader.load_context()
        
        return {
            'current_price': context.get('current_price'),
            'current_patterns': context.get('current_patterns', []),
            'active_goals': [goal.__dict__ for goal in 
                           trader.goal_manager.get_active_goals()],
            'recent_trades': trader.trade_history[-5:] if trader.trade_history else []
        }