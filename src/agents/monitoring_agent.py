from src.agents.base import BaseAgent, AgentCapability
from src.core.messaging import Message
from src.monitoring.metrics import MetricsCollector, MetricType
from datetime import datetime, timedelta
import logging
import json

class MonitoringAgent(BaseAgent):
    def __init__(self, agent_id=None, message_bus=None, config=None):
        self.agent_type = "monitoring"
        capabilities = [AgentCapability.BASE]
        super().__init__(agent_id=agent_id, message_bus=message_bus, config=config, capabilities=capabilities)
        self.logger = logging.getLogger(__name__)
        self.metrics = MetricsCollector()

    async def setup(self):
        ###"""Set up monitoring agent###"""
        self.logger.info(f"Setting up {self.agent_type} agent")
        return True

    async def cleanup(self):
        ###"""Clean up monitoring agent###"""
        self.logger.info(f"Cleaning up {self.agent_type} agent")
        return True

    async def process_message(self, message: Message):
        ###"""Process monitoring messages###"""
        if message.message_type == "RECORD_METRIC":
            return self._record_metric(message.payload)
        elif message.message_type == "GET_METRICS":
            return self._get_metrics(message.payload)
        return None

    def _record_metric(self, payload: dict) -> dict:
        ###"""Record a new metric###"""
        try:
            self.metrics.record_metric(
                name=payload["name"],
                value=payload["value"],
                metric_type=MetricType(payload["metric_type"]),
                labels=payload.get("labels")
            )
            return {"status": "success"}
        except Exception as e:
            self.logger.error(f"Error recording metric: {str(e)}")
            return {"status": "error", "message": str(e)}

    def _get_metrics(self, payload: dict) -> dict:
        ###"""Get metrics summary###"""
        try:
            time_window = timedelta(
                seconds=payload.get("time_window_seconds", 3600)
            )
            if payload.get("metric_name"):
                return self.metrics.get_metric_summary(
                    payload["metric_name"],
                    time_window
                )
            return self.metrics.get_all_metrics(time_window)
        except Exception as e:
            self.logger.error(f"Error retrieving metrics: {str(e)}")
            return {"status": "error", "message": str(e)}


