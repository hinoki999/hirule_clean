<<<<<<< ours
﻿class MessageBus:
    def __init__(self):
        self.subscribers = {}
    
    async def subscribe(self, topic: str, callback):
        if topic not in self.subscribers:
            self.subscribers[topic] = []
        self.subscribers[topic].append(callback)
||||||| base
=======
# src/communication/message_bus.py
import asyncio
import logging
from collections import defaultdict
from typing import Dict, List, Callable
from datetime import datetime, UTC
from .messages import Message, MessageStatus

class MessageBus:
    def __init__(self):
        self.logger = logging.getLogger('message_bus')
        self.logger.debug("Initializing MessageBus")
        self.subscribers = defaultdict(list)
        self.message_queue = asyncio.Queue()
        self.message_history = {}
        self.is_running = False
        self._processing_task = None
        self.logger.debug("MessageBus initialized successfully")

    async def start(self):
        """Start the message bus and message processing"""
        self.logger.debug("Starting message bus...")
        if not self.is_running:
            self.is_running = True
            self.logger.debug("Creating message processing task")
            self._processing_task = asyncio.create_task(self._process_messages())
            self.logger.info("Message bus started")
            await asyncio.sleep(0.1)  # Allow task to start

    async def stop(self):
        """Stop the message bus gracefully"""
        self.logger.debug("Stopping message bus...")
        if self.is_running:
            self.is_running = False
            if self._processing_task:
                self.logger.debug("Cancelling processing task")
                self._processing_task.cancel()
                try:
                    await self._processing_task
                except asyncio.CancelledError:
                    self.logger.debug("Processing task cancelled successfully")
                finally:
                    self._processing_task = None
            self.logger.info("Message bus stopped")

    async def _process_messages(self):
        """Process messages from the queue"""
        self.logger.debug("Message processing task started")
        while self.is_running:
            try:
                # Use wait_for to prevent hanging
                message = await asyncio.wait_for(
                    self.message_queue.get(), 
                    timeout=0.5
                )
                self.logger.debug(f"Processing message {message.id}")
                
                try:
                    message.update_status(MessageStatus.PROCESSING)
                    
                    if message.message_type in self.subscribers:
                        subscriber_count = len(self.subscribers[message.message_type])
                        self.logger.debug(f"Found {subscriber_count} subscribers for message type {message.message_type}")
                        for callback in self.subscribers[message.message_type]:
                            try:
                                await callback(message)
                                self.logger.debug(f"Message {message.id} delivered to subscriber")
                            except Exception as e:
                                self.logger.error(f"Error in subscriber callback: {str(e)}")
                    else:
                        self.logger.debug(f"No subscribers found for message type {message.message_type}")
                    
                    # Always mark as delivered after processing, even if no subscribers
                    message.update_status(MessageStatus.DELIVERED)
                except Exception as e:
                    self.logger.error(f"Error processing message {message.id}: {str(e)}")
                    message.update_status(MessageStatus.FAILED)
                finally:
                    self.message_queue.task_done()
                    self.logger.debug(f"Message {message.id} processing complete")
            
            except asyncio.TimeoutError:
                # Normal timeout on queue.get(), continue the loop
                continue
            except asyncio.CancelledError:
                self.logger.debug("Message processing task received cancel signal")
                # Clean up any remaining messages
                while not self.message_queue.empty():
                    try:
                        message = self.message_queue.get_nowait()
                        message.update_status(MessageStatus.FAILED)
                        self.message_queue.task_done()
                        self.logger.debug(f"Marked message {message.id} as failed during shutdown")
                    except asyncio.QueueEmpty:
                        break
                raise
            except Exception as e:
                self.logger.error(f"Error in message processing loop: {str(e)}")
                await asyncio.sleep(0.1)

    async def publish(self, message: Message) -> bool:
        """Publish a message"""
        try:
            self.logger.debug(f"Publishing message {message.id}")
            if not self.is_running:
                self.logger.error("Cannot publish - message bus is not running")
                return False
                
            message.update_status(MessageStatus.QUEUED)
            await self.message_queue.put(message)
            self.message_history[message.id] = message
            self.logger.debug(f"Message {message.id} published successfully")
            return True
        except Exception as e:
            self.logger.error(f"Error publishing message: {str(e)}")
            return False

    async def subscribe(self, message_type: str, callback: Callable):
        """Subscribe to message type"""
        self.logger.debug(f"Adding subscriber for message type: {message_type}")
        self.subscribers[message_type].append(callback)
        self.logger.debug(f"Subscriber added successfully for {message_type}")
>>>>>>> theirs
