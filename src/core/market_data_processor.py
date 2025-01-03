"""
Market data processing and analysis system
"""
from typing import Dict, List, Optional
import numpy as np
import pandas as pd
import logging
from dataclasses import dataclass
from datetime import datetime
import asyncio
import time
from .error_handler import ErrorHandler, ErrorSeverity, ErrorContext

logger = logging.getLogger(__name__)

@dataclass
class MarketSnapshot:
    timestamp: float
    symbol: str
    price: float
    volume: float
    bid: float
    ask: float
    depth: Dict[str, List[float]]

class MarketDataProcessor:
    def __init__(self, config: Dict, error_handler: ErrorHandler):
        self.config = config
        self.error_handler = error_handler
        self.data_buffer: Dict[str, List[MarketSnapshot]] = {}
        self.analysis_results: Dict[str, Dict] = {}
        self.processing_tasks: Dict[str, asyncio.Task] = {}
        self._running = False

    async def initialize(self):
        """Initialize the processor"""
        try:
            self._running = True
            # Register error handlers
            self.error_handler.register_error_callback(
                "DataProcessingError",
                self._handle_processing_error
            )
            
            # Start background processing tasks
            for symbol in self.config.get("symbols", []):
                self.data_buffer[symbol] = []
                self.processing_tasks[symbol] = asyncio.create_task(
                    self._process_symbol_data(symbol)
                )
                
        except Exception as e:
            await self.error_handler.handle_error(
                "MarketDataProcessor",
                e,
                ErrorSeverity.CRITICAL
            )

    async def shutdown(self):
        """Cleanup and shutdown processor"""
        logger.debug("Shutting down market data processor")
        self._running = False
        
        # Cancel all processing tasks
        for symbol, task in self.processing_tasks.items():
            if not task.done():
                logger.debug(f"Cancelling task for {symbol}")
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    logger.debug(f"Task cancelled for {symbol}")
                except Exception as e:
                    logger.error(f"Error cancelling task for {symbol}: {e}")
        
        self.processing_tasks.clear()
        logger.debug("Market data processor shutdown complete")

    async def process_market_data(self, data: Dict) -> Optional[Dict]:
        """Process incoming market data"""
        try:
            symbol = data.get("symbol")
            if not symbol:
                raise ValueError("Market data missing symbol")
                
            # Create market snapshot
            snapshot = MarketSnapshot(
                timestamp=data.get("timestamp", time.time()),
                symbol=symbol,
                price=data.get("price", 0.0),
                volume=data.get("volume", 0.0),
                bid=data.get("bid", 0.0),
                ask=data.get("ask", 0.0),
                depth=data.get("depth", {"bids": [], "asks": []})
            )
            
            # Add to buffer
            if symbol not in self.data_buffer:
                self.data_buffer[symbol] = []
            self.data_buffer[symbol].append(snapshot)
            
            # Trim buffer if needed
            max_buffer = self.config.get("max_buffer_size", 1000)
            if len(self.data_buffer[symbol]) > max_buffer:
                self.data_buffer[symbol] = self.data_buffer[symbol][-max_buffer:]
                
            return self.get_latest_analysis(symbol)
            
        except Exception as e:
            await self.error_handler.handle_error(
                "MarketDataProcessor",
                e,
                ErrorSeverity.ERROR
            )
            return None

    def get_latest_analysis(self, symbol: str) -> Optional[Dict]:
        """Get latest analysis results for a symbol"""
        return self.analysis_results.get(symbol)
            
    async def _process_symbol_data(self, symbol: str):
        """Background task to process data for a symbol"""
        try:
            while self._running:
                if symbol in self.data_buffer and len(self.data_buffer[symbol]) >= 2:
                    df = pd.DataFrame([
                        {
                            "timestamp": s.timestamp,
                            "price": s.price,
                            "volume": s.volume,
                            "bid": s.bid,
                            "ask": s.ask
                        }
                        for s in self.data_buffer[symbol]
                    ])
                    
                    analytics = {
                        "vwap": self._calculate_vwap(df),
                        "volatility": self._calculate_volatility(df),
                        "trend": self._calculate_trend(df),
                        "liquidity": self._calculate_liquidity(df),
                        "timestamp": time.time()
                    }
                    
                    self.analysis_results[symbol] = analytics
                    
                await asyncio.sleep(self.config.get("analysis_interval", 0.1))
                
        except asyncio.CancelledError:
            logger.info(f"Processing task cancelled for {symbol}")
            raise
        except Exception as e:
            await self.error_handler.handle_error(
                "MarketDataProcessor",
                e,
                ErrorSeverity.ERROR
            )
            
    def _calculate_vwap(self, df: pd.DataFrame) -> float:
        """Calculate Volume Weighted Average Price"""
        return float((df["price"] * df["volume"]).sum() / df["volume"].sum())
        
    def _calculate_volatility(self, df: pd.DataFrame) -> float:
        """Calculate price volatility"""
        return float(df["price"].std())
        
    def _calculate_trend(self, df: pd.DataFrame) -> Dict:
        """Calculate price trend indicators"""
        ema_short = float(df["price"].ewm(span=20).mean().iloc[-1])
        ema_long = float(df["price"].ewm(span=50).mean().iloc[-1])
        return {
            "ema_short": ema_short,
            "ema_long": ema_long,
            "trend_strength": ema_short - ema_long
        }
        
    def _calculate_liquidity(self, df: pd.DataFrame) -> Dict:
        """Calculate liquidity metrics"""
        spread = df["ask"] - df["bid"]
        return {
            "average_spread": float(spread.mean()),
            "spread_volatility": float(spread.std()),
            "volume_profile": float(df["volume"].sum())
        }
        
    async def _handle_processing_error(self, context: ErrorContext):
        """Handle data processing errors"""
        logger.error(f"Data processing error in {context.component}: {context.message}")
        # Implement specific recovery logic here
