<<<<<<< ours
from src.agents.base import BaseAgent
from src.core.protocol import ProtocolMessageType, ProtocolMessage
from src.core.utils import SystemMetrics
import asyncio
import logging

class BlockchainAgent(BaseAgent):
    ###"""
    Blockchain Agent for managing blockchain interactions.
    ###"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.metrics = SystemMetrics()



    async def setup(self):
        ###"""Setup blockchain agent.###"""
        self.logger.info(f"Setting up Blockchain Agent {self.agent_id}")
        self.register_handler(ProtocolMessageType.TASK_ASSIGNMENT, self.handle_transaction)
        self.register_handler(ProtocolMessageType.TASK_STATUS, self.handle_status_update)

    async def handle_transaction(self, message: ProtocolMessage):
        ###"""Handle incoming blockchain transaction task.###"""
        transaction_data = message.payload.get("transaction_data")
        try:
            # Simulate zkRollup aggregation
            aggregated_data = await self.aggregate_transactions(transaction_data)
            proof = await self.generate_proof(aggregated_data)

            # Respond with success
            response = self.protocol.create_message(
                message_type=ProtocolMessageType.TASK_RESULT,
                sender=self.agent_id,
                recipient=message.sender,
                payload={"status": "completed", "proof": proof},
                correlation_id=message.message_id
            )
            await self.protocol.send_message(response)
        except Exception as e:
            self.logger.error(f"Transaction processing failed: {str(e)}")
            error_response = self.protocol.create_message(
                message_type=ProtocolMessageType.ERROR,
                sender=self.agent_id,
                recipient=message.sender,
                payload={"error": f"Transaction processing failed: {str(e)}"},
                correlation_id=message.message_id
            )
            await self.protocol.send_message(error_response)

    async def aggregate_transactions(self, transactions):
        ###"""Aggregate transactions for zkRollup.###"""
        self.logger.info("Aggregating transactions for zkRollup")
        # Simulate aggregation logic
        return f"Aggregated {len(transactions)} transactions"

    async def generate_proof(self, aggregated_data):
        ###"""Generate zkProof for aggregated data.###"""
        self.logger.info("Generating zkProof for aggregated data")
        # Simulate proof generation logic
        return f"zkProof for {aggregated_data}"

    async def handle_status_update(self, message: ProtocolMessage):
        ###"""Handle status updates.###"""
        task_status = message.payload.get("status")
        self.logger.info(f"Task status updated: {task_status}")


||||||| base
=======
from src.agents.base import BaseAgent
from src.core.protocol import ProtocolMessageType, ProtocolMessage
from src.core.utils import SystemMetrics
import asyncio
import logging

class BlockchainAgent(BaseAgent):
    """
    Blockchain Agent for managing blockchain interactions.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.metrics = SystemMetrics()



    async def setup(self):
        """Setup blockchain agent."""
        self.logger.info(f"Setting up Blockchain Agent {self.agent_id}")
        self.register_handler(ProtocolMessageType.TASK_ASSIGNMENT, self.handle_transaction)
        self.register_handler(ProtocolMessageType.TASK_STATUS, self.handle_status_update)

    async def handle_transaction(self, message: ProtocolMessage):
        """Handle incoming blockchain transaction task."""
        transaction_data = message.payload.get("transaction_data")
        try:
            # Simulate zkRollup aggregation
            aggregated_data = await self.aggregate_transactions(transaction_data)
            proof = await self.generate_proof(aggregated_data)

            # Respond with success
            response = self.protocol.create_message(
                message_type=ProtocolMessageType.TASK_RESULT,
                sender=self.agent_id,
                recipient=message.sender,
                payload={"status": "completed", "proof": proof},
                correlation_id=message.message_id
            )
            await self.protocol.send_message(response)
        except Exception as e:
            self.logger.error(f"Transaction processing failed: {str(e)}")
            error_response = self.protocol.create_message(
                message_type=ProtocolMessageType.ERROR,
                sender=self.agent_id,
                recipient=message.sender,
                payload={"error": f"Transaction processing failed: {str(e)}"},
                correlation_id=message.message_id
            )
            await self.protocol.send_message(error_response)

    async def aggregate_transactions(self, transactions):
        """Aggregate transactions for zkRollup."""
        self.logger.info("Aggregating transactions for zkRollup")
        # Simulate aggregation logic
        return f"Aggregated {len(transactions)} transactions"

    async def generate_proof(self, aggregated_data):
        """Generate zkProof for aggregated data."""
        self.logger.info("Generating zkProof for aggregated data")
        # Simulate proof generation logic
        return f"zkProof for {aggregated_data}"

    async def handle_status_update(self, message: ProtocolMessage):
        """Handle status updates."""
        task_status = message.payload.get("status")
        self.logger.info(f"Task status updated: {task_status}")
>>>>>>> theirs
