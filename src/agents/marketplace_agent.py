from typing import Dict, Any, Optional, List
from src.agents.base import BaseAgent, AgentCapability
from src.core.messaging import Message
import asyncio
import logging
from datetime import datetime

class MarketplaceCapability(AgentCapability):
    """Extended capabilities for marketplace functionality"""
    MARKETPLACE = "MARKETPLACE"

class MarketplaceAgent(BaseAgent):
    """
    Agent responsible for handling marketplace operations including
    agent registration, discovery, and transaction processing.
    """
    
    def __init__(self, agent_id: Optional[str] = None, **kwargs):
        super().__init__(agent_id=agent_id, capabilities=[MarketplaceCapability.MARKETPLACE], **kwargs)
        self._registered_agents: Dict[str, Dict[str, Any]] = {}
        self._transactions: List[Dict[str, Any]] = []
        self.fee_percentage = 5.0  # 5% marketplace fee

    async def setup(self):
        """Initialize marketplace-specific handlers and resources"""
        self.register_handler("REGISTER_AGENT", self._handle_agent_registration)
        self.register_handler("SEARCH_AGENTS", self._handle_agent_search)
        self.register_handler("PURCHASE_AGENT", self._handle_purchase)
        self.logger.info("MarketplaceAgent initialized")

    async def cleanup(self):
        """Cleanup marketplace resources"""
        self._registered_agents.clear()
        self._transactions.clear()

    async def process_message(self, message: Message):
        """Process marketplace-specific messages"""
        self.logger.debug(f"Processing marketplace message: {message.message_type}")
        # Default message handling if not caught by specific handlers
        pass

    async def _handle_agent_registration(self, message: Message):
        """Handle agent registration requests"""
        agent_data = message.payload
        agent_id = agent_data.get("agent_id")
        
        if not agent_id:
            await self.send_message(
                message.sender,
                "REGISTRATION_FAILED",
                {"error": "Missing agent_id in registration"}
            )
            return

        # Store agent details
        self._registered_agents[agent_id] = {
            **agent_data,
            "registration_time": datetime.now().isoformat(),
            "status": "active"
        }

        await self.send_message(
            message.sender,
            "REGISTRATION_SUCCESS",
            {"agent_id": agent_id}
        )

    async def _handle_agent_search(self, message: Message):
        """Handle agent search requests"""
        search_params = message.payload
        category = search_params.get("category")
        query = search_params.get("query", "").lower()

        # Filter agents based on search criteria
        results = {}
        for agent_id, agent_data in self._registered_agents.items():
            if (not category or agent_data.get("category") == category) and \
               (not query or query in agent_data.get("name", "").lower()):
                results[agent_id] = agent_data

        await self.send_message(
            message.sender,
            "SEARCH_RESULTS",
            {"results": results}
        )

    async def _handle_purchase(self, message: Message):
        """Handle agent purchase transactions"""
        purchase_data = message.payload
        agent_id = purchase_data.get("agent_id")
        buyer_id = message.sender
        
        if agent_id not in self._registered_agents:
            await self.send_message(
                buyer_id,
                "PURCHASE_FAILED",
                {"error": "Agent not found"}
            )
            return

        # Process transaction
        amount = purchase_data.get("amount", 0)
        fee = amount * (self.fee_percentage / 100)
        net_amount = amount - fee

        transaction = {
            "id": f"txn_{len(self._transactions)}",
            "timestamp": datetime.now().isoformat(),
            "agent_id": agent_id,
            "buyer_id": buyer_id,
            "amount": amount,
            "fee": fee,
            "net_amount": net_amount,
            "status": "completed"
        }

        self._transactions.append(transaction)

        # Notify both parties
        await self.send_message(
            buyer_id,
            "PURCHASE_SUCCESS",
            {"transaction": transaction}
        )
        
        seller_id = self._registered_agents[agent_id].get("owner_id")
        if seller_id:
            await self.send_message(
                seller_id,
                "SALE_NOTIFICATION",
                {"transaction": transaction}
            )

    async def get_agent_details(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a registered agent"""
        return self._registered_agents.get(agent_id)

    async def get_transaction_history(self, agent_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get transaction history, optionally filtered by agent"""
        if not agent_id:
            return self._transactions
        
        return [t for t in self._transactions if t["agent_id"] == agent_id]

    async def update_agent_status(self, agent_id: str, status: str):
        """Update the status of a registered agent"""
        if agent_id in self._registered_agents:
            self._registered_agents[agent_id]["status"] = status
            self._registered_agents[agent_id]["last_updated"] = datetime.now().isoformat()