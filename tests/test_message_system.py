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
        self.processed_message_ids = set()  # Track processed messages
        
    async def receive_message(self, message: AgentMessage):
        # Check if we've already processed this message to prevent loops
        message_id = f"{message.sender_id}:{message.timestamp}"
        if message_id in self.processed_message_ids:
            return
            
        self.processed_message_ids.add(message_id)
        self.received_messages.append(message)
        
        # Echo back a response
        response_data = {"response_to": message.msg_type, "from": self.agent_id}
        await self.send_message(MessageType.LEARNING_UPDATE, response_data)

@pytest.mark.asyncio
async def test_basic_agent_communication():
    # Setup
    message_bus = MessageBus()
    
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
    assert len(agent1.received_messages) > 0
    assert len(agent2.received_messages) > 0
    assert agent1.received_messages[0].data == test_data
