from unittest.mock import MagicMock, Mock

class MockHubSpotResponse:
    def __init__(self, results=None):
        self.results = results or []

class MockSearchAPI:
    def __init__(self, results=None):
        # Make do_search a MagicMock
        self.do_search = MagicMock(return_value=MockHubSpotResponse(results or []))

class MockCompaniesAPI:
    def __init__(self, results=None):
        self.search_api = MockSearchAPI(results)

class MockCRMAPI:
    def __init__(self, results=None):
        self.companies = MockCompaniesAPI(results)

class MockHubSpotClient:
    def __init__(self, results=None):
        self.crm = MockCRMAPI(results)

def create_mock_company(
    id='123',
    name='Test Company',
    domain='test.com',
    created_at='2024-01-01T00:00:00Z',
    updated_at='2024-01-01T00:00:00Z'
):
    company = Mock()
    company.id = id
    company.properties = {
        'name': name,
        'domain': domain
    }
    company.created_at = created_at
    company.updated_at = updated_at
    return company

# Mock Exceptions
class MockApiException(Exception):
    pass

class MockUnauthorizedException(MockApiException):
    pass


