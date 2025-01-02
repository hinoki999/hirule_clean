from typing import Dict, List, Any
from datetime import datetime
from ..core.message_bus import MessageBus, MessageType, AgentMessage
from ..core.learning_environment import AgentLearningEnvironment

class SimulationEnvironment:
    def __init__(self):
        self.message_bus = MessageBus()
        self.learning_env = AgentLearningEnvironment()
        self.agents: Dict[str, Any] = {}
        self.sim_time: datetime = datetime.now()
        self.market_data: Dict[str, List[Dict]] = {}
        
    def add_agent(self, agent_id: str, agent: Any):
        """Add an agent to the simulation"""
        self.agents[agent_id] = agent
        
    async def step(self):
        """Advance simulation by one step"""
        self.sim_time += datetime.timedelta(minutes=1)
        await self.publish_market_data()
        await self.process_agent_actions()
        
    async def publish_market_data(self):
        """Publish market data to agents"""
        for asset, data in self.market_data.items():
            message = AgentMessage(
                msg_type=MessageType.MARKET_DATA,
                sender_id="simulation",
                timestamp=self.sim_time,
                data={"asset": asset, "data": data}
            )
            await self.message_bus.publish(message)
            
    async def process_agent_actions(self):
        """Process actions from all agents"""
        for agent_id, agent in self.agents.items():
            if hasattr(agent, "act"):
                action = await agent.act()
                await self.process_action(agent_id, action)
                
    async def process_action(self, agent_id: str, action: Dict):
        """Process a single agent's action"""
        # Implement action processing logic
        pass
        
    def get_performance_metrics(self) -> Dict[str, Dict]:
        """Get performance metrics for all agents"""
        metrics = {}
        for agent_id in self.agents:
            metrics[agent_id] = self.learning_env.get_learning_metrics(agent_id)
        return metrics
        
    def reset(self):
        """Reset simulation state"""
        self.sim_time = datetime.now()
        self.market_data = {}
        for agent in self.agents.values():
            if hasattr(agent, "reset"):
                agent.reset()
