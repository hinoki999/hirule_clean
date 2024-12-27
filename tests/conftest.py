# tests/conftest.py
import pytest
import asyncio
import logging

# Configure logging for tests
def pytest_configure(config):
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Set asyncio default loop scope
    config.option.asyncio_default_fixture_loop_scope = "function"

@pytest.fixture(scope="session", autouse=True)
def setup_test_env():
    """Setup test environment"""
    # Add any global test setup here
    yield
    # Add any global cleanup here