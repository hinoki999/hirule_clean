import pytest
import os
import tempfile
import json
from src.config.api_keys import APIKeys

def test_load_from_env():
    #"""Test loading API keys from environment variables#"""
    # Setup test environment variables
    os.environ['CLEARBIT_API_KEY'] = 'test_clearbit_key'
    os.environ['HUNTER_API_KEY'] = 'test_hunter_key'

    api_keys = APIKeys()
    api_keys.load_from_env()

    assert api_keys.get_key('clearbit') == 'test_clearbit_key'
    assert api_keys.get_key('hunter') == 'test_hunter_key'

def test_load_from_file():
    #"""Test loading API keys from file#"""
    test_keys = {
        'clearbit': 'file_clearbit_key',
        'hunter': 'file_hunter_key'
    }

    # Create temporary config file
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        json.dump(test_keys, f)

    api_keys = APIKeys()
    api_keys.load_from_file(f.name)

    assert api_keys.get_key('clearbit') == 'file_clearbit_key'
    assert api_keys.get_key('hunter') == 'file_hunter_key'

    # Cleanup
    os.unlink(f.name)

def test_missing_key():
    #"""Test behavior when API key is missing#"""
    api_keys = APIKeys()

    with pytest.raises(ValueError, match="No API key found for missing_service"):
        api_keys.get_key('missing_service')

def test_case_insensitive():
    #"""Test case-insensitive key retrieval#"""
    os.environ['CLEARBIT_API_KEY'] = 'test_key'

    api_keys = APIKeys()
    api_keys.load_from_env()

    assert api_keys.get_key('CLEARBIT') == 'test_key'
    assert api_keys.get_key('clearbit') == 'test_key'


