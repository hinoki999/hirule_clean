from typing import Dict, Optional, List
from dataclasses import dataclass
from src.integrations.clearbit import ClearbitClient, ClearbitNotFoundError 
from src.integrations.hunter import HunterClient, HunterNotFoundError

@dataclass
class EnrichmentResult:
    """Data class for enrichment results"""
    company_info: Optional[Dict] = None
    email_patterns: Optional[List[Dict]] = None
    key_contacts: Optional[List[Dict]] = None
    error: Optional[str] = None

class CompanyEnrichmentService:
    def __init__(self, clearbit_api_key: str, hunter_api_key: str):
        self.clearbit_client = ClearbitClient(clearbit_api_key)
        self.hunter_client = HunterClient(hunter_api_key)

    async def __aenter__(self):
        await self.clearbit_client.__aenter__()
        await self.hunter_client.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.clearbit_client.__aexit__(exc_type, exc, tb)
        await self.hunter_client.__aexit__(exc_type, exc, tb)

    async def enrich_company(self, domain: str) -> EnrichmentResult:
        """
        Enrich company information using both Clearbit and Hunter.io
        
        Args:
            domain: Company domain name
            
        Returns:
            EnrichmentResult containing company info and email data
        """
        result = EnrichmentResult()

        try:
            # Get company info from Clearbit
            result.company_info = await self.clearbit_client.enrich_company(domain)
        except ClearbitNotFoundError:
            result.error = f"Company not found in Clearbit: {domain}"
            return result
        except Exception as e:
            result.error = f"Error enriching company data: {str(e)}"
            return result

        try:
            # Get email patterns from Hunter
            hunter_data = await self.hunter_client.domain_search(domain)
            if hunter_data.get("data"):
                result.email_patterns = hunter_data["data"].get("patterns", [])
                result.key_contacts = hunter_data["data"].get("emails", [])
        except HunterNotFoundError:
            # Don"t fail if Hunter doesn"t find anything
            pass
        except Exception as e:
            result.error = f"Error finding email patterns: {str(e)}"

        return result
