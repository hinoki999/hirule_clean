<<<<<<< ours
from src.agents.base import BaseAgent, AgentCapability
import zlib
import json
import base64
from typing import Dict, Any

class CompressorAgent(BaseAgent):
    def __init__(self, agent_id: str):
        super().__init__(agent_id, [AgentCapability.DATA_COMPRESSION])

    def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        task_type = task.get('type')
        input_data = task.get('data')

        if isinstance(input_data, str) and self.file_handler.file_exists(input_data):
            # If input is a file path, read the file
            input_data = self.load_task_data(input_data)

        if task_type == 'compress':
            result = self.compress_data(input_data)
            # Save compressed data to file
            output_file = self.save_results(
                task['id'],
                {'compressed_data': result},
                'json'
            )
            return {
                'status': 'success',
                'output_file': output_file,
                'compression_ratio': self.calculate_compression_ratio(input_data, result)
            }
        else:
            raise ValueError(f"Unsupported task type: {task_type}")

    def compress_data(self, data: Any) -> str:
        ###"""Compress data and return as base64 string###"""
        json_str = json.dumps(data)
        compressed = zlib.compress(json_str.encode('utf-8'))
        return base64.b64encode(compressed).decode('utf-8')

    def calculate_compression_ratio(self, original: Any, compressed: str) -> float:
        ###"""Calculate compression ratio###"""
        original_size = len(json.dumps(original).encode('utf-8'))
        compressed_size = len(base64.b64decode(compressed))
        return round(compressed_size / original_size * 100, 2)


||||||| base
=======
from src.agents.base import BaseAgent, AgentCapability
import zlib
import json
import base64
from typing import Dict, Any

class CompressorAgent(BaseAgent):
    def __init__(self, agent_id: str):
        super().__init__(agent_id, [AgentCapability.DATA_COMPRESSION])

    def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        task_type = task.get('type')
        input_data = task.get('data')
        
        if isinstance(input_data, str) and self.file_handler.file_exists(input_data):
            # If input is a file path, read the file
            input_data = self.load_task_data(input_data)
        
        if task_type == 'compress':
            result = self.compress_data(input_data)
            # Save compressed data to file
            output_file = self.save_results(
                task['id'], 
                {'compressed_data': result}, 
                'json'
            )
            return {
                'status': 'success',
                'output_file': output_file,
                'compression_ratio': self.calculate_compression_ratio(input_data, result)
            }
        else:
            raise ValueError(f"Unsupported task type: {task_type}")

    def compress_data(self, data: Any) -> str:
        """Compress data and return as base64 string"""
        json_str = json.dumps(data)
        compressed = zlib.compress(json_str.encode('utf-8'))
        return base64.b64encode(compressed).decode('utf-8')
    
    def calculate_compression_ratio(self, original: Any, compressed: str) -> float:
        """Calculate compression ratio"""
        original_size = len(json.dumps(original).encode('utf-8'))
        compressed_size = len(base64.b64decode(compressed))
        return round(compressed_size / original_size * 100, 2)
>>>>>>> theirs
