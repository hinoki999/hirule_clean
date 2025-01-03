<<<<<<< ours
﻿class Capability:
    ANOMALY_DETECTION = "anomaly_detection"
||||||| base
=======
from enum import Enum, auto
from typing import Set, Dict, Any, Optional
from dataclasses import dataclass
import logging

class Capability(Enum):
    """Enumeration of possible agent capabilities."""
    MESSAGE_ROUTING = auto()
    PROTOCOL_TRANSLATION = auto()
    DATA_COMPRESSION = auto()
    SEMANTIC_ANALYSIS = auto()
    BLOCKCHAIN_VALIDATION = auto()
    MODEL_TRAINING = auto()
    SECURITY_ENFORCEMENT = auto()
    RESOURCE_MANAGEMENT = auto()
    NETWORK_OPTIMIZATION = auto()
    ANOMALY_DETECTION = auto()

@dataclass
class CapabilityMetadata:
    """Metadata about a capability."""
    description: str
    requirements: Dict[str, Any]
    performance_metrics: Dict[str, Any]

class CapabilityRegistry:
    """Registry for managing agent capabilities."""
    
    def __init__(self):
        self._capabilities: Dict[str, Set[Capability]] = {}
        self._metadata: Dict[Capability, CapabilityMetadata] = {}
        self.logger = logging.getLogger(self.__class__.__name__)

    def register_agent_capability(self, agent_id: str, capability: Capability):
        """Register a capability for an agent."""
        if not isinstance(capability, Capability):
            raise ValueError(f"Invalid capability: {capability}")
        
        if agent_id not in self._capabilities:
            self._capabilities[agent_id] = set()
        
        self._capabilities[agent_id].add(capability)
        self.logger.info(f"Registered capability {capability.name} for agent {agent_id}")

    def unregister_agent_capability(self, agent_id: str, capability: Capability):
        """Remove a capability from an agent."""
        if agent_id in self._capabilities:
            self._capabilities[agent_id].discard(capability)
            self.logger.info(f"Unregistered capability {capability.name} for agent {agent_id}")

    def get_agent_capabilities(self, agent_id: str) -> Set[Capability]:
        """Get all capabilities of an agent."""
        if agent_id not in self._capabilities:
            self.logger.warning(f"Agent {agent_id} not found in registry")
        return self._capabilities.get(agent_id, set())

    def find_agents_with_capability(self, capability: Capability) -> Set[str]:
        """Find all agents with a specific capability."""
        if not isinstance(capability, Capability):
            raise ValueError(f"Invalid capability: {capability}")
        
        agents = {
            agent_id for agent_id, caps in self._capabilities.items()
            if capability in caps
        }
        self.logger.info(f"Found {len(agents)} agents with capability {capability.name}")
        return agents

    def register_capability_metadata(self, 
                                     capability: Capability, 
                                     metadata: CapabilityMetadata):
        """Register metadata for a capability."""
        if not isinstance(capability, Capability):
            raise ValueError(f"Invalid capability: {capability}")
        
        self._metadata[capability] = metadata
        self.logger.info(f"Registered metadata for capability {capability.name}")

    def get_capability_metadata(self, capability: Capability) -> Optional[CapabilityMetadata]:
        """Get metadata for a capability."""
        if not isinstance(capability, Capability):
            raise ValueError(f"Invalid capability: {capability}")
        
        metadata = self._metadata.get(capability)
        if metadata is None:
            self.logger.warning(f"No metadata found for capability {capability.name}")
        return metadata
>>>>>>> theirs
