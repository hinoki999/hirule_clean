from typing import Dict, Optional
from datetime import datetime
import asyncio
import logging
from .base import BaseAgent
from src.integrations.clearbit import ClearbitClient
from src.integrations.hunter import HunterClient
from src.config.api_keys import APIKeys

class EnrichmentService:
    """Handles external data enrichment operations with real APIs"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.api_keys = APIKeys()
        self.api_keys.load_from_env()
        
        try:
            self.clearbit = ClearbitClient(self.api_keys.get_key('clearbit'))
            self.hunter = HunterClient(self.api_keys.get_key('hunter'))
        except ValueError as e:
            self.logger.error(f"Failed to initialize API clients: {str(e)}")
            raise

    async def close(self):
        """Close all API client sessions"""
        await asyncio.gather(
            self.clearbit.close(),
            self.hunter.close()
        )

    async def enrich_lead(self, lead_data: Dict) -> Dict:
        """Enrich lead data using multiple API services"""
        try:
            # ... (previous enrichment code) ...
            
            # Add API-specific enrichment
            if domain:
                clearbit_company = await self.clearbit.enrich_company(domain)
                if "error" not in clearbit_company:
                    enriched_data["company_info"].update({
                        "industry": clearbit_company.get("category", {}).get("industry"),
                        "employee_count": clearbit_company.get("metrics", {}).get("employees"),
                        "linkedin_handle": clearbit_company.get("linkedin", {}).get("handle"),
                        "twitter_handle": clearbit_company.get("twitter", {}).get("handle"),
                        "tech_stack": clearbit_company.get("tech", [])
                    })

            if email:
                # Verify email with Hunter
                email_verification = await self.hunter.verify_email(email)
                if "error" not in email_verification:
                    enriched_data["contact_info"].update({
                        "email_score": email_verification.get("score"),
                        "email_verified": email_verification.get("result") == "deliverable"
                    })
                
                # Enrich person data with Clearbit
                person_data = await self.clearbit.enrich_person(email)
                if "error" not in person_data:
                    enriched_data["contact_info"].update({
                        "title": person_data.get("employment", {}).get("title"),
                        "seniority": person_data.get("employment", {}).get("seniority"),
                        "linkedin_url": person_data.get("linkedin", {}).get("url"),
                        "twitter_url": person_data.get("twitter", {}).get("url")
                    })

            return enriched_data
            
        except Exception as e:
            self.logger.error(f"Enrichment failed: {str(e)}")
            return {
                "original_data": lead_data,
                "error": str(e),
                "company_info": {"verified": False, "error": str(e)},
                "contact_info": {"verified": False, "error": str(e)} if email else None,
                "timestamp": datetime.now().isoformat()
            }
