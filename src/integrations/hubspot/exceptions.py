from hubspot.crm.companies import ApiException

class HubSpotError(Exception):
    ###"""Base exception for HubSpot-related errors###"""
    pass

class RateLimitExceededError(HubSpotError):
    ###"""Raised when API rate limit is exceeded###"""
    pass

class HubSpotAPIError(HubSpotError):
    ###"""Raised when HubSpot API returns an error###"""
    pass

class CacheError(HubSpotError):
    ###"""Raised when there's an error with the cache###"""
    pass


