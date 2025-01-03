"""
Test script for NLT Trading System market data handling
"""

import asyncio
import pytest
from src.training.environment.market_data_handler import MarketDataHandler
from src.training.agents.base_agent import BaseAgent

async def test_market_data_fetch():
    """Test basic market data fetching"""
    config = {
        'market_data': {
            'exchange_id': 'binance',
            'symbols': ['BTC/USDT', 'ETH/USDT'],
            'exchange_params': {
                'enableRateLimit': True,
                'rateLimit': 1200
            }
        }
    }
    
    try:
        handler = MarketDataHandler(config['market_data'])
        await handler.initialize()
        
        # Test OHLCV data fetch
        data = await handler.fetch_ohlcv('BTC/USDT', '1m', 100)
        
        # Basic validation
        assert len(data) > 0
        assert all(key in data[0] for key in ['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        
        print("Market data fetch test successful")
        print(f"Sample data point: {data[0]}")
        
    except Exception as e:
        print(f"Test failed: {str(e)}")
        raise

async def test_agent_market_data():
    """Test agent's market data processing"""
    config = {
        'market_data': {
            'exchange_id': 'binance',
            'symbols': ['BTC/USDT'],
            'exchange_params': {
                'enableRateLimit': True
            }
        }
    }
    
    try:
        agent = BaseAgent(config)
        await agent.initialize()
        
        # Test market data processing
        data = await agent.process_market_data('BTC/USDT', '1m')
        
        assert len(data) > 0
        print("Agent market data processing test successful")
        
    except Exception as e:
        print(f"Test failed: {str(e)}")
        raise

def run_tests():
    """Run all tests"""
    asyncio.run(test_market_data_fetch())
    asyncio.run(test_agent_market_data())

if __name__ == "__main__":
    run_tests()
