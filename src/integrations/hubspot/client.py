import json
from typing import Optional, Dict, Any
import redis
import logging
from datetime import datetime
from hubspot import HubSpot
from hubspot.crm.companies.exceptions import ApiException
from .exceptions import HubSpotError, RateLimitExceededError, HubSpotAPIError

logger = logging.getLogger(__name__)

class HubSpotClient:
    def __init__(
        self,
        access_token: str,
        redis_client: Optional[redis.Redis] = None,
        rate_limiter: Optional[Any] = None,
        cache_ttl: int = 3600
    ):
        self.client = HubSpot(access_token=access_token)
        self.rate_limiter = rate_limiter
        self.cache_ttl = cache_ttl
        self.redis_client = redis_client

    def _get_cache_key(self, domain: str) -> str:
        return f"hubspot:company:{domain}"

    async def get_company_data(self, domain: str) -> Optional[Dict[str, Any]]:
        cache_key = self._get_cache_key(domain)

        if self.redis_client:
            try:
                cached_data = self.redis_client.get(cache_key)
                if cached_data:
                    try:
                        if isinstance(cached_data, bytes):
                            return json.loads(cached_data.decode('utf-8'))
                        return json.loads(cached_data)
                    except json.JSONDecodeError:
                        logger.warning("Error decoding cached data")
            except redis.RedisError as e:
                logger.warning(f"Redis cache error: {str(e)}")

        if self.rate_limiter:
            can_proceed = await self.rate_limiter.can_make_request()
            if not can_proceed:
                raise RateLimitExceededError("Rate limit exceeded")

        try:
            filter_groups = [{
                "filters": [{
                    "propertyName": "domain",
                    "operator": "EQ",
                    "value": domain
                }]
            }]

            properties = [
                "name", "domain", "website", "industry",
                "description", "phone", "address"
            ]

            companies = self.client.crm.companies.search_api.do_search({
                "filterGroups": filter_groups,
                "properties": properties,
                "limit": 1
            })

            if companies.results:
                company_data = {
                    "id": companies.results[0].id,
                    "properties": companies.results[0].properties,
                    "created_at": companies.results[0].created_at,
                    "updated_at": companies.results[0].updated_at
                }

                if self.redis_client:
                    try:
                        self.redis_client.setex(
                            cache_key,
                            self.cache_ttl,
                            json.dumps(company_data)
                        )
                    except redis.RedisError as e:
                        logger.warning(f"Redis caching error: {str(e)}")

                return company_data

            return None

        except ApiException as e:
            logger.error(f"HubSpot API error: {str(e)}")
            raise HubSpotAPIError(f"HubSpot API error: {str(e)}")


