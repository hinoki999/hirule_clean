from dataclasses import dataclass, field
from typing import Dict, List, Optional
from enum import Enum
import logging
import time

class AgentStatus(Enum):
    AVAILABLE = "available"
    BUSY = "busy"
    OVERLOADED = "overloaded"
    OFFLINE = "offline"

@dataclass
class AgentMetrics:
    """Tracks the current load and performance metrics of an agent."""
    current_tasks: int = 0
    total_tasks_processed: int = 0
    avg_processing_time: float = 0.0
    last_task_completion: float = 0.0
    status: AgentStatus = AgentStatus.AVAILABLE
    capabilities: List[str] = field(default_factory=list)
    
class LoadBalancer:
    """Manages task distribution among agents based on their current load and capabilities."""
    
    def __init__(self, max_tasks_per_agent: int = 5):
        self.agent_metrics: Dict[str, AgentMetrics] = {}
        self.max_tasks_per_agent = max_tasks_per_agent
        self.logger = logging.getLogger(__name__)

    def register_agent(self, agent_id: str, capabilities: List[str]) -> None:
        """Register a new agent with the load balancer."""
        self.agent_metrics[agent_id] = AgentMetrics(capabilities=capabilities)
        self.logger.info(f"Registered agent {agent_id} with capabilities {capabilities}")

    def update_agent_status(self, agent_id: str, status: AgentStatus) -> None:
        """Update the status of an agent."""
        if agent_id in self.agent_metrics:
            self.agent_metrics[agent_id].status = status
            self.logger.info(f"Updated agent {agent_id} status to {status.value}")

    def task_started(self, agent_id: str) -> None:
        """Record that an agent has started a new task."""
        if agent_id in self.agent_metrics:
            metrics = self.agent_metrics[agent_id]
            metrics.current_tasks += 1
            
            # Update status based on load
            if metrics.current_tasks >= self.max_tasks_per_agent:
                metrics.status = AgentStatus.OVERLOADED
            elif metrics.current_tasks > 0:
                metrics.status = AgentStatus.BUSY
                
            self.logger.info(f"Agent {agent_id} started task. Current load: {metrics.current_tasks}")

    def task_completed(self, agent_id: str, processing_time: float) -> None:
        """Record that an agent has completed a task."""
        if agent_id in self.agent_metrics:
            metrics = self.agent_metrics[agent_id]
            metrics.current_tasks -= 1
            metrics.total_tasks_processed += 1
            metrics.last_task_completion = time.time()
            
            # Update average processing time
            if metrics.avg_processing_time == 0.0:
                metrics.avg_processing_time = processing_time
            else:
                metrics.avg_processing_time = (metrics.avg_processing_time + processing_time) / 2
                
            # Update status based on new load
            if metrics.current_tasks == 0:
                metrics.status = AgentStatus.AVAILABLE
            elif metrics.current_tasks < self.max_tasks_per_agent:
                metrics.status = AgentStatus.BUSY
                
            self.logger.info(f"Agent {agent_id} completed task. Current load: {metrics.current_tasks}")

    def find_best_agent(self, required_capabilities: List[str]) -> Optional[str]:
        """Find the most suitable agent for a task based on capabilities and current load."""
        suitable_agents = []
        
        # First, filter agents by required capabilities
        for agent_id, metrics in self.agent_metrics.items():
            if metrics.status != AgentStatus.OFFLINE:
                if all(cap in metrics.capabilities for cap in required_capabilities):
                    suitable_agents.append((agent_id, metrics))
        
        if not suitable_agents:
            self.logger.warning(f"No suitable agents found with capabilities {required_capabilities}")
            return None
            
        # Sort by current load and previous performance
        sorted_agents = sorted(suitable_agents, 
                             key=lambda x: (x[1].current_tasks, 
                                          x[1].avg_processing_time))
        
        chosen_agent = sorted_agents[0][0]
        self.logger.info(f"Selected agent {chosen_agent} for task with capabilities {required_capabilities}")
        return chosen_agent

    def get_system_load(self) -> Dict[str, float]:
        """Get the current load distribution across all agents."""
        return {
            agent_id: metrics.current_tasks 
            for agent_id, metrics in self.agent_metrics.items()
        }