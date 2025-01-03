"""
Market Data Handler for NLT Trading System
Integrates CCXT for universal market data access
"""

from ccxt import Exchange
from typing import Dict, List
import numpy as np

class MarketDataHandler:
    def __init__(self, config: Dict):
        self.config = config
        self.exchange = None
        self.symbols = config.get('symbols', [])
        self.initialized = False
        
    async def initialize(self):
        """Initialize connection to exchange"""
        try:
            exchange_id = self.config.get('exchange_id', 'binance')
            self.exchange = Exchange({
                'enableRateLimit': True,
                **self.config.get('exchange_params', {})
            })
            self.initialized = True
        except Exception as e:
            raise Exception(f"Failed to initialize market data handler: {str(e)}")
            
    async def fetch_ohlcv(self, symbol: str, timeframe: str = '1m', limit: int = 100) -> List[Dict]:
        """Fetch OHLCV data for given symbol"""
        if not self.initialized:
            await self.initialize()
        try:
            ohlcv = await self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            return self.format_ohlcv_data(ohlcv)
        except Exception as e:
            raise Exception(f"Failed to fetch OHLCV data: {str(e)}")
            
    def format_ohlcv_data(self, ohlcv_data: List) -> List[Dict]:
        """Format OHLCV data into structured format"""
        formatted_data = []
        for candle in ohlcv_data:
            formatted_data.append({
                'timestamp': candle[0],
                'open': candle[1],
                'high': candle[2],
                'low': candle[3],
                'close': candle[4],
                'volume': candle[5]
            })
        return formatted_data
