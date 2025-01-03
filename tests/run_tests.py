"""
Test runner for NLT Trading System
"""
import pytest
import sys
import os

if __name__ == "__main__":
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    pytest.main(["tests/training/test_market_data.py", "-v"])
