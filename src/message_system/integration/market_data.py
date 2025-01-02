from datetime import datetime
from typing import Dict, List, Optional, Any
import aiohttp
import asyncio
import json
from src.message_system.core.message_bus import MessageBus, MessageType, AgentMessage

class ExchangeConfig:
    """Configuration for different exchanges"""
    BINANCE = {
        "rest": "https://api.binance.com/api/v3",
        "ws": "wss://stream.binance.com:9443/ws",
        "endpoints": {
            "klines": "/klines",
            "time": "/time",
            "ticker": "/ticker/24hr"
        }
    }
    
    KRAKEN = {
        "rest": "https://api.kraken.com/0/public",
        "ws": "wss://ws.kraken.com",
        "endpoints": {
            "ohlc": "/OHLC",
            "time": "/Time",
            "ticker": "/Ticker"
        }
    }
    
    COINBASE = {
        "rest": "https://api.pro.coinbase.com",
        "ws": "wss://ws-feed.pro.coinbase.com",
        "endpoints": {
            "candles": "/products/{}/candles",
            "time": "/time",
            "ticker": "/products/{}/ticker"
        }
    }

class MarketDataIntegration:
    """Handles integration with multiple market data sources"""
    def __init__(self, message_bus: MessageBus, exchange: str = "binance"):
        self.message_bus = message_bus
        self.active_feeds: Dict[str, Dict] = {}
        self.price_cache: Dict[str, float] = {}
        self.orderbook_cache: Dict[str, Dict] = {}
        self.exchange = exchange.lower()
        self.config = self._get_exchange_config()
        
    def _get_exchange_config(self) -> Dict:
        """Get configuration for selected exchange"""
        configs = {
            "binance": ExchangeConfig.BINANCE,
            "kraken": ExchangeConfig.KRAKEN,
            "coinbase": ExchangeConfig.COINBASE
        }
        return configs.get(self.exchange)
        
    async def get_historical_data(self, symbol: str, interval: str = "1m", limit: int = 1000):
        """Fetch historical data from exchange"""
        try:
            timeout = aiohttp.ClientTimeout(total=30)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                if self.exchange == "binance":
                    return await self._get_binance_historical(session, symbol, interval, limit)
                elif self.exchange == "kraken":
                    return await self._get_kraken_historical(session, symbol, interval, limit)
                elif self.exchange == "coinbase":
                    return await self._get_coinbase_historical(session, symbol, interval, limit)
                else:
                    raise ValueError(f"Unsupported exchange: {self.exchange}")
                    
    async def _get_binance_historical(self, session: aiohttp.ClientSession, symbol: str, interval: str, limit: int):
        """Get historical data from Binance"""
        url = f"{self.config['rest']}{self.config['endpoints']['klines']}"
        params = {
            "symbol": symbol.upper().replace('-', ''),
            "interval": interval,
            "limit": limit
        }
        
        async with session.get(url, params=params) as response:
            if response.status == 200:
                data = await response.json()
                return self._format_binance_data(data)
            return []
            
    async def _get_kraken_historical(self, session: aiohttp.ClientSession, symbol: str, interval: str, limit: int):
        """Get historical data from Kraken"""
        url = f"{self.config['rest']}{self.config['endpoints']['ohlc']}"
        # Convert interval to Kraken format
        interval_map = {"1m": 1, "5m": 5, "15m": 15, "30m": 30, "1h": 60, "4h": 240}
        params = {
            "pair": symbol,
            "interval": interval_map.get(interval, 1)
        }
        
        async with session.get(url, params=params) as response:
            if response.status == 200:
                data = await response.json()
                return self._format_kraken_data(data)
            return []
            
    async def _get_coinbase_historical(self, session: aiohttp.ClientSession, symbol: str, interval: str, limit: int):
        """Get historical data from Coinbase"""
        url = f"{self.config['rest']}{self.config['endpoints']['candles']}".format(symbol)
        # Convert interval to Coinbase format
        interval_map = {"1m": 60, "5m": 300, "15m": 900, "1h": 3600, "6h": 21600, "1d": 86400}
        params = {
            "granularity": interval_map.get(interval, 60)
        }
        
        async with session.get(url, params=params) as response:
            if response.status == 200:
                data = await response.json()
                return self._format_coinbase_data(data)
            return []
            
    def _format_binance_data(self, raw_data: List) -> List[Dict]:
        """Format Binance data into standard format"""
        formatted_data = []
        for candle in raw_data:
            formatted_data.append({
                "timestamp": datetime.fromtimestamp(candle[0] / 1000),
                "open": float(candle[1]),
                "high": float(candle[2]),
                "low": float(candle[3]),
                "close": float(candle[4]),
                "volume": float(candle[5])
            })
        return formatted_data
        
    def _format_kraken_data(self, raw_data: Dict) -> List[Dict]:
        """Format Kraken data into standard format"""
        formatted_data = []
        if 'result' in raw_data:
            for pair_data in raw_data['result'].values():
                for candle in pair_data:
                    formatted_data.append({
                        "timestamp": datetime.fromtimestamp(candle[0]),
                        "open": float(candle[1]),
                        "high": float(candle[2]),
                        "low": float(candle[3]),
                        "close": float(candle[4]),
                        "volume": float(candle[6])
                    })
        return formatted_data
        
    def _format_coinbase_data(self, raw_data: List) -> List[Dict]:
        """Format Coinbase data into standard format"""
        formatted_data = []
        for candle in raw_data:
            formatted_data.append({
                "timestamp": datetime.fromtimestamp(candle[0]),
                "open": float(candle[3]),
                "high": float(candle[2]),
                "low": float(candle[1]),
                "close": float(candle[4]),
                "volume": float(candle[5])
            })
        return formatted_data
