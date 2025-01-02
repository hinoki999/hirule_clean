# src/agents/semantic_coordinator.py
async def _process_tasks(self):
    #"""Process tasks from the queue#"""
    while self.is_running:
        try:
            if self.task_queue.empty():
                await asyncio.sleep(0.1)
                continue

            task = await self.task_queue.get()
            logging.info(f"Processing task: {task['task_id']}")

            # Basic round-robin distribution among available agents
            if self.semantic_agents:
                agent = list(self.semantic_agents.values())[0]  # For now, just use first agent
                result = await agent.process_task(task)
                logging.info(f"Task {task['task_id']} processed: {result}")
            else:
                logging.warning(f"No agents available to process task {task['task_id']}")

            self.task_queue.task_done()

        except Exception as e:
            logging.error(f"Error processing task: {str(e)}")
            await asyncio.sleep(0.1)  # Prevent tight loop on errors


