from dataclasses import dataclass
from typing import Optional, Dict, Any, List
from enum import Enum
import re

class ValidationSeverity(Enum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"

@dataclass
class ValidationResult:
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    info: List[str]
    enriched_data: Optional[Dict[str, Any]] = None

class LeadValidator:
    """Handles validation of lead data with detailed error reporting."""
    
    def __init__(self):
        self.email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        self.url_pattern = re.compile(
            r'^https?:\/\/'
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'
            r'localhost|'
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
            r'(?::\d+)?'
            r'(?:/?|[/?]\S+)$', re.IGNORECASE
        )

    def validate_lead(self, lead_data: Dict[str, Any]) -> ValidationResult:
        errors = []
        warnings = []
        info = []
        
        # Required fields validation
        if not lead_data.get("company_name"):
            errors.append("Company name is required")
        elif len(lead_data["company_name"].strip()) < 2:
            errors.append("Company name must be at least 2 characters long")
            
        # Email validation
        if "contact_email" in lead_data:
            email = lead_data.get("contact_email")
            if email:
                if not self.email_pattern.match(email):
                    errors.append("Invalid email format")
            else:
                warnings.append("Email field is empty")
        else:
            info.append("No email provided")
            
        # Website validation
        if "website" in lead_data:
            website = lead_data.get("website")
            if website:
                if not self.url_pattern.match(website):
                    errors.append("Invalid website URL format")
            else:
                warnings.append("Website field is empty")
        else:
            info.append("No website provided")
            
        # Additional data quality checks
        if "company_name" in lead_data:
            if lead_data["company_name"].isupper():
                warnings.append("Company name is all uppercase")
            if len(lead_data["company_name"]) > 100:
                warnings.append("Company name is unusually long")
                
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            info=info,
            enriched_data=lead_data if len(errors) == 0 else None
        )
