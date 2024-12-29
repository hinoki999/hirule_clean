# src/integrations/hunter.py

from typing import Dict
from .base import BaseAPIClient, APIConfig, APIError
import asyncio

class HunterError(APIError):
    """Hunter-specific API error."""
    pass

class HunterNotFoundError(HunterError):
    """Raised when Hunter cannot find data for the given input."""
    pass

class HunterInvalidError(HunterError):
    """Raised when input data is invalid."""
    pass

class HunterClient(BaseAPIClient):
    """Client for interacting with the Hunter.io API."""

    def __init__(self, api_key: str):
        """
        Initializes the HunterClient with the provided API key.

        Args:
            api_key (str): The API key for authenticating with the Hunter API.
        """
        config = APIConfig(
            api_key=api_key,
            base_url="https://api.hunter.io/v2",
            timeout=30,
            max_retries=3,
            rate_limit=100
        )
        super().__init__(config)

    async def _handle_response_error(self, response):
        """Handle Hunter-specific error responses."""
        if response.status == 404:
            raise HunterNotFoundError("Resource not found", status_code=404)
        elif response.status == 400:
            raise HunterInvalidError("Invalid input parameters", status_code=400)
        elif response.status == 429:
            # Hunter has specific rate limit error handling
            retry_after = response.headers.get("Retry-After", "60")  # Default to 60 seconds if not provided
            raise HunterError(
                f"Rate limit exceeded. Retry after {retry_after} seconds",
                status_code=429
            )
        await super()._handle_response_error(response)

    async def domain_search(self, domain: str) -> Dict:
        """
        Search for email addresses associated with a domain.

        Args:
            domain (str): The domain to search for.

        Returns:
            Dict: The response data containing emails.
        """
        try:
            params = {"domain": domain}
            return await self._request("GET", "/domain-search", params=params)
        except HunterError as e:
            if isinstance(e, HunterNotFoundError):
                raise HunterNotFoundError(f"No email patterns found for domain: {domain}") from e
            raise

    async def email_finder(self, domain: str, first_name: str, last_name: str) -> Dict:
        """
        Find an email address using domain and name.

        Args:
            domain (str): The domain to search within.
            first_name (str): The first name of the person.
            last_name (str): The last name of the person.

        Returns:
            Dict: The response data containing the email and score.
        """
        try:
            params = {
                "domain": domain,
                "first_name": first_name,
                "last_name": last_name
            }
            return await self._request("GET", "/email-finder", params=params)
        except HunterError as e:
            if isinstance(e, HunterInvalidError):
                raise HunterInvalidError("Invalid input parameters") from e
            raise

    async def email_verifier(self, email: str) -> Dict:
        """
        Verify the deliverability of an email address.

        Args:
            email (str): The email address to verify.

        Returns:
            Dict: The response data containing the verification status and score.
        """
        try:
            params = {"email": email}
            return await self._request("GET", "/email-verifier", params=params)
        except HunterError as e:
            if isinstance(e, HunterInvalidError):
                raise HunterInvalidError(f"Invalid email address: {email}") from e
            raise
