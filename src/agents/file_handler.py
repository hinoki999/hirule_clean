import json
import yaml
import os
import logging
from pathlib import Path
from typing import Any, Dict, List, Union

class FileHandler:
    def __init__(self, working_directory: str = None):
        self.working_directory = working_directory or os.getcwd()
        self.logger = logging.getLogger(__name__)

    def read_file(self, filepath: str, encoding: str = 'utf-8') -> str:
        ###"""Read any text file###"""
        try:
            full_path = Path(self.working_directory) / filepath
            with open(full_path, 'r', encoding=encoding) as file:
                return file.read()
        except Exception as e:
            self.logger.error(f"Error reading file {filepath}: {e}")
            raise

    def write_file(self, filepath: str, content: str, encoding: str = 'utf-8') -> None:
        ###"""Write content to any text file###"""
        try:
            full_path = Path(self.working_directory) / filepath
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, 'w', encoding=encoding) as file:
                file.write(content)
        except Exception as e:
            self.logger.error(f"Error writing file {filepath}: {e}")
            raise

    def read_json(self, filepath: str) -> Dict[str, Any]:
        ###"""Read and parse JSON file###"""
        try:
            content = self.read_file(filepath)
            return json.loads(content)
        except json.JSONDecodeError as e:
            self.logger.error(f"Error parsing JSON from {filepath}: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Error reading JSON file {filepath}: {e}")
            raise

    def write_json(self, filepath: str, data: Dict[str, Any], indent: int = 4) -> None:
        ###"""Write data to JSON file###"""
        try:
            content = json.dumps(data, indent=indent)
            self.write_file(filepath, content)
        except Exception as e:
            self.logger.error(f"Error writing JSON file {filepath}: {e}")
            raise

    def read_yaml(self, filepath: str) -> Dict[str, Any]:
        ###"""Read and parse YAML file###"""
        try:
            content = self.read_file(filepath)
            return yaml.safe_load(content)
        except yaml.YAMLError as e:
            self.logger.error(f"Error parsing YAML from {filepath}: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Error reading YAML file {filepath}: {e}")
            raise

    def write_yaml(self, filepath: str, data: Dict[str, Any]) -> None:
        ###"""Write data to YAML file###"""
        try:
            content = yaml.dump(data, default_flow_style=False)
            self.write_file(filepath, content)
        except Exception as e:
            self.logger.error(f"Error writing YAML file {filepath}: {e}")
            raise

    def read_python_file(self, filepath: str) -> str:
        ###"""Read Python file and return its content###"""
        return self.read_file(filepath)

    def write_python_file(self, filepath: str, content: str) -> None:
        ###"""Write Python file content###"""
        self.write_file(filepath, content)

    def ensure_directory(self, directory: str) -> None:
        ###"""Ensure a directory exists, create if it doesn't###"""
        try:
            full_path = Path(self.working_directory) / directory
            os.makedirs(full_path, exist_ok=True)
        except Exception as e:
            self.logger.error(f"Error creating directory {directory}: {e}")
            raise

    def list_files(self, directory: str = ".", pattern: str = "*") -> List[str]:
        ###"""List all files in directory matching pattern###"""
        try:
            full_path = Path(self.working_directory) / directory
            return [str(p.relative_to(self.working_directory))
                   for p in full_path.glob(pattern) if p.is_file()]
        except Exception as e:
            self.logger.error(f"Error listing files in {directory}: {e}")
            raise

    def file_exists(self, filepath: str) -> bool:
        ###"""Check if file exists###"""
        full_path = Path(self.working_directory) / filepath
        return full_path.exists() and full_path.is_file()

    def delete_file(self, filepath: str) -> None:
        ###"""Delete a file###"""
        try:
            full_path = Path(self.working_directory) / filepath
            if full_path.exists():
                os.remove(full_path)
        except Exception as e:
            self.logger.error(f"Error deleting file {filepath}: {e}")
            raise


