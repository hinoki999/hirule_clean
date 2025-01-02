from typing import Dict, Optional
from .base import BaseAPIClient, APIConfig, APIError

class ClearbitError(APIError):
    ###"""Clearbit specific API error###"""
    pass

class ClearbitNotFoundError(ClearbitError):
    ###"""Raised when Clearbit cannot find data for the given input###"""
    pass

class ClearbitClient(BaseAPIClient):
    def __init__(self, api_key: str):
        config = APIConfig(
            api_key=api_key,
            base_url="https://person.clearbit.com/v2",
            timeout=30,
            max_retries=3,
            rate_limit=600  # Clearbit's free tier limit
        )
        super().__init__(config)

    async def _handle_response_error(self, response):
        ###"""Handle Clearbit-specific error responses###"""
        if response.status == 402:
            raise ClearbitError("Query limit exceeded or payment required", status_code=402)
        elif response.status == 404:
            raise ClearbitNotFoundError("Resource not found", status_code=404)
        elif response.status == 422:
            raise ClearbitError("Validation failed - check input parameters", status_code=422)
        await super()._handle_response_error(response)

    async def enrich_company(self, domain: str) -> Dict:
        ###"""
        Enrich company data using Clearbit's Company API

        Args:
            domain: Company domain name

        Raises:
            ClearbitNotFoundError: When company data cannot be found
            ClearbitError: For Clearbit-specific errors
            APIError: For general API errors
        ###"""
        try:
            return await self._request("GET", f"/companies/find?domain={domain}")
        except ClearbitError as e:
            if isinstance(e, ClearbitNotFoundError):
                # Optionally transform to a more specific error message
                raise ClearbitNotFoundError(f"No company data found for domain: {domain}")
            raise

    async def enrich_person(self, email: str) -> Dict:
        ###"""
        Enrich person data using Clearbit's Person API

        Args:
            email: Person's email address

        Raises:
            ClearbitNotFoundError: When person data cannot be found
            ClearbitError: For Clearbit-specific errors
            APIError: For general API errors
        ###"""
        try:
            return await self._request("GET", f"/people/find?email={email}")
        except ClearbitError as e:
            if isinstance(e, ClearbitNotFoundError):
                raise ClearbitNotFoundError(f"No person data found for email: {email}")
            raise


