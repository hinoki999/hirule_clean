import pytest
import asyncio
from datetime import datetime
from src.message_system.simulation.market_environment import SimulationEnvironment
from src.message_system.agents.specialized_agents import MarketDataAgent, StrategyAgent

@pytest.mark.asyncio
async def test_simulation_basic():
    sim_env = SimulationEnvironment()
    
    # Add test agents
    market_agent = MarketDataAgent("market_agent", sim_env.message_bus)
    strategy_agent = StrategyAgent("strategy_agent", sim_env.message_bus)
    
    await sim_env.add_agent("market_agent", market_agent)
    await sim_env.add_agent("strategy_agent", strategy_agent)
    
    # Start simulation for a brief period
    async def run_brief_sim():
        await sim_env.start_simulation(
            symbols=["BTC-USD"],
            use_live_data=False
        )
    
    try:
        # Run simulation for 5 seconds
        sim_task = asyncio.create_task(run_brief_sim())
        await asyncio.sleep(5)
        sim_env.stop_simulation()
        await sim_task
    except asyncio.CancelledError:
        pass
    
    # Check metrics were recorded
    metrics = sim_env.get_metrics()
    assert "market_agent" in metrics
    assert "strategy_agent" in metrics
