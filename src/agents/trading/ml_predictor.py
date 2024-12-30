from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from decimal import Decimal
import numpy as np
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler

@dataclass
class TradeCostFeatures:
    """Features for trade cost prediction"""
    trade_size: float  # Absolute trade size
    trade_notional: float  # Trade value in USD
    relative_size: float  # Trade size relative to average volume
    volatility: float  # Historical volatility
    bid_ask_spread: float  # Current spread
    market_impact: float  # Estimated market impact
    time_of_day: float  # Hour of day (0-23)
    is_weekend: bool  # Weekend flag

class MLCostPredictor:
    """Machine learning based trade cost prediction"""
    
    def __init__(self, lookback_window: int = 100):
        self.lookback_window = lookback_window
        self.model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            min_samples_split=5
        )
        self.scaler = StandardScaler()
        self.is_trained = False
        self.historical_costs: List[Dict] = []
        
    def _extract_features(self, 
                         trade_size: Decimal,
                         symbol: str,
                         risk_manager,
                         timestamp: datetime) -> TradeCostFeatures:
        """Extract features for cost prediction"""
        # Get price and volume data
        price = float(risk_manager.price_history[symbol][-1])
        trade_notional = float(trade_size) * price
        
        # Calculate volatility
        returns = list(risk_manager.returns_history[symbol])
        volatility = np.std(returns) * np.sqrt(252) if returns else 0.0
        
        # Estimate bid-ask spread (simplified)
        spread = 0.001 * price  # 10 bps default spread
        
        # Basic market impact estimate
        avg_volume = 1000000  # Placeholder - would come from market data
        relative_size = abs(float(trade_size) * price) / avg_volume
        market_impact = 0.1 * np.sqrt(relative_size)  # Square root impact model
        
        # Time features
        time_of_day = timestamp.hour + timestamp.minute / 60.0
        is_weekend = timestamp.weekday() >= 5
        
        return TradeCostFeatures(
            trade_size=float(trade_size),
            trade_notional=trade_notional,
            relative_size=relative_size,
            volatility=volatility,
            bid_ask_spread=spread,
            market_impact=market_impact,
            time_of_day=time_of_day,
            is_weekend=is_weekend
        )
        
    def _features_to_array(self, features: TradeCostFeatures) -> np.ndarray:
        """Convert features to array for model"""
        return np.array([
            features.trade_size,
            features.trade_notional,
            features.relative_size,
            features.volatility,
            features.bid_ask_spread,
            features.market_impact,
            features.time_of_day,
            float(features.is_weekend)
        ]).reshape(1, -1)
        
    def record_trade_cost(self,
                         trade_size: Decimal,
                         symbol: str,
                         actual_cost: float,
                         risk_manager,
                         timestamp: Optional[datetime] = None):
        """Record actual trade cost for training"""
        timestamp = timestamp or datetime.now()
        features = self._extract_features(trade_size, symbol, risk_manager, timestamp)
        
        self.historical_costs.append({
            'features': features,
            'cost': actual_cost
        })
        
        # Keep only recent history
        if len(self.historical_costs) > self.lookback_window:
            self.historical_costs = self.historical_costs[-self.lookback_window:]
            
    def train_model(self):
        """Train the cost prediction model"""
        if len(self.historical_costs) < 10:  # Minimum required samples
            return
            
        # Prepare training data
        X = np.array([
            self._features_to_array(record['features'])[0]
            for record in self.historical_costs
        ])
        y = np.array([record['cost'] for record in self.historical_costs])
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Train model
        self.model.fit(X_scaled, y)
        self.is_trained = True
        
    def predict_cost(self,
                    trade_size: Decimal,
                    symbol: str,
                    risk_manager,
                    timestamp: Optional[datetime] = None) -> float:
        """Predict transaction cost for a trade"""
        timestamp = timestamp or datetime.now()
        features = self._extract_features(trade_size, symbol, risk_manager, timestamp)
        X = self._features_to_array(features)
        
        if not self.is_trained:
            # Fallback to simple model if not enough data
            return self._simple_cost_estimate(trade_size, symbol, risk_manager)
            
        X_scaled = self.scaler.transform(X)
        predicted_cost = float(self.model.predict(X_scaled)[0])
        
        # Ensure prediction is positive and reasonable
        return max(0.0, min(predicted_cost, float(trade_size) * 0.01))  # Cap at 1%
        
    def _simple_cost_estimate(self,
                            trade_size: Decimal,
                            symbol: str,
                            risk_manager) -> float:
        """Simple cost estimate when ML model isn't ready"""
        price = float(risk_manager.price_history[symbol][-1])
        trade_value = abs(float(trade_size) * price)
        
        # Simple model: spread + linear impact
        spread_cost = trade_value * 0.001  # 10 bps spread
        impact_cost = trade_value * trade_value * 1e-7  # Quadratic impact
        
        return float(spread_cost + impact_cost)
        
    def get_model_confidence(self) -> float:
        """Get confidence score for the model"""
        if not self.is_trained or len(self.historical_costs) < 10:
            return 0.0
            
        # Use R-squared score as confidence
        X = np.array([
            self._features_to_array(record['features'])[0]
            for record in self.historical_costs
        ])
        y = np.array([record['cost'] for record in self.historical_costs])
        X_scaled = self.scaler.transform(X)
        
        return float(self.model.score(X_scaled, y))