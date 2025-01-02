import sys
import os

# Add the src directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

import asyncio
import logging
from datetime import datetime
from agents.load_balancer import LoadBalancer, AgentStatus

async def test_load_balancer():
    # Setup logging
    logging.basicConfig(level=logging.INFO,
                       format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger('main')

    # Initialize load balancer
    lb = LoadBalancer(max_tasks_per_agent=3)

    # Register test agents with different capabilities
    agents = {
        'agent1': ['DATA_COMPRESSION', 'SEMANTIC_ANALYSIS'],
        'agent2': ['MODEL_TRAINING', 'DATA_COMPRESSION'],
        'agent3': ['SEMANTIC_ANALYSIS', 'MODEL_TRAINING']
    }

    for agent_id, capabilities in agents.items():
        lb.register_agent(agent_id, capabilities)

    # Simulate task assignments
    tasks = [
        (['DATA_COMPRESSION'], 2.0),
        (['SEMANTIC_ANALYSIS'], 1.5),
        (['MODEL_TRAINING'], 3.0),
        (['DATA_COMPRESSION'], 1.0),
        (['SEMANTIC_ANALYSIS'], 2.5),
    ]

    # Assign tasks and verify load distribution
    for i, (capabilities, processing_time) in enumerate(tasks):
        agent_id = lb.find_best_agent(capabilities)
        if agent_id:
            logger.info(f"Assigning task {i+1} to {agent_id}")
            lb.task_started(agent_id)

            # Simulate task processing
            await asyncio.sleep(0.1)  # Simulate some work

            # Complete task
            lb.task_completed(agent_id, processing_time)

            # Log current system load
            system_load = lb.get_system_load()
            logger.info(f"Current system load: {system_load}")
        else:
            logger.warning(f"No suitable agent found for task {i+1}")

    # Verify final load distribution
    final_load = lb.get_system_load()
    logger.info(f"Final system load distribution: {final_load}")

if __name__ == "__main__":
    asyncio.run(test_load_balancer())


