import os
from typing import Dict
import json
import logging

class APIKeys:
    ###"""Manages API keys for different services###"""
    def __init__(self):
        self.keys: Dict[str, str] = {}
        self.logger = logging.getLogger(__name__)

    def load_from_env(self):
        ###"""Load API keys from environment variables###"""
        services = ['CLEARBIT', 'HUNTER']
        for service in services:
            key = os.environ.get(f'{service}_API_KEY')
            if key:
                self.keys[service.lower()] = key
            else:
                self.logger.warning(f"No API key found for {service}")

    def load_from_file(self, filepath: str):
        ###"""Load API keys from JSON file###"""
        try:
            with open(filepath, 'r') as f:
                self.keys.update(json.load(f))
        except Exception as e:
            self.logger.error(f"Failed to load API keys from file: {str(e)}")

    def get_key(self, service: str) -> str:
        ###"""Get API key for specific service###"""
        key = self.keys.get(service.lower())
        if not key:
            raise ValueError(f"No API key found for {service}")
        return key


