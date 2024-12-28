from src.agents.base import BaseAgent
from src.core.messaging import Message
from datetime import datetime

class LeadEnrichmentAgent(BaseAgent):
    def __init__(self):
        super().__init__(agent_type="lead_enrichment")
        self._processed_leads = {}
        
    async def enrich_lead(self, lead_data: dict) -> dict:
        """
        Enrich lead data with additional information and validation.
        
        Args:
            lead_data (dict): Basic lead information including:
                - company_name (str)
                - contact_email (str, optional)
                - website (str, optional)
                
        Returns:
            dict: Enriched lead data with additional fields
        """
        # Generate a unique ID for this lead
        lead_id = f"lead_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Store the original data
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
                
            # Store for processing
            self._processed_leads[lead_id] = enriched_data
            
            # Initially just validate and structure the data
            # Will expand with actual enrichment in next iteration
            enriched_data.update({
                "enrichment_status": "completed",
                "validation_passed": True,
                "enrichment_data": {
                    "company_name": lead_data.get("company_name"),
                    "contact_email": lead_data.get("contact_email"),
                    "website": lead_data.get("website"),
                    # We'll add more enriched fields here
                }
            })
            
        except Exception as e:
            enriched_data.update({
                "enrichment_status": "failed",
                "error": str(e)
            })
            
        return enriched_data
    
    async def handle_message(self, message: Message):
        """Handle incoming enrichment requests"""
        if message.message_type == "ENRICH_LEAD":
            return await self.enrich_lead(message.payload)
        return await super().handle_message(message)
