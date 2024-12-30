from dataclasses import dataclass
from typing import Dict, List, Optional
from decimal import Decimal
import numpy as np
from datetime import datetime, timedelta
from collections import deque

@dataclass
class RiskMetrics:
    """Comprehensive risk metrics for a position or portfolio"""
    var_95: float  # 95% Value at Risk
    var_99: float  # 99% Value at Risk
    expected_shortfall: float  # Average loss beyond VaR
    beta: float  # Market correlation
    volatility: float  # Historical volatility
    sharpe_ratio: Optional[float] = None
    max_drawdown: float = 0.0
    correlation_matrix: Optional[np.ndarray] = None

class AdvancedRiskManager:
    """Advanced risk calculations and monitoring"""
    
    def __init__(self, 
                 lookback_period: int = 100,
                 confidence_level: float = 0.95,
                 use_monte_carlo: bool = True):
        self.lookback_period = lookback_period
        self.confidence_level = confidence_level
        self.use_monte_carlo = use_monte_carlo
        self.price_history: Dict[str, deque] = {}
        self.returns_history: Dict[str, deque] = {}
        self.last_update = datetime.now()
    
    def update_price_data(self, symbol: str, price: float, timestamp: datetime):
        """Update price history and calculate returns"""
        # Initialize if needed
        if symbol not in self.price_history:
            self.price_history[symbol] = deque(maxlen=self.lookback_period)
            self.returns_history[symbol] = deque(maxlen=self.lookback_period-1)
            
        self.price_history[symbol].append(price)
        
        # Calculate return if we have at least 2 prices
        if len(self.price_history[symbol]) >= 2:
            returns = np.log(price / self.price_history[symbol][-2])
            self.returns_history[symbol].append(returns)
    
    def calculate_correlation_matrix(self) -> np.ndarray:
        """Calculate correlation matrix between all traded symbols"""
        symbols = list(self.returns_history.keys())
        n_symbols = len(symbols)
        
        if n_symbols < 2:
            return np.array([[1.0]])
            
        # Create return matrix
        returns_matrix = np.zeros((self.lookback_period-1, n_symbols))
        for i, symbol in enumerate(symbols):
            returns = list(self.returns_history[symbol])
            if len(returns) < self.lookback_period-1:
                # Pad with zeros if not enough history
                returns = [0.0] * (self.lookback_period-1 - len(returns)) + returns
            returns_matrix[:, i] = returns
            
        return np.corrcoef(returns_matrix.T)
    
    def calculate_var(self, symbol: str, position_size: Decimal) -> float:
        """Calculate Value at Risk using historical simulation or Monte Carlo"""
        if len(self.returns_history[symbol]) < self.lookback_period // 2:
            return 0.0
            
        returns = np.array(self.returns_history[symbol])
        position_value = float(position_size * Decimal(str(self.price_history[symbol][-1])))
        
        if self.use_monte_carlo:
            # Monte Carlo VaR
            mean_return = np.mean(returns)
            std_return = np.std(returns)
            simulations = 10000
            simulated_returns = np.random.normal(mean_return, std_return, simulations)
            simulated_values = position_value * np.exp(simulated_returns)
            var = position_value - np.percentile(simulated_values, (1 - self.confidence_level) * 100)
        else:
            # Historical VaR
            sorted_returns = np.sort(returns)
            var_index = int((1 - self.confidence_level) * len(sorted_returns))
            var = position_value * -sorted_returns[var_index]
            
        return float(var)
        
    def calculate_expected_shortfall(self, symbol: str, position_size: Decimal) -> float:
        """Calculate Expected Shortfall (Conditional VaR)"""
        if len(self.returns_history[symbol]) < self.lookback_period // 2:
            return 0.0
            
        returns = np.array(self.returns_history[symbol])
        position_value = float(position_size * Decimal(str(self.price_history[symbol][-1])))
        
        # Sort returns and find cutoff for VaR
        sorted_returns = np.sort(returns)
        var_index = int((1 - self.confidence_level) * len(sorted_returns))
        
        # Calculate average loss beyond VaR
        tail_returns = sorted_returns[:var_index]
        expected_shortfall = position_value * -np.mean(tail_returns)
        
        return float(expected_shortfall)
    
    def calculate_portfolio_var(self, positions: Dict[str, Decimal]) -> float:
        """Calculate portfolio VaR considering correlations"""
        if not positions:
            return 0.0
            
        # Get position values and weights
        symbols = list(positions.keys())
        position_values = np.array([
            float(positions[s] * Decimal(str(self.price_history[s][-1])))
            for s in symbols
        ])
        total_value = np.sum(position_values)
        weights = position_values / total_value if total_value > 0 else np.zeros_like(position_values)
        
        # Get returns and correlation matrix
        corr_matrix = self.calculate_correlation_matrix()
        volatilities = np.array([
            np.std(list(self.returns_history[s])) for s in symbols
        ])
        
        # Calculate covariance matrix
        cov_matrix = np.diag(volatilities) @ corr_matrix @ np.diag(volatilities)
        
        # Portfolio variance
        portfolio_variance = weights @ cov_matrix @ weights.T
        
        # Portfolio VaR
        z_score = 1.645  # 95% confidence level
        portfolio_var = total_value * z_score * np.sqrt(portfolio_variance)
        
        return float(portfolio_var)
        
    def calculate_position_risk_metrics(self, symbol: str, position_size: Decimal) -> RiskMetrics:
        """Calculate comprehensive risk metrics for a position"""
        if len(self.returns_history[symbol]) < self.lookback_period // 2:
            return RiskMetrics(
                var_95=0.0,
                var_99=0.0,
                expected_shortfall=0.0,
                beta=0.0,
                volatility=0.0
            )
            
        returns = np.array(self.returns_history[symbol])
        
        # Calculate metrics
        volatility = np.std(returns) * np.sqrt(252)  # Annualized
        var_95 = self.calculate_var(symbol, position_size)
        
        # Temporarily set confidence level to 99% for VaR calculation
        old_confidence = self.confidence_level
        self.confidence_level = 0.99
        var_99 = self.calculate_var(symbol, position_size)
        self.confidence_level = old_confidence
        
        expected_shortfall = self.calculate_expected_shortfall(symbol, position_size)
        
        # Simple beta calculation (assuming market returns are available)
        beta = 1.0  # Placeholder for now
        
        return RiskMetrics(
            var_95=var_95,
            var_99=var_99,
            expected_shortfall=expected_shortfall,
            beta=beta,
            volatility=volatility
        )