from typing import Dict, Any, Optional, List
from datetime import datetime
import ccxt
from ..core.types import TradeSignal

class TradeExecutor:
    def __init__(self, exchange_config: Dict[str, Any]):
        self.exchange = self._initialize_exchange(exchange_config)
        self.active_orders: Dict[str, Dict[str, Any]] = {}
        self.position_cache: Dict[str, Dict[str, Any]] = {}
        self.risk_limits = exchange_config.get('risk_limits', {
            'max_position_size': 0.1,  # 10% of available balance
            'max_daily_loss': 0.05,    # 5% max daily loss
            'min_order_size': 0.001    # Minimum order size
        })

    def _initialize_exchange(self, config: Dict[str, Any]) -> ccxt.Exchange:
        """Initialize exchange connection using CCXT"""
        exchange_id = config['exchange_id']
        exchange_class = getattr(ccxt, exchange_id)
        return exchange_class({
            'apiKey': config['api_key'],
            'secret': config['api_secret'],
            'enableRateLimit': True,
            **config.get('extra_params', {})
        })

    async def execute_trade(self, signal: TradeSignal, 
                          market: str, size: float) -> Optional[Dict[str, Any]]:
        """Execute a trade based on the signal"""
        try:
            # Skip if signal confidence is too low
            if signal.confidence < 0.5:
                return None

            # Get market info
            market_info = await self.exchange.fetch_ticker(market)
            current_price = market_info['last']

            # Calculate position size
            position_size = await self._calculate_position_size(size, current_price)

            # Check risk limits
            if not self._check_risk_limits(position_size, current_price):
                return None

            # Execute order
            if signal.type == 'BUY':
                order = await self.exchange.create_market_buy_order(
                    market,
                    position_size
                )
            elif signal.type == 'SELL':
                order = await self.exchange.create_market_sell_order(
                    market,
                    position_size
                )
            else:
                return None

            # Store order info
            order_info = {
                'order': order,
                'signal': signal,
                'market': market,
                'size': position_size,
                'entry_price': current_price,
                'status': 'open',
                'timestamp': datetime.now().timestamp(),
                'risk_metrics': await self._calculate_risk_metrics(position_size, current_price)
            }
            self.active_orders[order['id']] = order_info

            return order_info

        except Exception as e:
            print(f"Error executing trade: {str(e)}")
            return None

    async def update_order_status(self, order_id: str) -> Dict[str, Any]:
        """Update the status of an active order"""
        if order_id not in self.active_orders:
            return {'status': 'not_found'}

        try:
            order_info = await self.exchange.fetch_order(order_id)
            self.active_orders[order_id]['status'] = order_info['status']
            self.active_orders[order_id]['filled'] = order_info['filled']
            self.active_orders[order_id]['remaining'] = order_info['remaining']
            
            # If order is filled, move to position cache
            if order_info['status'] == 'closed':
                position = self.active_orders.pop(order_id)
                self.position_cache[order_id] = position

            return self.active_orders.get(order_id, self.position_cache.get(order_id))

        except Exception as e:
            print(f"Error updating order status: {str(e)}")
            return {'status': 'error', 'error': str(e)}

    async def _calculate_position_size(self, size: float, current_price: float) -> float:
        """Calculate position size based on available balance and risk parameters"""
        try:
            # Get account balance
            balance = await self.exchange.fetch_balance()
            available_balance = balance['free']['USDT']  # Assuming USDT as base currency

            # Calculate position size
            max_position_size = available_balance * min(size, self.risk_limits['max_position_size'])
            position_size = max_position_size / current_price

            # Ensure minimum order size
            if position_size < self.risk_limits['min_order_size']:
                return 0.0

            return position_size

        except Exception as e:
            print(f"Error calculating position size: {str(e)}")
            return 0.0

    def _check_risk_limits(self, position_size: float, current_price: float) -> bool:
        """Check if trade meets risk management criteria"""
        try:
            # Calculate daily PnL
            daily_pnl = self._calculate_daily_pnl()
            if abs(daily_pnl) >= self.risk_limits['max_daily_loss']:
                return False

            # Check position size limits
            if position_size < self.risk_limits['min_order_size']:
                return False

            return True

        except Exception as e:
            print(f"Error checking risk limits: {str(e)}")
            return False

    async def close_position(self, position_id: str, reason: str = 'manual') -> Optional[Dict[str, Any]]:
        """Close an open position"""
        if position_id not in self.position_cache:
            return None

        position = self.position_cache[position_id]
        try:
            # Get current market price
            market_info = await self.exchange.fetch_ticker(position['market'])
            current_price = market_info['last']

            # Create opposite order to close position
            if position['signal'].type == 'BUY':
                order = await self.exchange.create_market_sell_order(
                    position['market'],
                    position['size']
                )
            else:
                order = await self.exchange.create_market_buy_order(
                    position['market'],
                    position['size']
                )

            # Calculate PnL
            pnl = self._calculate_pnl(position, current_price)

            # Update position info
            close_info = {
                'position_id': position_id,
                'close_order': order,
                'exit_price': current_price,
                'pnl': pnl,
                'reason': reason,
                'close_timestamp': datetime.now().timestamp()
            }

            # Remove from position cache
            closed_position = self.position_cache.pop(position_id)
            closed_position.update(close_info)

            return closed_position

        except Exception as e:
            print(f"Error closing position: {str(e)}")
            return None

    def _calculate_pnl(self, position: Dict[str, Any], current_price: float) -> float:
        """Calculate PnL for a position"""
        entry_price = position['entry_price']
        size = position['size']

        if position['signal'].type == 'BUY':
            return (current_price - entry_price) * size
        else:
            return (entry_price - current_price) * size

    def _calculate_daily_pnl(self) -> float:
        """Calculate total PnL for the day"""
        total_pnl = 0.0
        today = datetime.now().date()

        # Include closed positions
        for position in self.position_cache.values():
            if datetime.fromtimestamp(position['timestamp']).date() == today:
                total_pnl += position.get('pnl', 0.0)

        return total_pnl

    async def _calculate_risk_metrics(self, position_size: float, current_price: float) -> Dict[str, float]:
        """Calculate risk metrics for a position"""
        balance = await self.exchange.fetch_balance()
        available_balance = balance['free']['USDT']

        return {
            'position_size_ratio': (position_size * current_price) / available_balance,
            'daily_pnl_ratio': self._calculate_daily_pnl() / available_balance,
            'liquidation_price': 0.0  # To be implemented based on exchange specifics
        }