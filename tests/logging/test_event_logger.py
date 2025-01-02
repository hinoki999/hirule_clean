import unittest
from datetime import datetime, timedelta
import os
import shutil
from src.logging.event_logger import EventLogger, Event, EventCategory, EventSeverity

class TestEventLogger(unittest.TestCase):
    def setUp(self):
        self.test_log_dir = 'test_logs'
        self.config = {
            'log_dir': self.test_log_dir,
            'retention_days': 1,
            'min_severity': 'INFO',
            'max_cache_size': 100
        }
        self.logger = EventLogger(self.config)
        
    def tearDown(self):
        if os.path.exists(self.test_log_dir):
            shutil.rmtree(self.test_log_dir)
            
    def test_log_event(self):
        event = Event(
            timestamp=datetime.now(),
            category=EventCategory.TRADE,
            severity=EventSeverity.INFO,
            component='test_component',
            message='Test event',
            details={'test_key': 'test_value'},
            correlation_id='test_123'
        )
        
        self.logger.log_event(event)
        
        # Check event was added to cache
        self.assertEqual(len(self.logger.event_cache), 1)
        cached_event = self.logger.event_cache[0]
        self.assertEqual(cached_event.message, 'Test event')
        self.assertEqual(cached_event.category, EventCategory.TRADE)
        
    def test_get_events_filtering(self):
        # Add events with different categories and severities
        events = [
            Event(
                timestamp=datetime.now(),
                category=EventCategory.TRADE,
                severity=EventSeverity.INFO,
                component='component_1',
                message='Trade event',
                details={}
            ),
            Event(
                timestamp=datetime.now(),
                category=EventCategory.RISK,
                severity=EventSeverity.WARNING,
                component='component_2',
                message='Risk event',
                details={}
            ),
            Event(
                timestamp=datetime.now(),
                category=EventCategory.SYSTEM,
                severity=EventSeverity.ERROR,
                component='component_1',
                message='System event',
                details={}
            )
        ]
        
        for event in events:
            self.logger.log_event(event)
            
        # Test category filtering
        trade_events = self.logger.get_events(category=EventCategory.TRADE)
        self.assertEqual(len(trade_events), 1)
        self.assertEqual(trade_events[0].message, 'Trade event')
        
        # Test severity filtering
        warning_plus_events = self.logger.get_events(severity=EventSeverity.WARNING)
        self.assertEqual(len(warning_plus_events), 2)
        
        # Test component filtering
        component_1_events = self.logger.get_events(component='component_1')
        self.assertEqual(len(component_1_events), 2)
        
    def test_get_recent_events(self):
        # Add events with different timestamps
        old_event = Event(
            timestamp=datetime.now() - timedelta(minutes=10),
            category=EventCategory.TRADE,
            severity=EventSeverity.INFO,
            component='test',
            message='Old event',
            details={}
        )
        
        recent_event = Event(
            timestamp=datetime.now() - timedelta(minutes=2),
            category=EventCategory.TRADE,
            severity=EventSeverity.INFO,
            component='test',
            message='Recent event',
            details={}
        )
        
        self.logger.log_event(old_event)
        self.logger.log_event(recent_event)
        
        # Get events from last 5 minutes
        recent_events = self.logger.get_recent_events(minutes=5)
        self.assertEqual(len(recent_events), 1)
        self.assertEqual(recent_events[0].message, 'Recent event')
        
    def test_cache_size_limit(self):
        # Add more events than max cache size
        for i in range(self.config['max_cache_size'] + 10):
            event = Event(
                timestamp=datetime.now(),
                category=EventCategory.SYSTEM,
                severity=EventSeverity.INFO,
                component='test',
                message=f'Event {i}',
                details={}
            )
            self.logger.log_event(event)
            
        # Check cache size is limited
        self.assertEqual(
            len(self.logger.event_cache),
            self.config['max_cache_size']
        )
        
    def test_clear_cache(self):
        event = Event(
            timestamp=datetime.now(),
            category=EventCategory.SYSTEM,
            severity=EventSeverity.INFO,
            component='test',
            message='Test event',
            details={}
        )
        
        self.logger.log_event(event)
        self.assertEqual(len(self.logger.event_cache), 1)
        
        self.logger.clear_cache()
        self.assertEqual(len(self.logger.event_cache), 0)