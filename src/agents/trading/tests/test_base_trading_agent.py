# test_base_trading_agent.py

import pytest
from conftest import trading_agent
import logging

@pytest.mark.asyncio
async def test_agent_initialization(trading_agent):
    """Test that the trading agent initializes correctly."""
    assert trading_agent.positions == {}, "Positions should be initialized as an empty dictionary."
    assert trading_agent.orders == {}, "Orders should be initialized as an empty dictionary."
    assert trading_agent.balances == {}, "Balances should be initialized as an empty dictionary."
    assert trading_agent.latest_prices == {}, "Latest prices should be initialized as an empty dictionary."
    assert trading_agent.trade_history == {}, "Trade history should be initialized as an empty dictionary."
    assert trading_agent.trading_thresholds is not None, "Trading thresholds should be initialized."
    logger = trading_agent.trading_thresholds.trend_strength  # assuming logger is set up
    # If you need to check more attributes, add here



