from src.agents.base import BaseAgent
from src.core.messaging import Message

class MarketplaceAgent(BaseAgent):
    def __init__(self):
        super().__init__(agent_type="marketplace")
        self._registered_agents = {}

    async def get_registered_agents(self):
        ###"""Return list of all registered agents###"""
        return list(self._registered_agents.values())

    async def _handle_agent_registration(self, message: Message):
        ###"""Handle agent registration requests###"""
        agent_data = message.payload
        self._registered_agents[agent_data["agent_id"]] = agent_data
        return {"status": "success", "message": "Agent registered successfully"}

    async def _handle_agent_search(self, message: Message):
        ###"""Handle agent search requests###"""
        search_criteria = message.payload
        results = []

        for agent in self._registered_agents.values():
            if search_criteria.get("category") == agent.get("category"):
                results.append(agent)

        return results

    async def handle_message(self, message: Message):
        ###"""Route messages to appropriate handlers###"""
        handlers = {
            "REGISTER_AGENT": self._handle_agent_registration,
            "SEARCH_AGENTS": self._handle_agent_search,
        }

        handler = handlers.get(message.message_type)
        if handler:
            return await handler(message)
        return await super().handle_message(message)


