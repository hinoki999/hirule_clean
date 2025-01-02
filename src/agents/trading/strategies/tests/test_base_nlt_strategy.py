import pytest
from decimal import Decimal
from typing import Dict, Optional
from ...nlt_trading_agent import NLTTradingAgent, TradingConfig, ThresholdConfig
from ..base_nlt_strategy import BaseNLTStrategy

class TestStrategy(BaseNLTStrategy):
    async def analyze_market(self, symbol: str, market_data: Dict) -> Optional[Dict]:
        return {
            "symbol": symbol,
            "action": "buy",
            "confidence": 0.8
        }
        
    async def generate_trade_parameters(self, signal: Dict) -> Dict:
        return {
            "symbol": signal["symbol"],
            "side": signal["action"],
            "amount": "1.0",
            "type": "limit",
            "price": "100.0"
        }

@pytest.fixture
async def strategy():
    config = {
        "min_trade_size": "0.1",
        "max_position_size": "1000.0",
        "risk_per_trade": "0.02",
        "slippage_tolerance": "0.001",
        "thresholds": {
            "config": {
                "volatility_window": 20,
                "volume_window": 20,
                "price_change_threshold": 0.02,
                "volume_change_threshold": 0.5
            }
        }
    }
    agent = NLTTradingAgent(config=config, exchange_pairs=["NLT/USDT"])
    await agent.setup()
    return TestStrategy(agent)

@pytest.mark.asyncio
async def test_strategy_risk_checks(strategy):
    trade_params = {
        "symbol": "NLT/USDT",
        "amount": "0.5",
        "side": "buy",
        "type": "limit",
        "price": "100.0"
    }
    
    assert await strategy.check_risk_limits(trade_params)
    
    # Test exceeding position limit
    large_trade = trade_params.copy()
    large_trade["amount"] = "2000.0"
    assert not await strategy.check_risk_limits(large_trade)
    
    # Test minimum trade size
    small_trade = trade_params.copy()
    small_trade["amount"] = "0.05"
    assert not await strategy.check_risk_limits(small_trade)
