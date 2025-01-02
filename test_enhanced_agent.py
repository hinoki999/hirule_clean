import unittest
import json
import os
import sys
from pathlib import Path

# Add the src directory to the Python path
sys.path.append(str(Path(__file__).parent / 'src'))

from src.agents.compressor_agent import CompressorAgent
from src.agents.base_agent import AgentCapability

class TestEnhancedAgent(unittest.TestCase):
    def setUp(self):
        self.test_dir = "test_files"
        os.makedirs(self.test_dir, exist_ok=True)
        os.chdir(self.test_dir)

        # Create test agent
        self.agent = CompressorAgent("test_agent")

        # Create test data
        self.test_data = {
            "name": "test",
            "values": [1, 2, 3, 4, 5],
            "nested": {
                "key": "value"
            }
        }

        # Save test data to file
        with open("test_input.json", "w") as f:
            json.dump(self.test_data, f)

    def tearDown(self):
        os.chdir("..")
        for root, dirs, files in os.walk(self.test_dir, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
        os.rmdir(self.test_dir)

    def test_file_handling_capability(self):
        #"""Test that agent has file handling capability#"""
        self.assertTrue(self.agent.has_capability(AgentCapability.FILE_HANDLING))
        self.assertTrue(self.agent.has_capability(AgentCapability.DATA_COMPRESSION))

    def test_process_task_with_file(self):
        #"""Test processing task with file input#"""
        task = {
            "id": "test_task",
            "type": "compress",
            "data": "test_input.json"
        }

        # Process task
        result = self.agent.process_task(task)

        # Verify results
        self.assertEqual(result["status"], "success")
        self.assertTrue(self.agent.file_handler.file_exists(result["output_file"]))

        # Load and verify compressed results
        compressed_data = self.agent.file_handler.read_json(result["output_file"])
        self.assertTrue("compressed_data" in compressed_data)

    def test_process_task_with_direct_data(self):
        #"""Test processing task with direct data input#"""
        task = {
            "id": "test_task_direct",
            "type": "compress",
            "data": self.test_data
        }

        # Process task
        result = self.agent.process_task(task)

        # Verify results
        self.assertEqual(result["status"], "success")
        self.assertTrue(result["compression_ratio"] > 0)

        # Verify output file exists and contains compressed data
        self.assertTrue(self.agent.file_handler.file_exists(result["output_file"]))

if __name__ == '__main__':
    unittest.main()


