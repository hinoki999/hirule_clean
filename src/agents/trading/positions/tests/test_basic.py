import pytest

def test_basic():
    """Basic test to verify pytest is working."""
    assert True

@pytest.mark.asyncio
async def test_async_basic():
    """Basic async test to verify pytest-asyncio is working."""
    assert True
