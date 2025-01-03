"""
Error handling and recovery system for NLT Trading
"""
from typing import Dict, Optional, Callable
import logging
import asyncio
import traceback
import time
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class ErrorSeverity(Enum):
    INFO = 1
    WARNING = 2
    ERROR = 3
    CRITICAL = 4

@dataclass
class ErrorContext:
    timestamp: float
    component: str
    severity: ErrorSeverity
    error_type: str
    message: str
    stacktrace: str
    recovery_attempted: bool = False
    resolved: bool = False

class ErrorHandler:
    def __init__(self, config: Dict):
        self.config = config
        self.error_callbacks: Dict[str, Callable] = {}
        self.error_history: Dict[str, list[ErrorContext]] = {}
        self.recovery_strategies: Dict[str, Callable] = {}
        
    def register_error_callback(self, error_type: str, callback: Callable):
        """Register callback for specific error type"""
        self.error_callbacks[error_type] = callback
        
    def register_recovery_strategy(self, error_type: str, strategy: Callable):
        """Register recovery strategy for specific error type"""
        self.recovery_strategies[error_type] = strategy
        
    async def handle_error(self, component: str, error: Exception, severity: ErrorSeverity) -> Optional[ErrorContext]:
        """Handle an error and attempt recovery if possible"""
        try:
            error_type = error.__class__.__name__
            context = ErrorContext(
                timestamp=time.time(),
                component=component,
                severity=severity,
                error_type=error_type,
                message=str(error),
                stacktrace=traceback.format_exc()
            )
            
            # Log error
            logger.error(f"Error in {component}: {error_type} - {str(error)}")
            
            # Store in history
            if component not in self.error_history:
                self.error_history[component] = []
            self.error_history[component].append(context)
            
            # Notify callbacks
            if error_type in self.error_callbacks:
                await self.error_callbacks[error_type](context)
            
            # Attempt recovery if strategy exists
            if error_type in self.recovery_strategies:
                try:
                    await self.recovery_strategies[error_type](context)
                    context.recovery_attempted = True
                    context.resolved = True
                except Exception as recovery_error:
                    logger.error(f"Recovery failed: {str(recovery_error)}")
                    context.recovery_attempted = True
                    context.resolved = False
            
            return context
            
        except Exception as e:
            logger.error(f"Error in error handler: {str(e)}")
            return None
