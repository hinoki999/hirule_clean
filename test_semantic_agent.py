import pytest
import pytest_asyncio
import json
import os
from src.agents.semantic_agent import SemanticAgent

@pytest.fixture(scope="module")
async def setup_test_env():
    """Setup test environment with required directories and config"""
    os.makedirs("config", exist_ok=True)
    os.makedirs("results", exist_ok=True)
    
    test_config = {
        "api_key": os.getenv('OPENAI_API_KEY'),
        "endpoint": "https://api.openai.com/v1"
    }
    with open("config/api_config.json", "w") as f:
        json.dump(test_config, f)

    yield

    # Cleanup
    if os.path.exists("config/api_config.json"):
        os.remove("config/api_config.json")
    for file in os.listdir("results"):
        os.remove(os.path.join("results", file))
    os.rmdir("results")
    os.rmdir("config")

@pytest.fixture
async def semantic_agent():
    agent = SemanticAgent(test_mode=False)
    await agent.setup()
    yield agent
    await agent.stop()

@pytest.mark.asyncio
async def test_semantic_agent_process_task(setup_test_env, semantic_agent):
    task_data = {
        "query": "What are three interesting facts about quantum computing?",
        "max_results": 1
    }
    
    result = await semantic_agent.process_task(task_data)
    assert result["status"] == "success", f"Task failed with error: {result.get('error', 'Unknown error')}"
    assert "output_file" in result
    assert os.path.exists(result["output_file"])

    # Verify output
    with open(result["output_file"], "r") as f:
        analysis = json.load(f)
        print("\nAnalysis results:", json.dumps(analysis, indent=2))

@pytest.mark.asyncio
async def test_semantic_agent_analyze(setup_test_env, semantic_agent):
    result = await semantic_agent.analyze(
        "What are three interesting facts about quantum computing?",
        max_results=1
    )
    
    assert result["status"] == "success"
    assert os.path.exists(result["output_file"])
    
    with open(result["output_file"], "r") as f:
        analysis = json.load(f)
        assert isinstance(analysis, dict), "Analysis output should be a dictionary"