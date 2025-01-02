import pytest
import asyncio
from datetime import datetime
from src.message_system.core.message_bus import MessageBus, MessageType, AgentMessage
from src.message_system.agents.base_agent import BaseAgent
from src.message_system.simulation.sim_environment import SimulationEnvironment

class TestAgent(BaseAgent):
    def __init__(self, agent_id: str, message_bus: MessageBus):
        super().__init__(agent_id, message_bus)
        self.received_messages = []
        
    async def receive_message(self, message: AgentMessage):
        self.received_messages.append(message)
        # Echo back a response
        response_data = {"response_to": message.data, "from": self.agent_id}
        await self.send_message(MessageType.LEARNING_UPDATE, response_data)

@pytest.mark.asyncio
async def test_basic_agent_communication():
    # Setup
    message_bus = MessageBus()
    sim_env = SimulationEnvironment()
    
    # Create test agents
    agent1 = TestAgent("agent1", message_bus)
    agent2 = TestAgent("agent2", message_bus)
    
    # Subscribe agents to messages
    message_bus.subscribe(MessageType.MARKET_DATA, agent1.receive_message)
    message_bus.subscribe(MessageType.LEARNING_UPDATE, agent2.receive_message)
    
    # Send test message
    test_data = {"test": "data", "timestamp": str(datetime.now())}
    test_message = AgentMessage(
        msg_type=MessageType.MARKET_DATA,
        sender_id="test",
        timestamp=datetime.now(),
        data=test_data
    )
    
    # Publish message
    await message_bus.publish(test_message)
    
    # Allow time for message processing
    await asyncio.sleep(0.1)
    
    # Verify
    assert len(agent1.received_messages) == 1
    assert agent1.received_messages[0].data == test_data
    assert len(agent2.received_messages) == 1  # Should have received the echo response
    assert agent2.received_messages[0].data["response_to"] == test_data

@pytest.mark.asyncio
async def test_simulation_environment():
    sim_env = SimulationEnvironment()
    message_bus = MessageBus()
    
    # Create test agents
    agent1 = TestAgent("agent1", message_bus)
    agent2 = TestAgent("agent2", message_bus)
    
    # Add agents to simulation
    sim_env.add_agent("agent1", agent1)
    sim_env.add_agent("agent2", agent2)
    
    # Run simulation step
    await sim_env.step()
    
    # Verify simulation metrics
    metrics = sim_env.get_performance_metrics()
    assert "agent1" in metrics
    assert "agent2" in metrics

if __name__ == "__main__":
    asyncio.run(test_basic_agent_communication())
    asyncio.run(test_simulation_environment())