import pytest
from decimal import Decimal
from ..nlt_trading_agent import NLTTradingAgent
from ..messages import TradingMessageTypes

@pytest.fixture
async def nlt_agent():
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
    agent = NLTTradingAgent(
        config=config,
        exchange_pairs=["NLT/USDT", "NLT/BTC"]
    )
    await agent.setup()
    return agent

@pytest.mark.asyncio
async def test_nlt_agent_initialization(nlt_agent):
    assert nlt_agent.exchange_pairs == ["NLT/USDT", "NLT/BTC"]
    assert hasattr(nlt_agent.config, "thresholds")
    assert hasattr(nlt_agent.config.thresholds, "config")

@pytest.mark.asyncio
async def test_market_data_handling(nlt_agent):
    test_data = {
        "type": TradingMessageTypes.MARKET_DATA.value,
        "payload": {
            "symbol": "NLT/USDT",
            "last_price": "1.234",
            "volume": "100000"
        }
    }
    
    await nlt_agent.process_message(test_data)
    assert nlt_agent.latest_prices["NLT/USDT"] == "1.234"
