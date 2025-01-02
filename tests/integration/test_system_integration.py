import unittest
import os
import shutil
import json
from datetime import datetime, timedelta
from src.main import TradingSystem
from src.logging.event_logger import EventCategory, EventSeverity

class TestSystemIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Create test configuration
        cls.test_config_dir = 'test_config'
        cls.test_log_dir = 'test_logs'
        os.makedirs(cls.test_config_dir, exist_ok=True)
        
        # Copy default config and modify for testing
        with open('config/default_config.json', 'r') as f:
            config = json.load(f)
            
        config.update({
            'log_dir': cls.test_log_dir,
            'initial_capital': 10000.0,  # Smaller amount for testing
            'max_position_size': 1000.0,
            'performance_metrics_lookback': 5  # Shorter lookback for testing
        })
        
        cls.config_path = os.path.join(cls.test_config_dir, 'test_config.json')
        with open(cls.config_path, 'w') as f:
            json.dump(config, f)
    
    @classmethod
    def tearDownClass(cls):
        # Cleanup test directories
        for dir_path in [cls.test_config_dir, cls.test_log_dir]:
            if os.path.exists(dir_path):
                shutil.rmtree(dir_path)
    
    def setUp(self):
        self.trading_system = TradingSystem(self.config_path)
    
    def tearDown(self):
        if self.trading_system.running:
            self.trading_system.stop()
            
    def test_system_initialization(self):
        """Test that all components are properly initialized"""
        self.assertIsNotNone(self.trading_system.config_manager)
        self.assertIsNotNone(self.trading_system.event_logger)
        self.assertIsNotNone(self.trading_system.performance_tracker)
        self.assertIsNotNone(self.trading_system.risk_monitor)
        self.assertIsNotNone(self.trading_system.memory_manager)
        
    def test_system_start_stop(self):
        """Test system startup and shutdown"""
        # Test startup
        self.trading_system.start()
        self.assertTrue(self.trading_system.running)
        
        # Verify startup events were logged
        recent_events = self.trading_system.event_logger.get_recent_events(minutes=1)
        startup_events = [e for e in recent_events 
                         if e.message == 'System starting']
        self.assertGreaterEqual(len(startup_events), 1)
        
        # Test shutdown
        self.trading_system.stop()
        self.assertFalse(self.trading_system.running)
        
        # Verify shutdown events were logged
        recent_events = self.trading_system.event_logger.get_recent_events(minutes=1)
        shutdown_events = [e for e in recent_events 
                          if e.message == 'System stopped']
        self.assertGreaterEqual(len(shutdown_events), 1)
        
    def test_config_reload(self):
        """Test configuration reloading"""
        # Start system
        self.trading_system.start()
        
        # Modify configuration
        with open(self.config_path, 'r') as f:
            config = json.load(f)
        
        config['max_position_size'] = 2000.0
        
        with open(self.config_path, 'w') as f:
            json.dump(config, f)
        
        # Reload configuration
        self.trading_system.reload_config()
        
        # Verify new configuration was loaded
        self.assertEqual(
            self.trading_system.system_config.max_position_size,
            2000.0
        )
        
        # Verify reload event was logged
        recent_events = self.trading_system.event_logger.get_recent_events(minutes=1)
        reload_events = [e for e in recent_events 
                        if e.message == 'Configuration reloaded']
        self.assertGreaterEqual(len(reload_events), 1)
        
    def test_component_interaction(self):
        """Test interaction between system components"""
        self.trading_system.start()
        
        # Add a trade and verify it's tracked by performance tracker
        trade = {
            'timestamp': datetime.now(),
            'symbol': 'AAPL',
            'size': 100,
            'price': 150.0,
            'direction': 'BUY',
            'pnl': 500.0
        }
        
        self.trading_system.performance_tracker.add_trade(trade)
        
        # Verify trade metrics are updated
        metrics = self.trading_system.performance_tracker.get_trade_metrics(
            lookback_days=1
        )
        self.assertGreater(metrics.avg_profit, 0)
        
        # Verify risk monitoring is working
        positions = {
            'AAPL': {
                'value': 15000.0,  # Exceeds position limit
                'leverage': 1.5
            }
        }
        
        alerts = self.trading_system.risk_monitor.check_position_risk(positions)
        self.assertGreaterEqual(len(alerts), 1)
        
        # Verify memory system integration
        memory_key = 'test_memory'
        memory_value = {'type': 'trade_pattern', 'data': 'breakout'}
        
        self.trading_system.memory_manager.store(
            memory_key,
            memory_value,
            importance=0.8
        )
        
        retrieved_memory = self.trading_system.memory_manager.retrieve(memory_key)
        self.assertEqual(retrieved_memory['data'], 'breakout')
        
    def test_error_handling(self):
        """Test system error handling"""
        # Test invalid configuration
        with self.assertRaises(ValueError):
            with open(self.config_path, 'w') as f:
                json.dump({}, f)  # Empty config
            TradingSystem(self.config_path)
        
        # Test startup failure handling
        def failing_init():
            raise Exception("Simulated initialization failure")
            
        self.trading_system._initialize_market_data = failing_init
        
        with self.assertRaises(Exception):
            self.trading_system.start()
        
        # Verify error was logged
        recent_events = self.trading_system.event_logger.get_recent_events(minutes=1)
        error_events = [e for e in recent_events 
                       if e.severity == EventSeverity.ERROR]
        self.assertGreaterEqual(len(error_events), 1)