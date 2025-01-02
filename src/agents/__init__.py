<<<<<<< ours

||||||| base
=======
"""
Hirule Agents Package
Contains all agent-related implementations for the Hirule system.
"""
from src.agents.base import BaseAgent
from src.agents.capability import CapabilityRegistry, Capability
from src.agents.task_management import TaskTracker, Task, TaskStatus, TaskPriority
from src.agents.protocol_agent import ProtocolAgent
from src.agents.blockchain_agent import BlockchainAgent
from src.agents.handlers import TaskAgentHandler, ProtocolAgentHandler
from src.agents.master_coordinator import MasterCoordinator  # Added this import

__all__ = [
    "BaseAgent",
    "CapabilityRegistry",
    "Capability", 
    "MasterCoordinator",
    "TaskTracker",
    "Task",
    "TaskStatus",
    "TaskPriority",
    "ProtocolAgent",
    "BlockchainAgent",
    "TaskAgentHandler",
    "ProtocolAgentHandler",
]
>>>>>>> theirs
