from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

class GoalStatus(Enum):
    PENDING = 'pending'
    IN_PROGRESS = 'in_progress'
    COMPLETED = 'completed'
    FAILED = 'failed'

@dataclass
class Goal:
    id: str
    type: str
    parameters: Dict[str, Any]
    status: GoalStatus
    priority: int
    dependencies: List[str]  # List of goal IDs this goal depends on
    created_at: datetime
    completed_at: Optional[datetime] = None
    progress: float = 0.0  # 0.0 to 1.0
    result: Optional[Dict[str, Any]] = None

class GoalManager:
    def __init__(self):
        self.goals: Dict[str, Goal] = {}
        self.active_goals: List[str] = []

    async def add_goal(self, goal: Goal) -> None:
        """Add a new goal to the manager"""
        self.goals[goal.id] = goal
        if not goal.dependencies or all(self.is_goal_completed(dep) for dep in goal.dependencies):
            self.active_goals.append(goal.id)

    async def update_goal_progress(self, goal_id: str, progress: float, 
                                 result: Optional[Dict[str, Any]] = None) -> None:
        """Update the progress of a goal"""
        if goal_id not in self.goals:
            return

        goal = self.goals[goal_id]
        goal.progress = progress

        if progress >= 1.0:
            goal.status = GoalStatus.COMPLETED
            goal.completed_at = datetime.now()
            goal.result = result
            self.active_goals.remove(goal_id)
            
            # Activate dependent goals
            self._activate_dependent_goals(goal_id)

    def get_active_goals(self) -> List[Goal]:
        """Get list of currently active goals"""
        return [self.goals[goal_id] for goal_id in self.active_goals]

    def is_goal_completed(self, goal_id: str) -> bool:
        """Check if a goal is completed"""
        return goal_id in self.goals and self.goals[goal_id].status == GoalStatus.COMPLETED

    def _activate_dependent_goals(self, completed_goal_id: str) -> None:
        """Activate goals that were waiting on the completed goal"""
        for goal_id, goal in self.goals.items():
            if (goal.status == GoalStatus.PENDING and 
                completed_goal_id in goal.dependencies and
                all(self.is_goal_completed(dep) for dep in goal.dependencies)):
                goal.status = GoalStatus.IN_PROGRESS
                self.active_goals.append(goal_id)