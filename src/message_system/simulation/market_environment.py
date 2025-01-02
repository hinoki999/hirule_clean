from datetime import datetime
from typing import Dict, List, Optional, Any  # Added Any import
import aiohttp
import asyncio
import json
from src.message_system.core.message_bus import MessageBus, MessageType, AgentMessage

class MarketEnvironment:
    """Handles both historical and live market data"""
    def __init__(self, message_bus: MessageBus):
        self.message_bus = message_bus
        self.current_prices: Dict[str, float] = {}
        self.historical_data: Dict[str, List[Dict]] = {}
        self.live_feeds: Dict[str, asyncio.Task] = {}
        self.api_endpoints = {
            "binance": "wss://stream.binance.com:9443/ws/",
            "coinbase": "wss://ws-feed.pro.coinbase.com"
        }
        
    async def start_live_feed(self, symbol: str, exchange: str = "binance"):
        """Start live market data feed"""
        if symbol in self.live_feeds:
            return
            
        if exchange == "binance":
            ws_symbol = symbol.lower().replace('-', '')
            endpoint = f"{self.api_endpoints['binance']}{ws_symbol}@trade"
            self.live_feeds[symbol] = asyncio.create_task(
                self._binance_websocket_feed(endpoint, symbol)
            )
            
    async def _binance_websocket_feed(self, endpoint: str, symbol: str):
        """Handle Binance WebSocket feed"""
        async with aiohttp.ClientSession() as session:
            async with session.ws_connect(endpoint) as ws:
                async for msg in ws:
                    if msg.type == aiohttp.WSMsgType.TEXT:
                        data = json.loads(msg.data)
                        await self._process_live_data(symbol, data)
                        
    async def _process_live_data(self, symbol: str, data: Dict):
        """Process incoming live market data"""
        price = float(data.get('p', 0))
        if price > 0:
            self.current_prices[symbol] = price
            await self._broadcast_price_update(symbol, price)
            
    async def _broadcast_price_update(self, symbol: str, price: float):
        """Broadcast price updates to all subscribed agents"""
        message = AgentMessage(
            msg_type=MessageType.MARKET_DATA,
            sender_id="market_environment",
            timestamp=datetime.now(),
            data={
                "symbol": symbol,
                "price": price,
                "type": "price_update"
            }
        )
        await self.message_bus.publish(message)

class SimulationEnvironment:
    """Main simulation environment coordinating all components"""
    def __init__(self):
        self.message_bus = MessageBus()
        self.market_env = MarketEnvironment(self.message_bus)
        self.agents: Dict[str, Any] = {}
        self.running: bool = False
        self.start_time: Optional[datetime] = None
        self.performance_metrics: Dict[str, List[float]] = {}
        
    async def add_agent(self, agent_id: str, agent: Any):
        """Add an agent to the simulation"""
        self.agents[agent_id] = agent
        self.performance_metrics[agent_id] = []
        
    async def start_simulation(self, symbols: List[str], use_live_data: bool = False):
        """Start the simulation with specified symbols"""
        self.running = True
        self.start_time = datetime.now()
        
        if use_live_data:
            for symbol in symbols:
                await self.market_env.start_live_feed(symbol)
        
        while self.running:
            await self._simulation_step()
            await asyncio.sleep(1)  # Control simulation speed
            
    async def _simulation_step(self):
        """Execute one step of the simulation"""
        # Update agent states
        for agent_id, agent in self.agents.items():
            if hasattr(agent, 'update'):
                await agent.update()
                
        # Record performance metrics
        await self._record_metrics()
        
    async def _record_metrics(self):
        """Record performance metrics for all agents"""
        for agent_id, agent in self.agents.items():
            if hasattr(agent, 'get_performance'):
                metric = await agent.get_performance()
                self.performance_metrics[agent_id].append(metric)
                
    def stop_simulation(self):
        """Stop the simulation"""
        self.running = False
        
    def get_metrics(self) -> Dict[str, List[float]]:
        """Get performance metrics for all agents"""
        return self.performance_metrics.copy()
