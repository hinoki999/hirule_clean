import aiohttp
import asyncio
import random
from dataclasses import dataclass
from typing import Optional, Dict, Any
from .rate_limiter import RateLimiter

class APIError(Exception):
    ###"""Base exception for API errors###"""
    def __init__(self, message: str, status_code: Optional[int] = None):
        super().__init__(message)
        self.status_code = status_code

class RateLimitError(APIError):
    ###"""Raised when API rate limit is exceeded###"""
    pass

class AuthenticationError(APIError):
    ###"""Raised when API authentication fails###"""
    pass

class ServerError(APIError):
    ###"""Raised when API server returns an error###"""
    pass

@dataclass
class APIConfig:
    api_key: str
    base_url: str
    timeout: int = 30
    max_retries: int = 3
    rate_limit: int = 60
    retry_delay_base: float = 2.0

class BaseAPIClient:
    def __init__(self, config: APIConfig):
        self.config = config
        self._session: Optional[aiohttp.ClientSession] = None
        self._rate_limiter = RateLimiter(config.rate_limit)

    async def __aenter__(self):
        if not self._session:
            headers = {
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json",
            }
            self._session = aiohttp.ClientSession(headers=headers)
        return self

    async def __aexit__(self, exc_type, exc, tb):
        if self._session:
            await self._session.close()
            self._session = None

    async def close(self):
        if self._session:
            await self._session.close()
            self._session = None

    def _should_retry(self, attempt: int, error: Exception) -> bool:
        ###"""Determine if request should be retried based on error type###"""
        if attempt >= self.config.max_retries:
            return False

        if isinstance(error, aiohttp.ServerTimeoutError):
            return True
        if isinstance(error, aiohttp.ClientResponseError):
            return error.status >= 500
        if isinstance(error, (aiohttp.ServerDisconnectedError, asyncio.TimeoutError)):
            return True
        if isinstance(error, ServerError):
            return True
        return False

    async def _handle_response_error(self, response: aiohttp.ClientResponse) -> None:
        ###"""Handle error responses with appropriate custom exceptions###"""
        if response.status == 401:
            raise AuthenticationError("Invalid API key", status_code=401)
        elif response.status == 429:
            raise RateLimitError("Rate limit exceeded", status_code=429)
        elif response.status >= 500:
            raise ServerError(f"Server error: {response.status}", status_code=response.status)
        else:
            response.raise_for_status()

    async def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        if not self._session:
            await self.__aenter__()

        url = f"{self.config.base_url}{endpoint}"
        kwargs["timeout"] = self.config.timeout
        if params:
            kwargs["params"] = params
        if json:
            kwargs["json"] = json

        last_error = None
        for attempt in range(self.config.max_retries + 1):
            try:
                if not await self._rate_limiter.acquire():
                    raise RateLimitError("Rate limit exceeded")

                response = await self._session.request(method, url, **kwargs)
                if response.status != 200:
                    await self._handle_response_error(response)
                return await response.json()

            except Exception as e:
                last_error = e
                if not self._should_retry(attempt, e):
                    break

                delay = self.config.retry_delay_base ** attempt * (0.5 + random.random())
                await asyncio.sleep(delay)

        raise last_error


