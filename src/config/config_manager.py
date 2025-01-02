from typing import Dict, Any, Optional
import json
import os
from dataclasses import dataclass
from datetime import datetime

@dataclass
class SystemConfig:
    # Trading Configuration
    initial_capital: float
    max_position_size: float
    max_leverage: float
    trading_hours: Dict[str, Dict[str, str]]
    allowed_markets: list[str]
    
    # Risk Management
    risk_limits: Dict[str, float]
    max_drawdown: float
    var_limit: float
    position_limits: Dict[str, float]
    
    # Performance Tracking
    performance_metrics_lookback: int
    benchmark_index: str
    risk_free_rate: float
    
    # Logging Configuration
    log_dir: str
    log_level: str
    retention_days: int
    max_cache_size: int
    
    # Memory System
    memory_retention_period: int
    max_memories: int
    memory_importance_threshold: float

class ConfigManager:
    def __init__(self, config_path: str):
        self.config_path = config_path
        self.config: Dict[str, Any] = {}
        self.last_reload: Optional[datetime] = None
        self._load_config()
    
    def _load_config(self) -> None:
        """Load configuration from file"""
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
            
        with open(self.config_path, 'r') as f:
            self.config = json.load(f)
            
        self._validate_config()
        self.last_reload = datetime.now()
    
    def _validate_config(self) -> None:
        """Validate configuration values and types"""
        required_fields = {
            'initial_capital': float,
            'max_position_size': float,
            'max_leverage': float,
            'trading_hours': dict,
            'allowed_markets': list,
            'risk_limits': dict,
            'max_drawdown': float,
            'var_limit': float,
            'position_limits': dict,
            'performance_metrics_lookback': int,
            'benchmark_index': str,
            'risk_free_rate': float,
            'log_dir': str,
            'log_level': str,
            'retention_days': int,
            'max_cache_size': int,
            'memory_retention_period': int,
            'max_memories': int,
            'memory_importance_threshold': float
        }
        
        for field, field_type in required_fields.items():
            if field not in self.config:
                raise ValueError(f"Missing required configuration field: {field}")
            if not isinstance(self.config[field], field_type):
                raise TypeError(
                    f"Invalid type for {field}. Expected {field_type}, "
                    f"got {type(self.config[field])}"
                )
    
    def get_system_config(self) -> SystemConfig:
        """Get validated system configuration"""
        return SystemConfig(**self.config)
    
    def get_trading_config(self) -> Dict[str, Any]:
        """Get trading-specific configuration"""
        return {
            'initial_capital': self.config['initial_capital'],
            'max_position_size': self.config['max_position_size'],
            'max_leverage': self.config['max_leverage'],
            'trading_hours': self.config['trading_hours'],
            'allowed_markets': self.config['allowed_markets']
        }
    
    def get_risk_config(self) -> Dict[str, Any]:
        """Get risk management configuration"""
        return {
            'risk_limits': self.config['risk_limits'],
            'max_drawdown': self.config['max_drawdown'],
            'var_limit': self.config['var_limit'],
            'position_limits': self.config['position_limits']
        }
    
    def get_performance_config(self) -> Dict[str, Any]:
        """Get performance tracking configuration"""
        return {
            'lookback_days': self.config['performance_metrics_lookback'],
            'benchmark_index': self.config['benchmark_index'],
            'risk_free_rate': self.config['risk_free_rate']
        }
    
    def get_logging_config(self) -> Dict[str, Any]:
        """Get logging configuration"""
        return {
            'log_dir': self.config['log_dir'],
            'log_level': self.config['log_level'],
            'retention_days': self.config['retention_days'],
            'max_cache_size': self.config['max_cache_size']
        }
    
    def get_memory_config(self) -> Dict[str, Any]:
        """Get memory system configuration"""
        return {
            'retention_period': self.config['memory_retention_period'],
            'max_memories': self.config['max_memories'],
            'importance_threshold': self.config['memory_importance_threshold']
        }
    
    def reload(self) -> None:
        """Reload configuration from file"""
        self._load_config()
    
    def update(self, updates: Dict[str, Any]) -> None:
        """Update configuration values"""
        self.config.update(updates)
        self._validate_config()
        
        # Save updates to file
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=4)
