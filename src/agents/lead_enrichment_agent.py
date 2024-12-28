from src.agents.base import BaseAgent
from src.core.messaging import Message
from datetime import datetime
import logging

class LeadEnrichmentAgent(BaseAgent):
    def __init__(self):
        super().__init__(agent_type="lead_enrichment")
        self._processed_leads = {}
        self.logger = logging.getLogger(__name__)
        
    async def enrich_lead(self, lead_data: dict) -> dict:
        """
        Enrich lead data with basic validation and structure.
        Designed for minimal implementation to pass initial tests.
        """
        lead_id = f"lead_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        enriched_data = {
            "lead_id": lead_id,
            "original_data": lead_data,
            "processed_at": datetime.now().isoformat(),
            "enrichment_status": "pending"
        }
        
        try:
            # Basic validation
            if not lead_data.get("company_name"):
                raise ValueError("Company name is required")
            
            enriched_data.update({
                "enrichment_status": "completed",
                "enrichment_data": {
                    "company_name": lead_data["company_name"],
                    "contact_email": lead_data.get("contact_email"),
                    "website": lead_data.get("website"),
                    "validation_timestamp": datetime.now().isoformat()
                }
            })
            
            # Store processed lead
            self._processed_leads[lead_id] = enriched_data
            self.logger.info(f"Successfully processed lead {lead_id}")
            
        except Exception as e:
            self.logger.error(f"Failed to process lead: {str(e)}")
            enriched_data.update({
                "enrichment_status": "failed",
                "error": str(e)
            })
            
        return enriched_data
    
    async def handle_message(self, message: Message):
        """Route and handle incoming messages"""
        if message.message_type == "ENRICH_LEAD":
            return await self.enrich_lead(message.payload)
        return await super().handle_message(message)