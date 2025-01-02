<<<<<<< ours
from enum import Enum, auto
from dataclasses import dataclass, field
from datetime import datetime, UTC
import uuid
from typing import Any, Optional, Dict, List

class MessageStatus(Enum):
    CREATED = auto()
    QUEUED = auto()
    PROCESSING = auto()
    DELIVERED = auto()
    ACKNOWLEDGED = auto()
    FAILED = auto()
    RETRYING = auto()

class MessagePriority(Enum):
    LOW = 0
    NORMAL = 1
    HIGH = 2
    CRITICAL = 3

@dataclass
class Message:
    # Required fields
    sender_id: str
    recipient_id: Optional[str]
    message_type: str
    content: Dict[str, Any]

    # Optional fields with defaults
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    priority: MessagePriority = field(default=MessagePriority.NORMAL)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    status: MessageStatus = field(default=MessageStatus.CREATED)
    attempts: int = field(default=0)
    max_retries: int = field(default=3)
    last_error: Optional[str] = field(default=None)
    acknowledgment_required: bool = field(default=True)
    timeout_seconds: float = field(default=30.0)
    status_history: List[Dict] = field(default_factory=list)

    def __post_init__(self):
        if not self.status_history:
            self.status_history = [{
                'status': self.status,
                'timestamp': self.created_at,
                'details': 'Message created'
            }]

    def update_status(self, new_status: MessageStatus, details: str = None):
        self.status = new_status
        self.status_history.append({
            'status': new_status,
            'timestamp': datetime.now(UTC),
            'details': details
        })


||||||| base
=======
from enum import Enum, auto
from dataclasses import dataclass, field
from datetime import datetime, UTC
import uuid
from typing import Any, Optional, Dict, List

class MessageStatus(Enum):
    CREATED = auto()
    QUEUED = auto()
    PROCESSING = auto()
    DELIVERED = auto()
    ACKNOWLEDGED = auto()
    FAILED = auto()
    RETRYING = auto()

class MessagePriority(Enum):
    LOW = 0
    NORMAL = 1
    HIGH = 2
    CRITICAL = 3

@dataclass
class Message:
    # Required fields
    sender_id: str
    recipient_id: Optional[str]
    message_type: str
    content: Dict[str, Any]
    
    # Optional fields with defaults
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    priority: MessagePriority = field(default=MessagePriority.NORMAL)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    status: MessageStatus = field(default=MessageStatus.CREATED)
    attempts: int = field(default=0)
    max_retries: int = field(default=3)
    last_error: Optional[str] = field(default=None)
    acknowledgment_required: bool = field(default=True)
    timeout_seconds: float = field(default=30.0)
    status_history: List[Dict] = field(default_factory=list)

    def __post_init__(self):
        if not self.status_history:
            self.status_history = [{
                'status': self.status,
                'timestamp': self.created_at,
                'details': 'Message created'
            }]

    def update_status(self, new_status: MessageStatus, details: str = None):
        self.status = new_status
        self.status_history.append({
            'status': new_status,
            'timestamp': datetime.now(UTC),
            'details': details
        })
>>>>>>> theirs
