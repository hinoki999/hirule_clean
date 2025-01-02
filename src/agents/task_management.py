<<<<<<< ours
from dataclasses import dataclass
from typing import Dict, Any, List, Optional
from enum import Enum
import time
import uuid
import asyncio

class TaskStatus(Enum):
    PENDING = "pending"
    ASSIGNED = "assigned"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    REASSIGNED = "reassigned"

class TaskPriority(Enum):
    LOW = 0
    MEDIUM = 1
    HIGH = 2
    CRITICAL = 3

@dataclass
class Task:
    ###"""Represents a task in the system.###"""
    task_id: str
    priority: TaskPriority
    required_capability: str
    status: TaskStatus
    assigned_agent: Optional[str]
    created_at: float
    started_at: Optional[float]
    completed_at: Optional[float]
    estimated_load: float
    actual_load: Optional[float]
    dependencies: List[str]  # List of task IDs this task depends on
    payload: Dict[str, Any]
    result: Optional[Dict[str, Any]] = None

class TaskTracker:
    ###"""Manages task lifecycle and dependencies.###"""

    def __init__(self):
        self.tasks: Dict[str, Task] = {}
        self.agent_tasks: Dict[str, List[str]] = {}  # agent_id -> task_ids
        self._lock = asyncio.Lock()

    def create_task(self,
                    required_capability: str,
                    payload: Dict[str, Any],
                    priority: TaskPriority = TaskPriority.MEDIUM,
                    estimated_load: float = 0.1,
                    dependencies: List[str] = None) -> Task:
        ###"""Create a new task.###"""
        task_id = str(uuid.uuid4())
        task = Task(
            task_id=task_id,
            priority=priority,
            required_capability=required_capability,
            status=TaskStatus.PENDING,
            assigned_agent=None,
            created_at=time.time(),
            started_at=None,
            completed_at=None,
            estimated_load=estimated_load,
            actual_load=None,
            dependencies=dependencies or [],
            payload=payload
        )
        self.tasks[task_id] = task
        return task

    async def assign_task(self, task_id: str, agent_id: str):
        ###"""Assign a task to an agent.###"""
        async with self._lock:
            if task_id not in self.tasks:
                raise ValueError(f"Task {task_id} not found")

            task = self.tasks[task_id]
            task.assigned_agent = agent_id
            task.status = TaskStatus.ASSIGNED

            if agent_id not in self.agent_tasks:
                self.agent_tasks[agent_id] = []
            self.agent_tasks[agent_id].append(task_id)

    async def update_task_status(self,
                               task_id: str,
                               status: TaskStatus,
                               result: Dict[str, Any] = None,
                               actual_load: float = None):
        ###"""Update task status and optionally store result.###"""
        async with self._lock:
            if task_id not in self.tasks:
                raise ValueError(f"Task {task_id} not found")

            task = self.tasks[task_id]
            task.status = status

            if status == TaskStatus.RUNNING and not task.started_at:
                task.started_at = time.time()
            elif status == TaskStatus.COMPLETED:
                task.completed_at = time.time()
                task.result = result
                task.actual_load = actual_load

    async def get_agent_load(self, agent_id: str) -> float:
        ###"""Calculate current load for an agent.###"""
        async with self._lock:
            if agent_id not in self.agent_tasks:
                return 0.0

            total_load = 0.0
            for task_id in self.agent_tasks[agent_id]:
                task = self.tasks[task_id]
                if task.status in [TaskStatus.ASSIGNED, TaskStatus.RUNNING]:
                    total_load += task.estimated_load
            return total_load

    async def get_pending_tasks(self, capability: str = None) -> List[Task]:
        ###"""Get all pending tasks, optionally filtered by capability.###"""
        async with self._lock:
            pending = []
            for task in self.tasks.values():
                if task.status == TaskStatus.PENDING:
                    if capability is None or task.required_capability == capability:
                        pending.append(task)
            return sorted(pending, key=lambda t: t.priority.value, reverse=True)

    async def reassign_tasks(self, from_agent: str, to_agent: str = None):
        ###"""Reassign tasks from one agent to another or back to pending.###"""
        async with self._lock:
            if from_agent not in self.agent_tasks:
                return

            tasks_to_reassign = self.agent_tasks[from_agent]
            for task_id in tasks_to_reassign:
                task = self.tasks[task_id]
                if task.status in [TaskStatus.ASSIGNED, TaskStatus.RUNNING]:
                    if to_agent:
                        task.assigned_agent = to_agent
                        task.status = TaskStatus.REASSIGNED
                        if to_agent not in self.agent_tasks:
                            self.agent_tasks[to_agent] = []
                        self.agent_tasks[to_agent].append(task_id)
                    else:
                        task.assigned_agent = None
                        task.status = TaskStatus.PENDING

            del self.agent_tasks[from_agent]


||||||| base
=======
from dataclasses import dataclass
from typing import Dict, Any, List, Optional
from enum import Enum
import time
import uuid
import asyncio

class TaskStatus(Enum):
    PENDING = "pending"
    ASSIGNED = "assigned"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    REASSIGNED = "reassigned"

class TaskPriority(Enum):
    LOW = 0
    MEDIUM = 1
    HIGH = 2
    CRITICAL = 3

@dataclass
class Task:
    """Represents a task in the system."""
    task_id: str
    priority: TaskPriority
    required_capability: str
    status: TaskStatus
    assigned_agent: Optional[str]
    created_at: float
    started_at: Optional[float]
    completed_at: Optional[float]
    estimated_load: float
    actual_load: Optional[float]
    dependencies: List[str]  # List of task IDs this task depends on
    payload: Dict[str, Any]
    result: Optional[Dict[str, Any]] = None

class TaskTracker:
    """Manages task lifecycle and dependencies."""
    
    def __init__(self):
        self.tasks: Dict[str, Task] = {}
        self.agent_tasks: Dict[str, List[str]] = {}  # agent_id -> task_ids
        self._lock = asyncio.Lock()
        
    def create_task(self, 
                    required_capability: str,
                    payload: Dict[str, Any],
                    priority: TaskPriority = TaskPriority.MEDIUM,
                    estimated_load: float = 0.1,
                    dependencies: List[str] = None) -> Task:
        """Create a new task."""
        task_id = str(uuid.uuid4())
        task = Task(
            task_id=task_id,
            priority=priority,
            required_capability=required_capability,
            status=TaskStatus.PENDING,
            assigned_agent=None,
            created_at=time.time(),
            started_at=None,
            completed_at=None,
            estimated_load=estimated_load,
            actual_load=None,
            dependencies=dependencies or [],
            payload=payload
        )
        self.tasks[task_id] = task
        return task

    async def assign_task(self, task_id: str, agent_id: str):
        """Assign a task to an agent."""
        async with self._lock:
            if task_id not in self.tasks:
                raise ValueError(f"Task {task_id} not found")
                
            task = self.tasks[task_id]
            task.assigned_agent = agent_id
            task.status = TaskStatus.ASSIGNED
            
            if agent_id not in self.agent_tasks:
                self.agent_tasks[agent_id] = []
            self.agent_tasks[agent_id].append(task_id)

    async def update_task_status(self, 
                               task_id: str, 
                               status: TaskStatus, 
                               result: Dict[str, Any] = None,
                               actual_load: float = None):
        """Update task status and optionally store result."""
        async with self._lock:
            if task_id not in self.tasks:
                raise ValueError(f"Task {task_id} not found")
                
            task = self.tasks[task_id]
            task.status = status
            
            if status == TaskStatus.RUNNING and not task.started_at:
                task.started_at = time.time()
            elif status == TaskStatus.COMPLETED:
                task.completed_at = time.time()
                task.result = result
                task.actual_load = actual_load

    async def get_agent_load(self, agent_id: str) -> float:
        """Calculate current load for an agent."""
        async with self._lock:
            if agent_id not in self.agent_tasks:
                return 0.0
                
            total_load = 0.0
            for task_id in self.agent_tasks[agent_id]:
                task = self.tasks[task_id]
                if task.status in [TaskStatus.ASSIGNED, TaskStatus.RUNNING]:
                    total_load += task.estimated_load
            return total_load

    async def get_pending_tasks(self, capability: str = None) -> List[Task]:
        """Get all pending tasks, optionally filtered by capability."""
        async with self._lock:
            pending = []
            for task in self.tasks.values():
                if task.status == TaskStatus.PENDING:
                    if capability is None or task.required_capability == capability:
                        pending.append(task)
            return sorted(pending, key=lambda t: t.priority.value, reverse=True)

    async def reassign_tasks(self, from_agent: str, to_agent: str = None):
        """Reassign tasks from one agent to another or back to pending."""
        async with self._lock:
            if from_agent not in self.agent_tasks:
                return
                
            tasks_to_reassign = self.agent_tasks[from_agent]
            for task_id in tasks_to_reassign:
                task = self.tasks[task_id]
                if task.status in [TaskStatus.ASSIGNED, TaskStatus.RUNNING]:
                    if to_agent:
                        task.assigned_agent = to_agent
                        task.status = TaskStatus.REASSIGNED
                        if to_agent not in self.agent_tasks:
                            self.agent_tasks[to_agent] = []
                        self.agent_tasks[to_agent].append(task_id)
                    else:
                        task.assigned_agent = None
                        task.status = TaskStatus.PENDING
                        
            del self.agent_tasks[from_agent]
>>>>>>> theirs
