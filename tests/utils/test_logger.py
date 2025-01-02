# tests/utils/test_logger.py
import logging
import sys
from pathlib import Path
from datetime import datetime

class TestLogger:
    #"""Enhanced logging for test execution#"""

    def __init__(self, test_name: str):
        self.test_name = test_name
        self.log_dir = Path("tests/logs")
        self.log_dir.mkdir(exist_ok=True)

        # Create timestamped log file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = self.log_dir / f"{test_name}_{timestamp}.log"

        # Setup logger
        self.logger = logging.getLogger(test_name)
        self.logger.setLevel(logging.DEBUG)

        # File handler
        file_handler = logging.FileHandler(self.log_file)
        file_handler.setLevel(logging.DEBUG)

        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)

        # Formatting
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

    def log_test_start(self, test_method: str):
        #"""Log test method start#"""
        self.logger.info(f"Starting test: {test_method}")

    def log_test_end(self, test_method: str, success: bool):
        #"""Log test method completion#"""
        status = "PASSED" if success else "FAILED"
        self.logger.info(f"Test {test_method} {status}")


