import json
from typing import Dict, List, Optional
from datetime import datetime
from .memory_types import Memory, MemoryType
import sqlite3
from pathlib import Path

class MemoryStore:
    """Persistent storage for agent memories"""
    
    def __init__(self, db_path: str = "memory.db"):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Initialize the SQLite database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create memories table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT NOT NULL,
                content TEXT NOT NULL,
                importance REAL,
                timestamp TEXT NOT NULL,
                last_accessed TEXT NOT NULL,
                access_count INTEGER DEFAULT 0
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def store(self, memory: Memory) -> int:
        """Store a memory and return its ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO memories (type, content, importance, timestamp, last_accessed, access_count)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            memory.memory_type.value,
            json.dumps(memory.content),
            memory.importance,
            memory.timestamp.isoformat(),
            memory.last_accessed.isoformat(),
            memory.access_count
        ))
        
        memory_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return memory_id
    
    def retrieve(self, memory_type: Optional[MemoryType] = None, 
                start_time: Optional[datetime] = None,
                end_time: Optional[datetime] = None,
                limit: int = 100) -> List[Memory]:
        """Retrieve memories based on filters"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = "SELECT * FROM memories"
        conditions = []
        params = []
        
        if memory_type:
            conditions.append("type = ?")
            params.append(memory_type.value)
            
        if start_time:
            conditions.append("timestamp >= ?")
            params.append(start_time.isoformat())
            
        if end_time:
            conditions.append("timestamp <= ?")
            params.append(end_time.isoformat())
            
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
            
        query += " ORDER BY importance DESC, timestamp DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        memories = []
        for row in rows:
            memory = Memory(
                memory_type=MemoryType(row[1]),
                content=json.loads(row[2]),
                importance=row[3],
                timestamp=datetime.fromisoformat(row[4])
            )
            memory.last_accessed = datetime.fromisoformat(row[5])
            memory.access_count = row[6]
            memory.access()  # Update access time and count
            
            # Update access metadata in DB
            cursor.execute('''
                UPDATE memories 
                SET last_accessed = ?, access_count = ?
                WHERE id = ?
            ''', (memory.last_accessed.isoformat(), memory.access_count, row[0]))
            
            memories.append(memory)
            
        conn.commit()
        conn.close()
        
        return memories
    
    def clear(self, memory_type: Optional[MemoryType] = None):
        """Clear memories of a specific type or all memories"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if memory_type:
            cursor.execute("DELETE FROM memories WHERE type = ?", (memory_type.value,))
        else:
            cursor.execute("DELETE FROM memories")
            
        conn.commit()
        conn.close()