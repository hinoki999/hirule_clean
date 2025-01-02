<<<<<<< ours
# tests/test_agents/test_semantic_agent.py
import pytest
import pytest_asyncio
import os
from src.agents.semantic_agent import SemanticAgent

@pytest_asyncio.fixture
async def semantic_agent():
    #"""Create and setup a semantic agent for testing#"""
    agent = SemanticAgent()
    await agent.setup()
    yield agent
    await agent.cleanup()

@pytest.mark.asyncio
async def test_semantic_agent_creation(semantic_agent):
    #"""Test that we can create a semantic agent#"""
    assert isinstance(semantic_agent, SemanticAgent)

@pytest.mark.asyncio
async def test_semantic_agent_attributes(semantic_agent):
    #"""Test that semantic agent has expected attributes#"""
    assert hasattr(semantic_agent, 'process_task')
    assert hasattr(semantic_agent, 'process_message')
    assert hasattr(semantic_agent, 'cleanup')

@pytest.mark.asyncio
async def test_semantic_agent_task_processing(semantic_agent):
    #"""Test semantic agent's ability to process tasks#"""
    task_data = {
        "query": "test query",
        "max_results": 1
    }
    result = await semantic_agent.process_task(task_data)
    assert result["status"] == "success"
    assert "output_file" in result

@pytest.mark.asyncio
async def test_semantic_agent_message_handling(semantic_agent):
    #"""Test semantic agent's message handling#"""
    message = {"type": "test", "content": "test message"}
    result = await semantic_agent.process_message(message)
    assert result["status"] == "success"


||||||| base
=======
# tests/test_agents/test_semantic_agent.py
import pytest
import pytest_asyncio
import os
from src.agents.semantic_agent import SemanticAgent

@pytest_asyncio.fixture
async def semantic_agent():
    """Create and setup a semantic agent for testing"""
    agent = SemanticAgent()
    await agent.setup()
    yield agent
    await agent.cleanup()

@pytest.mark.asyncio
async def test_semantic_agent_creation(semantic_agent):
    """Test that we can create a semantic agent"""
    assert isinstance(semantic_agent, SemanticAgent)

@pytest.mark.asyncio
async def test_semantic_agent_attributes(semantic_agent):
    """Test that semantic agent has expected attributes"""
    assert hasattr(semantic_agent, 'process_task')
    assert hasattr(semantic_agent, 'process_message')
    assert hasattr(semantic_agent, 'cleanup')

@pytest.mark.asyncio
async def test_semantic_agent_task_processing(semantic_agent):
    """Test semantic agent's ability to process tasks"""
    task_data = {
        "query": "test query",
        "max_results": 1
    }
    result = await semantic_agent.process_task(task_data)
    assert result["status"] == "success"
    assert "output_file" in result

@pytest.mark.asyncio
async def test_semantic_agent_message_handling(semantic_agent):
    """Test semantic agent's message handling"""
    message = {"type": "test", "content": "test message"}
    result = await semantic_agent.process_message(message)
    assert result["status"] == "success"
>>>>>>> theirs
