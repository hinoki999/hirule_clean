import unittest
import json
import yaml
import os
from pathlib import Path
from src.agents.file_handler import FileHandler

class TestFileHandler(unittest.TestCase):
    def setUp(self):
        # Create a test directory
        self.test_dir = "test_files"
        self.file_handler = FileHandler(self.test_dir)
        os.makedirs(self.test_dir, exist_ok=True)

    def tearDown(self):
        # Clean up test files
        for root, dirs, files in os.walk(self.test_dir, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        os.rmdir(self.test_dir)

    def test_text_file_operations(self):
        # Test basic text file operations
        test_content = "Hello, World!"
        self.file_handler.write_file("test.txt", test_content)

        # Verify file exists
        self.assertTrue(self.file_handler.file_exists("test.txt"))

        # Read and verify content
        read_content = self.file_handler.read_file("test.txt")
        self.assertEqual(test_content, read_content)

    def test_json_operations(self):
        # Test JSON operations
        test_data = {
            "name": "Test Agent",
            "capabilities": ["file_handling", "data_processing"],
            "active": True
        }

        # Write JSON
        self.file_handler.write_json("config.json", test_data)

        # Read and verify JSON
        read_data = self.file_handler.read_json("config.json")
        self.assertEqual(test_data, read_data)

    def test_yaml_operations(self):
        # Test YAML operations
        test_data = {
            "agent": {
                "name": "Test Agent",
                "settings": {
                    "max_tasks": 5,
                    "timeout": 30
                }
            }
        }

        # Write YAML
        self.file_handler.write_yaml("config.yaml", test_data)

        # Read and verify YAML
        read_data = self.file_handler.read_yaml("config.yaml")
        self.assertEqual(test_data, read_data)

    def test_python_file_operations(self):
        # Test Python file operations
        python_content = #"""
def greet(name):
    return f"Hello, {name}!"
        #"""

        # Write Python file
        self.file_handler.write_python_file("greet.py", python_content)

        # Read and verify Python file
        read_content = self.file_handler.read_python_file("greet.py")
        self.assertEqual(python_content, read_content)

    def test_directory_operations(self):
        # Test directory operations
        test_dir = "nested/test/dir"
        self.file_handler.ensure_directory(test_dir)

        # Write a file in nested directory
        self.file_handler.write_file(f"{test_dir}/test.txt", "Test content")

        # List files
        files = self.file_handler.list_files(test_dir)
        self.assertEqual(len(files), 1)
        self.assertTrue("test.txt" in files[0])

    def test_file_deletion(self):
        # Test file deletion
        self.file_handler.write_file("to_delete.txt", "Delete me")
        self.assertTrue(self.file_handler.file_exists("to_delete.txt"))

        # Delete file
        self.file_handler.delete_file("to_delete.txt")
        self.assertFalse(self.file_handler.file_exists("to_delete.txt"))

if __name__ == '__main__':
    unittest.main()


