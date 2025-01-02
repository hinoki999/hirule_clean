<<<<<<< ours
class Config:
    ###"""Configuration management class###"""
    def __init__(self):
        self.settings = {}

    def get(self, key, default=None):
        return self.settings.get(key, default)

    def set(self, key, value):
        self.settings[key] = value


||||||| base
=======
from typing import Dict, Any, Optional
import json
import os
import logging

class Config:
    """
    Configuration management for the Hirule system.
    Handles loading, saving, and providing default configurations.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        self.logger = logging.getLogger("Config")
        self._config: Dict[str, Any] = {}
        self._config_path = config_path or "config.json"
        self.logger.info(f"Initializing Config with path: {self._config_path}")
        self.load_config()
        
    def load_config(self):
        """Load configuration from the specified file or create defaults."""
        if os.path.exists(self._config_path):
            try:
                with open(self._config_path, 'r') as f:
                    self._config = json.load(f)
                self.logger.info(f"Configuration loaded from {self._config_path}")
            except json.JSONDecodeError as e:
                self.logger.error(f"Failed to parse config file: {str(e)}. Reverting to defaults.")
                self._config = self.default_config()
                self.save_config()
        else:
            self.logger.warning(f"Config file {self._config_path} not found. Using default configuration.")
            self._config = self.default_config()
            self.save_config()
    
    def save_config(self):
        """Save the current configuration to the file."""
        try:
            with open(self._config_path, 'w') as f:
                json.dump(self._config, f, indent=4)
            self.logger.info(f"Configuration saved to {self._config_path}")
        except IOError as e:
            self.logger.error(f"Failed to save config file: {str(e)}")

    def default_config(self) -> Dict[str, Any]:
        """Provide the default configuration values."""
        self.logger.info("Generating default configuration.")
        return {
            "agents": {
                "protocol": {
                    "mqtt": {"host": "localhost", "port": 1883},
                    "coap": {"host": "localhost", "port": 5683},
                    "http3": {"host": "localhost", "port": 443}
                },
                "blockchain": {
                    "rollup_batch_size": 100,
                    "validation_threshold": 0.75
                },
                "semantic": {
                    "model_name": "bert-base-uncased",
                    "compression_ratio": 0.5,
                    "priority_threshold": 0.7
                }
            },
            "network": {
                "max_connections": 1000,
                "timeout": 30,
                "retry_attempts": 3
            },
            "security": {
                "encryption_enabled": True,
                "auth_required": True,
                "token_expiry": 3600
            }
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Retrieve a configuration value using dot-separated keys.
        
        Args:
            key (str): Dot-separated key string (e.g., "network.timeout").
            default (Any): Default value if the key is not found.
        
        Returns:
            Any: The value corresponding to the key, or the default value.
        """
        self.logger.debug(f"Getting config value for key: {key}")
        keys = key.split('.')
        value = self._config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k, default)
            else:
                self.logger.warning(f"Invalid key path: {key}. Returning default value.")
                return default
        return value
    
    def set(self, key: str, value: Any):
        """
        Set a configuration value using dot-separated keys.
        
        Args:
            key (str): Dot-separated key string (e.g., "network.timeout").
            value (Any): The value to set.
        """
        self.logger.debug(f"Setting config value for key: {key} to {value}")
        keys = key.split('.')
        config = self._config
        for k in keys[:-1]:
            config = config.setdefault(k, {})
        config[keys[-1]] = value
        self.save_config()

    def validate_config(self) -> bool:
        """
        Validate the configuration for required keys and values.
        
        Returns:
            bool: True if valid, False otherwise.
        """
        self.logger.info("Validating configuration.")
        # Example validation logic
        try:
            assert isinstance(self.get("network.max_connections"), int), "max_connections must be an integer."
            assert isinstance(self.get("security.encryption_enabled"), bool), "encryption_enabled must be a boolean."
            assert self.get("network.timeout") > 0, "timeout must be greater than 0."
            self.logger.info("Configuration is valid.")
            return True
        except AssertionError as e:
            self.logger.error(f"Configuration validation failed: {str(e)}")
            return False
>>>>>>> theirs
