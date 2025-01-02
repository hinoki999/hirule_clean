from typing import Dict, List, Any, Optional
from datetime import datetime

class AgentLearningEnvironment:
    def __init__(self):
        self.performance_history: Dict[str, List[float]] = {}
        self.learning_metrics: Dict[str, Dict] = {}
        self.interaction_history: List[Dict] = []
        
    async def record_interaction(self, interaction: Dict):
        """Record agent interactions for learning"""
        self.interaction_history.append(interaction)
        agent_id = interaction.get("agent_id")
        if agent_id not in self.performance_history:
            self.performance_history[agent_id] = []
            
    async def update_learning_metrics(self, agent_id: str, metrics: Dict):
        """Update learning metrics for an agent"""
        if agent_id not in self.learning_metrics:
            self.learning_metrics[agent_id] = {}
        self.learning_metrics[agent_id].update(metrics)
        
    def get_agent_performance(self, agent_id: str) -> List[float]:
        """Get historical performance for an agent"""
        return self.performance_history.get(agent_id, [])
        
    def get_learning_metrics(self, agent_id: str) -> Dict:
        """Get current learning metrics for an agent"""
        return self.learning_metrics.get(agent_id, {})
