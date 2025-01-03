"""
Tests for error handling and market data processing
"""
import pytest
import asyncio
from typing import Dict
import pandas as pd
import numpy as np
from src.core.error_handler import ErrorHandler, ErrorSeverity
from src.core.market_data_processor import MarketDataProcessor

# Apply asyncio mark to all tests in this module
pytestmark = pytest.mark.asyncio

@pytest.fixture
async def market_processor():
    """Fixture for market data processor with cleanup"""
    config = {
        "symbols": ["NLT/USDT"],
        "max_buffer_size": 100,
        "analysis_interval": 0.1
    }
    
    error_handler = ErrorHandler({})
    processor = MarketDataProcessor(config, error_handler)
    await processor.initialize()
    
    try:
        yield processor
    finally:
        # Ensure cleanup happens even if test fails
        await processor.shutdown()

async def test_error_handler():
    """Test error handling system"""
    config = {"error_ttl": 3600}
    handler = ErrorHandler(config)
    
    test_error = ValueError("Test error")
    context = await handler.handle_error(
        "TestComponent",
        test_error,
        ErrorSeverity.ERROR
    )
    
    assert context is not None
    assert context.component == "TestComponent"
    assert context.error_type == "ValueError"
    assert not context.resolved
    
    async def recovery_strategy(ctx):
        ctx.resolved = True
        
    handler.register_recovery_strategy("ValueError", recovery_strategy)
    context = await handler.handle_error(
        "TestComponent",
        test_error,
        ErrorSeverity.ERROR
    )
    
    assert context.recovery_attempted
    assert context.resolved

async def test_market_data_processor(market_processor):
    """Test market data processing"""
    test_data = {
        "symbol": "NLT/USDT",
        "price": 1.234,
        "volume": 1000.0,
        "bid": 1.233,
        "ask": 1.235,
        "timestamp": 1641234567.0
    }
    
    result = await market_processor.process_market_data(test_data)
    assert result is None  # First point, need at least 2
    
    # Add another point
    test_data["price"] = 1.236
    test_data["timestamp"] = 1641234568.0
    await market_processor.process_market_data(test_data)
    
    # Wait for analysis to complete
    await asyncio.sleep(0.2)
    
    result = market_processor.get_latest_analysis("NLT/USDT")
    assert result is not None
    assert "vwap" in result
    assert "volatility" in result
    assert "trend" in result
    assert "liquidity" in result
