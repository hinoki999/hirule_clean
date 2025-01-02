import pytest
import pytest_asyncio
from datetime import datetime
from src.enrichment.company import CompanyEnricher, CompanyInfo
from src.enrichment.contact import ContactEnricher, ContactInfo
from src.enrichment.service import EnrichmentService

@pytest.fixture
def sample_lead_data():
    return {
        "company_name": "Test Company",
        "contact_email": "john.doe@testcompany.com",
        "website": "https://testcompany.com"
    }

@pytest.fixture
def invalid_lead_data():
    return {
        "company_name": "",
        "contact_email": "invalid-email",
        "website": "not-a-url"
    }

class TestCompanyEnrichment:
    @pytest.mark.asyncio
    async def test_company_enrichment_success(self):
        #"""Test successful company enrichment#"""
        enricher = CompanyEnricher()
        result = await enricher.enrich_company(
            "Test Company",
            "testcompany.com"
        )

        assert isinstance(result, CompanyInfo)
        assert result.name == "Test Company"
        assert result.domain == "testcompany.com"
        assert result.verified is True
        assert isinstance(result.technologies, list)
        assert isinstance(result.social_profiles, dict)
        assert "linkedin" in result.social_profiles
        assert "twitter" in result.social_profiles

    @pytest.mark.asyncio
    async def test_company_enrichment_no_domain(self):
        #"""Test company enrichment without domain#"""
        enricher = CompanyEnricher()
        result = await enricher.enrich_company("Test Company")

        assert isinstance(result, CompanyInfo)
        assert result.name == "Test Company"
        assert result.domain is None
        assert result.verified is False

    @pytest.mark.asyncio
    async def test_company_enrichment_error_handling(self):
        #"""Test company enrichment error handling#"""
        enricher = CompanyEnricher()
        result = await enricher.enrich_company("")  # Invalid company name

        assert isinstance(result, CompanyInfo)
        assert not result.verified
        assert result.social_profiles is None

class TestContactEnrichment:
    @pytest.mark.asyncio
    async def test_contact_enrichment_success(self):
        #"""Test successful contact enrichment#"""
        enricher = ContactEnricher()
        result = await enricher.enrich_contact(
            "john.doe@testcompany.com",
            "testcompany.com"
        )

        assert isinstance(result, ContactInfo)
        assert result.email == "john.doe@testcompany.com"
        assert result.verified is True
        assert result.first_name == "John"
        assert result.last_name == "Doe"
        assert isinstance(result.social_profiles, dict)

    @pytest.mark.asyncio
    async def test_contact_enrichment_invalid_email(self):
        #"""Test contact enrichment with invalid email#"""
        enricher = ContactEnricher()
        result = await enricher.enrich_contact("invalid-email")

        assert isinstance(result, ContactInfo)
        assert result.email == "invalid-email"
        assert result.verified is False
        assert result.social_profiles is None

    @pytest.mark.asyncio
    async def test_contact_social_profiles(self):
        #"""Test social profile discovery#"""
        enricher = ContactEnricher()
        result = await enricher.enrich_contact(
            "john.doe@testcompany.com",
            "testcompany.com"
        )

        assert result.social_profiles is not None
        assert "linkedin" in result.social_profiles
        assert "twitter" in result.social_profiles

class TestEnrichmentService:
    @pytest.mark.asyncio
    async def test_full_enrichment_success(self, sample_lead_data):
        #"""Test complete enrichment process#"""
        service = EnrichmentService()
        result = await service.enrich_lead(sample_lead_data)

        # Check structure
        assert "original_data" in result
        assert "company_info" in result
        assert "contact_info" in result
        assert "timestamp" in result

        # Check company info
        company_info = result["company_info"]
        assert company_info["name"] == sample_lead_data["company_name"]
        assert company_info["verified"] is True
        assert "technologies" in company_info
        assert "social_profiles" in company_info

        # Check contact info
        contact_info = result["contact_info"]
        assert contact_info["email"] == sample_lead_data["contact_email"]
        assert contact_info["verified"] is True
        assert contact_info["first_name"] == "John"
        assert contact_info["last_name"] == "Doe"
        assert "social_profiles" in contact_info

    @pytest.mark.asyncio
    async def test_enrichment_invalid_data(self, invalid_lead_data):
        #"""Test enrichment with invalid data#"""
        service = EnrichmentService()
        result = await service.enrich_lead(invalid_lead_data)

        assert "original_data" in result

        # Company info should indicate failure
        company_info = result.get("company_info", {})
        assert company_info.get("verified") is False

        # Contact info should indicate failure
        contact_info = result.get("contact_info", {})
        assert contact_info.get("verified") is False

    @pytest.mark.asyncio
    async def test_enrichment_partial_data(self):
        #"""Test enrichment with partial data#"""
        partial_data = {
            "company_name": "Test Company"
            # Missing email and website
        }

        service = EnrichmentService()
        result = await service.enrich_lead(partial_data)

        assert "company_info" in result
        assert result["company_info"]["name"] == "Test Company"
        assert "contact_info" not in result

    @pytest.mark.asyncio
    async def test_parallel_processing(self, sample_lead_data):
        #"""Test that enrichment tasks run in parallel#"""
        service = EnrichmentService()

        start_time = datetime.now()
        result = await service.enrich_lead(sample_lead_data)
        end_time = datetime.now()

        # Both enrichment tasks should complete in roughly the same time
        # as a single task due to parallel processing
        processing_time = (end_time - start_time).total_seconds()
        assert processing_time < 0.3  # Should be much less than sum of individual delays

        assert "company_info" in result
        assert "contact_info" in result


