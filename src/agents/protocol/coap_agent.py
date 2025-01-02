import asyncio
import logging
from uuid import uuid4

try:
    import aiocoap
    from aiocoap import resource as resource
except ImportError:
    aiocoap = None
    resource = None

from src.agents.base import BaseAgent, AgentCapability
from src.communication.messages import Message

class CoAPAgent(BaseAgent):
    def __init__(self, agent_id: str = None, coap_port: int = 5683):
        if not agent_id:
            agent_id = f"coap_agent_{str(uuid4())[:8]}"

        super().__init__(agent_id=agent_id, capabilities=[AgentCapability.PROTOCOL])

        self.coap_port = coap_port
        self.protocol = "CoAP"
        self._site = None
        self._server_context = None
        self._listener_task = None
        self.logger = logging.getLogger(self.agent_id)
        self.is_running = False  # Explicit running state

        self.logger.info(f"Initialized CoAPAgent: {agent_id} on port {coap_port}")

    async def setup(self):
        ###"""Initialize the agent with proper error handling###"""
        try:
            await super().setup()
            if aiocoap:
                self.logger.info("aiocoap library detected. Preparing CoAP server resources.")
                self._site = resource.Site()
            else:
                self.logger.warning("aiocoap not installed. CoAP server will be a stub.")
            self.is_running = True
            self.logger.info("CoAPAgent setup complete.")
        except Exception as e:
            self.logger.error(f"Error during setup: {e}")
            self.is_running = False
            raise

    async def start(self):
        ###"""Start the agent explicitly###"""
        if not self.is_running:
            await self.setup()
        await self.post_start()
        self.is_running = True

    async def post_start(self):
        ###"""Post-start initialization with proper error handling###"""
        try:
            await super().post_start()
            if aiocoap:
                self.logger.info("Starting CoAP server context...")
                self._listener_task = asyncio.create_task(self._start_coap_server())
            else:
                self.logger.warning("Skipping CoAP server since aiocoap is missing.")
        except Exception as e:
            self.logger.error(f"Error during post_start: {e}")
            self.is_running = False
            raise

    async def cleanup(self):
        ###"""Enhanced cleanup with proper error handling###"""
        try:
            if self._listener_task and not self._listener_task.done():
                self._listener_task.cancel()
                try:
                    async with asyncio.timeout(5.0):  # Add timeout
                        await self._listener_task
                except (asyncio.CancelledError, asyncio.TimeoutError):
                    self.logger.info("CoAP server listener task cancelled.")
                except Exception as e:
                    self.logger.error(f"Error cancelling listener task: {e}")

            if self._server_context is not None:
                try:
                    async with asyncio.timeout(5.0):  # Add timeout
                        await self._server_context.shutdown()
                    self.logger.info("CoAP server context shutdown complete.")
                except Exception as e:
                    self.logger.error(f"Error shutting down server context: {e}")

            await super().cleanup()
        finally:
            self.is_running = False
            self._site = None
            self._server_context = None
            self._listener_task = None

    async def process_message(self, message: Message):
        ###"""Process messages with enhanced error handling###"""
        try:
            self.logger.info(f"[CoAPAgent] Received Message ID {message.id}, Type: {message.message_type}")
            if message.message_type == "coap_request":
                response_data = await self.process_request(message.content)
                reply = self.message_bus.create_message(
                    sender=self.agent_id,
                    recipient_id=message.sender_id,
                    message_type="coap_response",
                    content=response_data
                )
                await self.message_bus.publish(reply)
            else:
                self.logger.debug(f"Unhandled message type: {message.message_type}")
        except Exception as e:
            self.logger.error(f"Error processing message: {e}")
            raise

    async def process_request(self, request: dict) -> dict:
        ###"""Process requests with input validation###"""
        try:
            if not isinstance(request, dict):
                raise ValueError("Request must be a dictionary")

            self.logger.info(f"Processing CoAP request object: {request}")

            # Validate required fields
            if request.get('method') not in ['GET', 'POST', 'PUT', 'DELETE']:
                return {
                    "status": "error",
                    "message": f"Invalid method: {request.get('method')}"
                }

            response = {
                "status": "success",
                "protocol": self.protocol,
                "agent_id": self.agent_id,
                "message": f"Processed request using {self.protocol}"
            }
            return response
        except Exception as e:
            self.logger.error(f"Error in process_request: {str(e)}")
            return {
                "status": "error",
                "message": str(e)
            }

    async def _start_coap_server(self):
        ###"""Start CoAP server with enhanced error handling and monitoring###"""
        if not aiocoap:
            self.logger.warning("aiocoap not installed. Skipping server startup.")
            return

        self.logger.info(f"CoAP server listening on UDP port {self.coap_port}...")
        try:
            self._server_context = await aiocoap.Context.create_server_context(
                self._site,
                bind=(None, self.coap_port)
            )
            await self._server_context.async_run()
        except asyncio.CancelledError:
            self.logger.info("CoAP server context received cancellation.")
            raise
        except Exception as e:
            self.logger.error(f"Fatal error in CoAP server context: {e}")
            self.is_running = False
            raise


