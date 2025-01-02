import pytest
from datetime import datetime
from src.communication.messages import Message, MessageStatus, MessagePriority

def test_message_creation():
    #"""Test basic message creation#"""
    message = Message(
        sender_id="agent_1",
        recipient_id="agent_2",
        message_type="test_message",
        content={"test": "data"}
    )

    assert message.sender_id == "agent_1"
    assert message.recipient_id == "agent_2"
    assert message.message_type == "test_message"
    assert message.content == {"test": "data"}
    assert message.status == MessageStatus.CREATED
    assert len(message.status_history) == 1

def test_message_status_update():
    #"""Test message status updates#"""
    message = Message(
        sender_id="agent_1",
        recipient_id="agent_2",
        message_type="test_message",
        content={"test": "data"}
    )

    message.update_status(MessageStatus.QUEUED)
    assert message.status == MessageStatus.QUEUED
    assert len(message.status_history) == 2


