from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import numpy as np
from dataclasses import dataclass

@dataclass
class TradeMetrics:
    win_rate: float
    profit_factor: float
    avg_profit: float
    avg_loss: float
    max_drawdown: float
    sharpe_ratio: float
    recovery_factor: float
    avg_trade_duration: timedelta
    risk_reward_ratio: float

@dataclass
class PositionMetrics:
    total_positions: int
    open_positions: int
    closed_positions: int
    profitable_positions: int
    losing_positions: int
    avg_position_size: float
    largest_position: float
    avg_holding_time: timedelta

@dataclass
class RiskMetrics:
    daily_var: float
    monthly_var: float
    beta: float
    correlation: float
    max_leverage: float
    margin_usage: float
    stress_test_loss: float

class PerformanceTracker:
    def __init__(self, config: Dict[str, Any]):
        self.trade_history: List[Dict[str, Any]] = []
        self.position_history: List[Dict[str, Any]] = []
        self.daily_returns: List[float] = []
        self.config = config
        self.risk_free_rate = config.get('risk_free_rate', 0.02)

    def add_trade(self, trade: Dict[str, Any]) -> None:
        """Add a new trade to history"""
        self.trade_history.append({
            **trade,
            'timestamp': datetime.now() if 'timestamp' not in trade else trade['timestamp']
        })
        self._update_daily_returns()

    def add_position(self, position: Dict[str, Any]) -> None:
        """Add a position to history"""
        self.position_history.append({
            **position,
            'timestamp': datetime.now() if 'timestamp' not in position else position['timestamp']
        })

    def get_trade_metrics(self, lookback_days: Optional[int] = None) -> TradeMetrics:
        """Calculate trade performance metrics"""
        trades = self._filter_by_lookback(self.trade_history, lookback_days)
        if not trades:
            return self._empty_trade_metrics()

        profitable_trades = [t for t in trades if t.get('pnl', 0) > 0]
        losing_trades = [t for t in trades if t.get('pnl', 0) <= 0]

        win_rate = len(profitable_trades) / len(trades) if trades else 0
        profit_factor = (sum(t['pnl'] for t in profitable_trades) / 
                        abs(sum(t['pnl'] for t in losing_trades))) if losing_trades else float('inf')

        avg_profit = np.mean([t['pnl'] for t in profitable_trades]) if profitable_trades else 0
        avg_loss = np.mean([t['pnl'] for t in losing_trades]) if losing_trades else 0

        durations = [t.get('duration', timedelta(0)) for t in trades]
        avg_duration = sum(durations, timedelta(0)) / len(durations) if durations else timedelta(0)

        return TradeMetrics(
            win_rate=win_rate,
            profit_factor=profit_factor,
            avg_profit=avg_profit,
            avg_loss=avg_loss,
            max_drawdown=self._calculate_max_drawdown(trades),
            sharpe_ratio=self._calculate_sharpe_ratio(),
            recovery_factor=self._calculate_recovery_factor(trades),
            avg_trade_duration=avg_duration,
            risk_reward_ratio=abs(avg_profit/avg_loss) if avg_loss != 0 else float('inf')
        )

    def get_position_metrics(self, lookback_days: Optional[int] = None) -> PositionMetrics:
        """Calculate position-related metrics"""
        positions = self._filter_by_lookback(self.position_history, lookback_days)
        if not positions:
            return self._empty_position_metrics()

        open_positions = [p for p in positions if p.get('status') == 'open']
        closed_positions = [p for p in positions if p.get('status') == 'closed']
        profitable_positions = [p for p in closed_positions if p.get('pnl', 0) > 0]

        sizes = [p.get('size', 0) for p in positions]
        holding_times = [p.get('duration', timedelta(0)) for p in closed_positions]

        return PositionMetrics(
            total_positions=len(positions),
            open_positions=len(open_positions),
            closed_positions=len(closed_positions),
            profitable_positions=len(profitable_positions),
            losing_positions=len(closed_positions) - len(profitable_positions),
            avg_position_size=np.mean(sizes) if sizes else 0,
            largest_position=max(sizes) if sizes else 0,
            avg_holding_time=sum(holding_times, timedelta(0)) / len(holding_times) 
                if holding_times else timedelta(0)
        )

    def get_risk_metrics(self, lookback_days: Optional[int] = None) -> RiskMetrics:
        """Calculate risk metrics"""
        returns = self._get_returns_series(lookback_days)
        if not returns:
            return self._empty_risk_metrics()

        daily_returns = np.array(returns)
        monthly_returns = self._aggregate_to_monthly(daily_returns)

        return RiskMetrics(
            daily_var=self._calculate_var(daily_returns, 0.95),
            monthly_var=self._calculate_var(monthly_returns, 0.95),
            beta=self._calculate_beta(daily_returns),
            correlation=self._calculate_correlation(daily_returns),
            max_leverage=self._calculate_max_leverage(),
            margin_usage=self._calculate_margin_usage(),
            stress_test_loss=self._calculate_stress_test_loss(daily_returns)
        )

    def _calculate_max_drawdown(self, trades: List[Dict[str, Any]]) -> float:
        """Calculate maximum drawdown from trade history"""
        if not trades:
            return 0.0

        cumulative_pnl = np.cumsum([t.get('pnl', 0) for t in trades])
        peak = np.maximum.accumulate(cumulative_pnl)
        drawdown = (cumulative_pnl - peak) / peak
        return abs(float(min(drawdown, default=0)))

    def _calculate_sharpe_ratio(self) -> float:
        """Calculate Sharpe ratio from daily returns"""
        if not self.daily_returns:
            return 0.0

        excess_returns = np.array(self.daily_returns) - self.risk_free_rate/252
        if len(excess_returns) < 2:
            return 0.0

        return np.mean(excess_returns) / np.std(excess_returns, ddof=1) * np.sqrt(252)

    def _calculate_recovery_factor(self, trades: List[Dict[str, Any]]) -> float:
        """Calculate recovery factor"""
        if not trades:
            return 0.0

        total_profit = sum(t.get('pnl', 0) for t in trades)
        max_drawdown = self._calculate_max_drawdown(trades)
        return total_profit / max_drawdown if max_drawdown != 0 else float('inf')

    def _calculate_var(self, returns: np.ndarray, confidence: float) -> float:
        """Calculate Value at Risk"""
        if len(returns) < 2:
            return 0.0
        return float(np.percentile(returns, (1 - confidence) * 100))

    def _calculate_beta(self, returns: np.ndarray) -> float:
        """Calculate beta against market returns"""
        if len(returns) < 2:
            return 1.0

        market_returns = self._get_market_returns()
        if len(market_returns) != len(returns):
            return 1.0

        covariance = np.cov(returns, market_returns)[0,1]
        market_variance = np.var(market_returns)
        return covariance / market_variance if market_variance != 0 else 1.0

    def _calculate_correlation(self, returns: np.ndarray) -> float:
        """Calculate correlation with market"""
        if len(returns) < 2:
            return 0.0

        market_returns = self._get_market_returns()
        if len(market_returns) != len(returns):
            return 0.0

        return float(np.corrcoef(returns, market_returns)[0,1])

    def _calculate_max_leverage(self) -> float:
        """Calculate maximum leverage used"""
        if not self.position_history:
            return 1.0

        leverages = [p.get('leverage', 1.0) for p in self.position_history]
        return max(leverages)

    def _calculate_margin_usage(self) -> float:
        """Calculate current margin usage"""
        open_positions = [p for p in self.position_history if p.get('status') == 'open']
        if not open_positions:
            return 0.0

        total_margin = sum(p.get('margin', 0) for p in open_positions)
        account_value = self.config.get('account_value', float('inf'))
        return total_margin / account_value if account_value != 0 else 0.0

    def _calculate_stress_test_loss(self, returns: np.ndarray) -> float:
        """Calculate potential loss under stress scenario"""
        if len(returns) < 2:
            return 0.0

        # Simulate extreme market conditions (3 standard deviations)
        std_dev = np.std(returns)
        stress_scenario = -3 * std_dev
        
        # Calculate potential portfolio loss
        portfolio_value = self.config.get('account_value', 0)
        return portfolio_value * stress_scenario

    def _update_daily_returns(self) -> None:
        """Update daily returns series"""
        if not self.trade_history:
            return

        # Group trades by day and calculate daily PnL
        trades_by_day = {}
        for trade in self.trade_history:
            date = trade['timestamp'].date()
            trades_by_day.setdefault(date, []).append(trade)

        daily_pnl = {date: sum(t.get('pnl', 0) for t in trades)
                    for date, trades in trades_by_day.items()}

        # Convert to returns
        starting_value = self.config.get('initial_capital', 100000)
        current_value = starting_value
        self.daily_returns = []

        for date in sorted(daily_pnl.keys()):
            pnl = daily_pnl[date]
            daily_return = pnl / current_value
            self.daily_returns.append(daily_return)
            current_value += pnl

    def _filter_by_lookback(self, 
                          items: List[Dict[str, Any]], 
                          lookback_days: Optional[int]) -> List[Dict[str, Any]]:
        """Filter items by lookback period"""
        if not lookback_days:
            return items

        cutoff = datetime.now() - timedelta(days=lookback_days)
        return [item for item in items if item['timestamp'] >= cutoff]

    def _get_returns_series(self, lookback_days: Optional[int]) -> List[float]:
        """Get returns series filtered by lookback period"""
        if not lookback_days:
            return self.daily_returns

        return self.daily_returns[-lookback_days:]

    def _get_market_returns(self) -> np.ndarray:
        """Get market benchmark returns"""
        # Placeholder - should be implemented to fetch actual market data
        return np.zeros_like(self.daily_returns)

    def _aggregate_to_monthly(self, daily_returns: np.ndarray) -> np.ndarray:
        """Aggregate daily returns to monthly"""
        if len(daily_returns) < 21:  # Minimum one month of data
            return np.array([]))

        # Approximate monthly returns by combining 21 trading days
        n_months = len(daily_returns) // 21
        monthly_returns = np.array([np.prod(1 + daily_returns[i*21:(i+1)*21]) - 1
                                  for i in range(n_months)])
        return monthly_returns

    def _empty_trade_metrics(self) -> TradeMetrics:
        """Return empty trade metrics"""
        return TradeMetrics(
            win_rate=0.0, profit_factor=0.0, avg_profit=0.0, avg_loss=0.0,
            max_drawdown=0.0, sharpe_ratio=0.0, recovery_factor=0.0,
            avg_trade_duration=timedelta(0), risk_reward_ratio=0.0
        )

    def _empty_position_metrics(self) -> PositionMetrics:
        """Return empty position metrics"""
        return PositionMetrics(
            total_positions=0, open_positions=0, closed_positions=0,
            profitable_positions=0, losing_positions=0, avg_position_size=0.0,
            largest_position=0.0, avg_holding_time=timedelta(0)
        )

    def _empty_risk_metrics(self) -> RiskMetrics:
        """Return empty risk metrics"""
        return RiskMetrics(
            daily_var=0.0, monthly_var=0.0, beta=1.0, correlation=0.0,
            max_leverage=1.0, margin_usage=0.0, stress_test_loss=0.0
        )