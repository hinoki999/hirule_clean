"""
Test configuration and fixtures
"""
import pytest
import sys
import os
from typing import Dict

# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

@pytest.fixture
def test_config() -> Dict:
    """Provide test configuration"""
    return {
        'memory_system': {
            'host': 'localhost',
            'port': 6379,
            'db': 0,
            'namespace': 'nlt_test'
        },
        'message_bus': {
            'host': 'localhost',
            'port': 6379,
            'db': 1
        }
    }
