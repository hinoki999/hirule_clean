from typing import Dict, Any, List, Optional
import numpy as np
from dataclasses import dataclass

@dataclass
class PortfolioAllocation:
    assets: Dict[str, float]  # Asset -> weight mapping
    expected_return: float
    volatility: float
    sharpe_ratio: float

class PortfolioOptimizer:
    def __init__(self, config: Dict[str, Any]):
        self.risk_free_rate = config.get('risk_free_rate', 0.02)  # Annual risk-free rate
        self.min_weight = config.get('min_weight', 0.05)        # Minimum position size
        self.max_weight = config.get('max_weight', 0.4)         # Maximum position size
        self.optimization_window = config.get('window', 30)     # Days for optimization

    def optimize_portfolio(self, 
                          asset_returns: Dict[str, List[float]],
                          constraints: Optional[Dict[str, Any]] = None) -> PortfolioAllocation:
        """Optimize portfolio weights using Modern Portfolio Theory"""
        assets = list(asset_returns.keys())
        returns_data = np.array([asset_returns[asset] for asset in assets])

        # Calculate expected returns and covariance
        expected_returns = np.mean(returns_data, axis=1)
        cov_matrix = np.cov(returns_data)

        # Generate random portfolios
        num_portfolios = 10000
        results = self._generate_portfolios(
            num_portfolios,
            len(assets),
            expected_returns,
            cov_matrix,
            constraints
        )

        # Find optimal portfolio (highest Sharpe ratio)
        sharpe_ratios = self._calculate_sharpe_ratios(
            results['returns'],
            results['volatilities']
        )
        optimal_idx = np.argmax(sharpe_ratios)

        # Create allocation with optimal weights
        allocation = PortfolioAllocation(
            assets={asset: weight for asset, weight in 
                   zip(assets, results['weights'][optimal_idx])},
            expected_return=results['returns'][optimal_idx],
            volatility=results['volatilities'][optimal_idx],
            sharpe_ratio=sharpe_ratios[optimal_idx]
        )

        return allocation

    def _generate_portfolios(self,
                           num_portfolios: int,
                           num_assets: int,
                           expected_returns: np.ndarray,
                           cov_matrix: np.ndarray,
                           constraints: Optional[Dict[str, Any]]) -> Dict[str, np.ndarray]:
        """Generate random portfolio allocations"""
        results = {
            'weights': np.zeros((num_portfolios, num_assets)),
            'returns': np.zeros(num_portfolios),
            'volatilities': np.zeros(num_portfolios)
        }

        for i in range(num_portfolios):
            # Generate random weights
            weights = np.random.random(num_assets)
            weights = self._apply_constraints(weights, constraints)
            weights = weights / np.sum(weights)  # Normalize to sum to 1

            # Calculate portfolio metrics
            portfolio_return = np.sum(expected_returns * weights)
            portfolio_volatility = np.sqrt(
                np.dot(weights.T, np.dot(cov_matrix, weights))
            )

            # Store results
            results['weights'][i] = weights
            results['returns'][i] = portfolio_return
            results['volatilities'][i] = portfolio_volatility

        return results

    def _apply_constraints(self,
                         weights: np.ndarray,
                         constraints: Optional[Dict[str, Any]]) -> np.ndarray:
        """Apply portfolio constraints to weights"""
        # Apply min/max weight constraints
        weights = np.clip(weights, self.min_weight, self.max_weight)

        if constraints:
            # Apply custom constraints if provided
            if 'max_sector_exposure' in constraints:
                sector_weights = constraints['sector_weights']
                for sector, assets in sector_weights.items():
                    sector_exposure = np.sum(weights[assets])
                    if sector_exposure > constraints['max_sector_exposure']:
                        scale = constraints['max_sector_exposure'] / sector_exposure
                        weights[assets] *= scale

            if 'market_cap_weighted' in constraints and constraints['market_cap_weighted']:
                market_caps = np.array(constraints['market_caps'])
                weights *= market_caps

        return weights

    def _calculate_sharpe_ratios(self,
                               returns: np.ndarray,
                               volatilities: np.ndarray) -> np.ndarray:
        """Calculate Sharpe ratios for portfolios"""
        excess_returns = returns - self.risk_free_rate
        return excess_returns / volatilities

    def get_portfolio_metrics(self,
                            allocation: PortfolioAllocation,
                            asset_returns: Dict[str, List[float]]) -> Dict[str, float]:
        """Calculate additional portfolio metrics"""
        weights = np.array(list(allocation.assets.values()))
        returns_data = np.array([asset_returns[asset] for asset in allocation.assets.keys()])

        # Calculate metrics
        metrics = {
            'beta': self._calculate_portfolio_beta(weights, returns_data),
            'alpha': self._calculate_portfolio_alpha(weights, returns_data),
            'var_95': self._calculate_value_at_risk(weights, returns_data, 0.95),
            'max_drawdown': self._calculate_max_drawdown(weights, returns_data),
            'sortino_ratio': self._calculate_sortino_ratio(weights, returns_data)
        }

        return metrics

    def _calculate_portfolio_beta(self,
                                weights: np.ndarray,
                                returns_data: np.ndarray) -> float:
        """Calculate portfolio beta relative to market"""
        market_returns = np.mean(returns_data, axis=0)  # Using equal-weighted market proxy
        portfolio_returns = np.dot(weights, returns_data)
        
        covariance = np.cov(portfolio_returns, market_returns)[0,1]
        market_variance = np.var(market_returns)
        
        return covariance / market_variance if market_variance != 0 else 1.0

    def _calculate_portfolio_alpha(self,
                                 weights: np.ndarray,
                                 returns_data: np.ndarray) -> float:
        """Calculate portfolio alpha"""
        portfolio_returns = np.dot(weights, returns_data)
        market_returns = np.mean(returns_data, axis=0)
        beta = self._calculate_portfolio_beta(weights, returns_data)
        
        expected_portfolio_return = np.mean(portfolio_returns)
        expected_market_return = np.mean(market_returns)
        
        return expected_portfolio_return - (self.risk_free_rate + 
                                          beta * (expected_market_return - self.risk_free_rate))

    def _calculate_value_at_risk(self,
                                weights: np.ndarray,
                                returns_data: np.ndarray,
                                confidence_level: float) -> float:
        """Calculate portfolio Value at Risk"""
        portfolio_returns = np.dot(weights, returns_data)
        return np.percentile(portfolio_returns, (1 - confidence_level) * 100)

    def _calculate_max_drawdown(self,
                              weights: np.ndarray,
                              returns_data: np.ndarray) -> float:
        """Calculate maximum drawdown"""
        portfolio_returns = np.dot(weights, returns_data)
        cumulative_returns = np.cumprod(1 + portfolio_returns)
        running_max = np.maximum.accumulate(cumulative_returns)
        drawdowns = cumulative_returns / running_max - 1
        return np.min(drawdowns)

    def _calculate_sortino_ratio(self,
                               weights: np.ndarray,
                               returns_data: np.ndarray) -> float:
        """Calculate Sortino ratio (downside risk-adjusted return)"""
        portfolio_returns = np.dot(weights, returns_data)
        excess_returns = np.mean(portfolio_returns) - self.risk_free_rate
        downside_returns = portfolio_returns[portfolio_returns < 0]
        downside_std = np.std(downside_returns) if len(downside_returns) > 0 else np.std(portfolio_returns)
        
        return excess_returns / downside_std if downside_std != 0 else 0.0