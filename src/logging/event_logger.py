import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import json
import os
from enum import Enum

class EventSeverity(Enum):
    DEBUG = 'DEBUG'
    INFO = 'INFO'
    WARNING = 'WARNING'
    ERROR = 'ERROR'
    CRITICAL = 'CRITICAL'

class EventCategory(Enum):
    SYSTEM = 'SYSTEM'
    TRADE = 'TRADE'
    RISK = 'RISK'
    PERFORMANCE = 'PERFORMANCE'
    MEMORY = 'MEMORY'
    GOAL = 'GOAL'

@dataclass
class Event:
    timestamp: datetime
    category: EventCategory
    severity: EventSeverity
    component: str
    message: str
    details: Dict[str, Any]
    correlation_id: Optional[str] = None

class EventLogger:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.log_dir = config.get('log_dir', 'logs')
        self.retention_days = config.get('retention_days', 30)
        self.min_severity = EventSeverity[config.get('min_severity', 'INFO')]
        
        # Create log directory if it doesn't exist
        os.makedirs(self.log_dir, exist_ok=True)
        
        # Initialize logging
        self._setup_logging()
        
        # Initialize in-memory event cache
        self.event_cache: List[Event] = []
        self.max_cache_size = config.get('max_cache_size', 1000)
        
    def _setup_logging(self):
        """Configure logging handlers and formatters"""
        self.logger = logging.getLogger('trading_system')
        self.logger.setLevel(logging.DEBUG)
        
        # Create handlers
        file_handler = logging.FileHandler(
            os.path.join(
                self.log_dir,
                f'trading_system_{datetime.now().strftime("%Y%m%d")}.log'
            )
        )
        console_handler = logging.StreamHandler()
        
        # Create formatters
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)s | %(name)s | %(message)s'
        )
        
        # Set formatters
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Add handlers
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
    def log_event(self, event: Event) -> None:
        """Log an event to both file and memory cache"""
        if event.severity.value >= self.min_severity.value:
            # Convert event to loggable format
            log_entry = self._format_event(event)
            
            # Log to file
            log_level = getattr(logging, event.severity.value)
            self.logger.log(log_level, log_entry)
            
            # Add to cache
            self.event_cache.append(event)
            
            # Trim cache if needed
            if len(self.event_cache) > self.max_cache_size:
                self.event_cache = self.event_cache[-self.max_cache_size:]
                
            # Archive old logs if needed
            self._archive_old_logs()
    
    def _format_event(self, event: Event) -> str:
        """Format event for logging"""
        return json.dumps({
            'timestamp': event.timestamp.isoformat(),
            'category': event.category.value,
            'severity': event.severity.value,
            'component': event.component,
            'message': event.message,
            'details': event.details,
            'correlation_id': event.correlation_id
        })
    
    def get_events(self,
                   category: Optional[EventCategory] = None,
                   severity: Optional[EventSeverity] = None,
                   component: Optional[str] = None,
                   start_time: Optional[datetime] = None,
                   end_time: Optional[datetime] = None) -> List[Event]:
        """Query events from cache with optional filters"""
        filtered_events = self.event_cache
        
        if category:
            filtered_events = [
                e for e in filtered_events if e.category == category
            ]
            
        if severity:
            filtered_events = [
                e for e in filtered_events if e.severity >= severity
            ]
            
        if component:
            filtered_events = [
                e for e in filtered_events if e.component == component
            ]
            
        if start_time:
            filtered_events = [
                e for e in filtered_events if e.timestamp >= start_time
            ]
            
        if end_time:
            filtered_events = [
                e for e in filtered_events if e.timestamp <= end_time
            ]
            
        return filtered_events
    
    def get_recent_events(self,
                         minutes: int = 5,
                         category: Optional[EventCategory] = None,
                         min_severity: Optional[EventSeverity] = None) -> List[Event]:
        """Get recent events within specified timeframe"""
        start_time = datetime.now() - timedelta(minutes=minutes)
        return self.get_events(
            category=category,
            severity=min_severity,
            start_time=start_time
        )
    
    def _archive_old_logs(self) -> None:
        """Archive logs older than retention period"""
        cutoff_date = datetime.now() - timedelta(days=self.retention_days)
        
        for filename in os.listdir(self.log_dir):
            if not filename.startswith('trading_system_'):
                continue
                
            file_path = os.path.join(self.log_dir, filename)
            file_date_str = filename.split('_')[-1].split('.')[0]
            
            try:
                file_date = datetime.strptime(file_date_str, '%Y%m%d')
                if file_date < cutoff_date:
                    archive_dir = os.path.join(self.log_dir, 'archive')
                    os.makedirs(archive_dir, exist_ok=True)
                    os.rename(
                        file_path,
                        os.path.join(archive_dir, filename)
                    )
            except ValueError:
                continue
    
    def clear_cache(self) -> None:
        """Clear the event cache"""
        self.event_cache = []
