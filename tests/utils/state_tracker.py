# tests/utils/state_tracker.py
from typing import Dict, List
import time
from dataclasses import dataclass
from collections import defaultdict

@dataclass
class StateEvent:
    timestamp: float
    event_type: str
    details: Dict
    
class TestStateTracker:
    """Tracks test execution state and timing"""
    
    def __init__(self):
        self.events: List[StateEvent] = []
        self.state_changes = defaultdict(list)
        self.start_time = time.time()
    
    def record_event(self, event_type: str, details: Dict):
        """Record a test event"""
        event = StateEvent(
            timestamp=time.time() - self.start_time,
            event_type=event_type,
            details=details
        )
        self.events.append(event)
    
    def record_state_change(self, component: str, old_state: str, new_state: str):
        """Record component state changes"""
        self.state_changes[component].append({
            'timestamp': time.time() - self.start_time,
            'old_state': old_state,
            'new_state': new_state
        })
    
    def get_timeline(self) -> List[Dict]:
        """Get chronological timeline of events"""
        timeline = []
        for event in self.events:
            timeline.append({
                'time': f"{event.timestamp:.3f}s",
                'type': event.event_type,
                'details': event.details
            })
        return timeline

    def get_component_history(self, component: str) -> List[Dict]:
        """Get state history for a component"""
        return self.state_changes[component]