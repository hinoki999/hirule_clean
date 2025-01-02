class Config:
    """Configuration class for the system"""
    def __init__(self, config_dict: dict = None):
        self._config = config_dict or {}
        
    def get(self, key: str, default=None):
        """Get a configuration value"""
        return self._config.get(key, default)
        
    def __getitem__(self, key: str):
        """Get a configuration value using dictionary syntax"""
        return self._config[key]
