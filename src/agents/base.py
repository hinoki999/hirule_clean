from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Callable
import asyncio
import uuid
from datetime import datetime
from enum import Enum, auto
from src.core.messaging import MessageBus, Message
from src.core.config import Config
import logging

class AgentCapability(Enum):
    """Enumeration of agent capabilities"""
    COORDINATION = auto()
    SEMANTIC = auto()
    PROTOCOL = auto()
    BLOCKCHAIN = auto()
    BASE = auto()
    EDGE = auto()
    MONITORING = auto()
    TRADING = auto()           # New trading capability
    MARKET_DATA = auto()       # For market data handling
    ORDER_MANAGEMENT = auto()  # For order execution
    RISK_MANAGEMENT = auto()   # For risk calculations