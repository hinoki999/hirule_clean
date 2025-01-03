<<<<<<< ours
import pytest
import logging
import asyncio
from src.agents.protocol_coordinator import ProtocolCoordinator
from src.agents.protocol.mqtt_agent import MQTTAgent
from src.agents.protocol.coap_agent import CoAPAgent
from src.agents.protocol.http_agent import HTTPAgent

@pytest.fixture
async def coordinator():
    coordinator = ProtocolCoordinator()
    yield coordinator
    await coordinator.stop()

@pytest.mark.asyncio
async def test_protocol_coordinator(coordinator):
    # Test initialization
    assert coordinator.agent_id is not None
    assert len(coordinator.protocol_agents) == 0

    # Test agent registration
    mqtt_agent = MQTTAgent()
    coap_agent = CoAPAgent()
    http_agent = HTTPAgent()

    assert coordinator.register_agent(mqtt_agent)
    assert coordinator.register_agent(coap_agent)
    assert coordinator.register_agent(http_agent)
    assert len(coordinator.protocol_agents) == 3

    # Test coordinator operations
    await coordinator.start()
    assert coordinator.is_running

    # Submit and process test task
    task = {
        "type": "http_request",
        "protocol": "HTTP3",
        "content": "Test request"
    }
    task_id = await coordinator.submit_task(task)
    assert task_id is not None

    await asyncio.sleep(0.5)

    await coordinator.stop()
    assert not coordinator.is_running

if __name__ == '__main__':
    pytest.main([__file__])


||||||| base
=======
import pytest
import logging
from src.agents.protocol_coordinator import ProtocolCoordinator
from src.agents.protocol.mqtt_agent import MQTTAgent
from src.agents.protocol.coap_agent import CoAPAgent
from src.agents.protocol.http_agent import HTTPAgent

@pytest.fixture
async def coordinator():
    coordinator = ProtocolCoordinator()
    yield coordinator
    await coordinator.stop()

@pytest.mark.asyncio
async def test_protocol_coordinator(coordinator):
    # Test initialization
    assert coordinator.agent_id is not None
    assert len(coordinator.protocol_agents) == 0

    # Test agent registration
    mqtt_agent = MQTTAgent()
    coap_agent = CoAPAgent()
    http_agent = HTTPAgent()
    
    assert coordinator.register_agent(mqtt_agent)
    assert coordinator.register_agent(coap_agent)
    assert coordinator.register_agent(http_agent)
    assert len(coordinator.protocol_agents) == 3

    # Test coordinator operations
    await coordinator.start()
    assert coordinator.is_running

    # Submit and process test task
    task = {
        "type": "http_request",
        "protocol": "HTTP3",
        "content": "Test request"
    }
    task_id = await coordinator.submit_task(task)
    assert task_id is not None
    
    await asyncio.sleep(0.5)
    
    await coordinator.stop()
    assert not coordinator.is_running

if __name__ == '__main__':
    pytest.main([__file__])
>>>>>>> theirs
