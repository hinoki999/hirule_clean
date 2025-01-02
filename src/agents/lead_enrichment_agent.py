<<<<<<< ours
from src.agents.base import BaseAgent, AgentCapability
from src.core.messaging import Message
from src.validation.lead_validator import LeadValidator, ValidationResult
from src.metrics.collector import MetricsCollector
from src.enrichment.service import EnrichmentService
from datetime import datetime, timedelta
from enum import Enum
import logging
import json

class LeadEnrichmentAgent(BaseAgent):
    def __init__(self, agent_id=None, message_bus=None, config=None):
        self.agent_type = "lead_enrichment"
        capabilities = [AgentCapability.BASE]
        super().__init__(agent_id=agent_id, message_bus=message_bus, config=config, capabilities=capabilities)
        self._processed_leads = {}
        self.logger = logging.getLogger(__name__)
        self.validator = LeadValidator()
        self.metrics = MetricsCollector(window_size=timedelta(hours=1))
        self.enrichment_service = EnrichmentService()

    async def setup(self):
        ###"""Implementation of abstract setup method###"""
        self.logger.info(f"Setting up {self.agent_type} agent")
        return True

    async def cleanup(self):
        ###"""Implementation of abstract cleanup method###"""
        self.logger.info(f"Cleaning up {self.agent_type} agent")
        return True

    async def process_message(self, message: Message):
        ###"""Implementation of abstract process_message method###"""
        if message.message_type == "ENRICH_LEAD":
            return await self.enrich_lead(message.payload)
        elif message.message_type == "GET_METRICS":
            return self.get_metrics()
        return None

    def get_metrics(self) -> dict:
        ###"""Get current metrics###"""
        return {
            "metrics": self.metrics.get_current_metrics(),
            "error_distribution": self.metrics.get_error_distribution()
        }

    def _format_validation_result(self, validation_result: ValidationResult) -> dict:
        ###"""Format validation results for logging and response###"""
        return {
            "validation_status": "valid" if validation_result.is_valid else "invalid",
            "errors": validation_result.errors,
            "warnings": validation_result.warnings,
            "info": validation_result.info
        }

    async def enrich_lead(self, lead_data: dict) -> dict:
        ###"""Enrich lead data with validation and external enrichment.###"""
        lead_id = f"lead_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}"
        metric = self.metrics.start_processing()

        try:
            # Validate the lead data
            validation_result = self.validator.validate_lead(lead_data)

            enriched_data = {
                "lead_id": lead_id,
                "original_data": lead_data,
                "processed_at": datetime.now().isoformat(),
                "validation_details": self._format_validation_result(validation_result),
                "enrichment_status": "pending"
            }

            if not validation_result.is_valid:
                error_msg = "Validation failed"
                self.logger.error(f"Lead validation failed: {json.dumps(enriched_data['validation_details'])}")
                enriched_data.update({
                    "enrichment_status": "failed",
                    "error": error_msg
                })
                metric.complete(
                    success=False,
                    validation_status="invalid",
                    error_type="validation_error",
                    warning_count=len(validation_result.warnings)
                )
                return enriched_data

            # Perform external enrichment
            try:
                enrichment_results = await self.enrichment_service.enrich_lead(lead_data)
                enriched_data.update({
                    "enrichment_status": "completed",
                    "enrichment_data": enrichment_results
                })
            except Exception as e:
                self.logger.error(f"Enrichment failed for lead {lead_id}: {str(e)}")
                enriched_data.update({
                    "enrichment_status": "partial",
                    "enrichment_error": str(e)
                })

            # Store processed lead
            self._processed_leads[lead_id] = enriched_data
            self.logger.info(f"Successfully processed lead {lead_id}")

            metric.complete(
                success=True,
                validation_status="valid",
                warning_count=len(validation_result.warnings)
            )

        except Exception as e:
            error_msg = str(e)
            self.logger.error(f"Failed to process lead: {error_msg}")
            enriched_data = {
                "lead_id": lead_id,
                "original_data": lead_data,
                "processed_at": datetime.now().isoformat(),
                "enrichment_status": "failed",
                "error": error_msg
            }

            metric.complete(
                success=False,
                validation_status="error",
                error_type="processing_error",
                warning_count=0
            )

        return enriched_data


||||||| base
=======
ZnJvbSBzcmMuYWdlbnRzLmJhc2UgaW1wb3J0IEJhc2VBZ2VudApmcm9tIHNyYy5jb3JlLm1lc3NhZ2luZyBpbXBvcnQgTWVzc2FnZQpmcm9tIGRhdGV0aW1lIGltcG9ydCBkYXRldGltZQppbXBvcnQgbG9nZ2luZwoKY2xhc3MgTGVhZEVucmljaG1lbnRBZ2VudChCYXNlQWdlbnQpOgogICAgZGVmIF9faW5pdF9fKHNlbGYpOgogICAgICAgIHN1cGVyKCkuX19pbml0X18oYWdlbnRfdHlwZT0ibGVhZF9lbnJpY2htZW50IikKICAgICAgICBzZWxmLl9wcm9jZXNzZWRfbGVhZHMgPSB7fQogICAgICAgIHNlbGYubG9nZ2VyID0gbG9nZ2luZy5nZXRMb2dnZXIoX19uYW1lX18pCiAgICAgICAgCiAgICBhc3luYyBkZWYgZW5yaWNoX2xlYWQoc2VsZiwgbGVhZF9kYXRhOiBkaWN0KSAtPiBkaWN0OgogICAgICAgICIiIgogICAgICAgIEVucmljaCBsZWFkIGRhdGEgd2l0aCBiYXNpYyB2YWxpZGF0aW9uIGFuZCBzdHJ1Y3R1cmUuCiAgICAgICAgRGVzaWduZWQgZm9yIG1pbmltYWwgaW1wbGVtZW50YXRpb24gdG8gcGFzcyBpbml0aWFsIHRlc3RzLgogICAgICAgICIiIgogICAgICAgIGxlYWRfaWQgPSBmImxlYWRfe2RhdGV0aW1lLm5vdygpLnN0cmZ0aW1lKCclWS1tLWRfJUgtJU0tJVMnKX0iCiAgICAgICAgCiAgICAgICAgZW5yaWNoZWRfZGF0YSA9IHsKICAgICAgICAgICAgImxlYWRfaWQiOiBsZWFkX2lkLAogICAgICAgICAgICAib3JpZ2luYWxfZGF0YSI6IGxlYWRfZGF0YSwKICAgICAgICAgICAgInByb2Nlc3NlZF9hdCI6IGRhdGV0aW1lLm5vdygpLmlzb2Zvcm1hdCgpLAogICAgICAgICAgICAiZW5yaWNobWVudF9zdGF0dXMiOiAicGVuZGluZyIKICAgICAgICB9CiAgICAgICAgCiAgICAgICAgdHJ5OgogICAgICAgICAgICAjIEJhc2ljIHZhbGlkYXRpb24KICAgICAgICAgICAgaWYgbm90IGxlYWRfZGF0YS5nZXQoImNvbXBhbnlfbmFtZSIpOgogICAgICAgICAgICAgICAgcmFpc2UgVmFsdWVFcnJvcigiQ29tcGFueSBuYW1lIGlzIHJlcXVpcmVkIikKICAgICAgICAgICAgCiAgICAgICAgICAgIGVucmljaGVkX2RhdGEudXBkYXRlKHsKICAgICAgICAgICAgICAgICJlbnJpY2htZW50X3N0YXR1cyI6ICJjb21wbGV0ZWQiLAogICAgICAgICAgICAgICAgImVucmljaG1lbnRfZGF0YSI6IHsKICAgICAgICAgICAgICAgICAgICAiY29tcGFueV9uYW1lIjogbGVhZF9kYXRhWyJjb21wYW55X25hbWUiXSwKICAgICAgICAgICAgICAgICAgICAiY29udGFjdF9lbWFpbCI6IGxlYWRfZGF0YS5nZXQoImNvbnRhY3RfZW1haWwiKSwKICAgICAgICAgICAgICAgICAgICAid2Vic2l0ZSI6IGxlYWRfZGF0YS5nZXQoIndlYnNpdGUiKSwKICAgICAgICAgICAgICAgICAgICAidmFsaWRhdGlvbl90aW1lc3RhbXAiOiBkYXRldGltZS5ub3coKS5pc29mb3JtYXQoKQogICAgICAgICAgICAgICAgfQogICAgICAgICAgICB9KQogICAgICAgICAgICAKICAgICAgICAgICAgIyBTdG9yZSBwcm9jZXNzZWQgbGVhZAogICAgICAgICAgICBzZWxmLl9wcm9jZXNzZWRfbGVhZHNbbGVhZF9pZF0gPSBlbnJpY2hlZF9kYXRhCiAgICAgICAgICAgIHNlbGYubG9nZ2VyLmluZm8oZiJTdWNjZXNzZnVsbHkgcHJvY2Vzc2VkIGxlYWQge2xlYWRfaWR9IikKICAgICAgICAgICAgCiAgICAgICAgZXhjZXB0IEV4Y2VwdGlvbiBhcyBlOgogICAgICAgICAgICBzZWxmLmxvZ2dlci5lcnJvcihmIkZhaWxlZCB0byBwcm9jZXNzIGxlYWQ6IHtzdHIoZSl9IikKICAgICAgICAgICAgZW5yaWNoZWRfZGF0YS51cGRhdGUoewogICAgICAgICAgICAgICAgImVucmljaG1lbnRfc3RhdHVzIjogImZhaWxlZCIsCiAgICAgICAgICAgICAgICAiZXJyb3IiOiBzdHIoZSkKICAgICAgICAgICAgfSkKICAgICAgICAgICAgCiAgICAgICAgcmV0dXJuIGVucmljaGVkX2RhdGEKICAgIAogICAgYXN5bmMgZGVmIGhhbmRsZV9tZXNzYWdlKHNlbGYsIG1lc3NhZ2U6IE1lc3NhZ2UpOgogICAgICAgICIiIlJvdXRlIGFuZCBoYW5kbGUgaW5jb21pbmcgbWVzc2FnZXMiIiIKICAgICAgICBpZiBtZXNzYWdlLm1lc3NhZ2VfdHlwZSA9PSAiRU5SSUNIX0xFQUQiOgogICAgICAgICAgICByZXR1cm4gYXdhaXQgc2VsZi5lbnJpY2hfbGVhZChtZXNzYWdlLnBheWxvYWQpCiAgICAgICAgcmV0dXJuIGF3YWl0IHN1cGVyKCkuaGFuZGxlX21lc3NhZ2UobWVzc2FnZSk=
>>>>>>> theirs
