"""
Memory management for the DaVinci Resolve AI Agent
"""

import json
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
from collections import deque
import sqlite3
from pathlib import Path

import logging
logger = logging.getLogger(__name__)


class MemoryManager:
    """Manages short-term and long-term memory for the agent"""
    
    def __init__(self, db_path: Optional[str] = None, max_short_term: int = 100):
        self.db_path = db_path or self._get_default_db_path()
        self.max_short_term = max_short_term
        self.short_term_memory = deque(maxlen=max_short_term)
        self._init_database()
        
    def add_interaction(self, content: Any, interaction_type: str, metadata: Optional[Dict[str, Any]] = None):
        """Add an interaction to memory"""
        interaction = {
            'timestamp': datetime.now().isoformat(),
            'type': interaction_type,
            'content': content,
            'metadata': metadata or {}
        }
        
        # Add to short-term memory
        self.short_term_memory.append(interaction)
        
        # Store in long-term memory
        self._store_long_term(interaction)
        
    def get_recent_actions(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent actions from memory"""
        recent = list(self.short_term_memory)[-limit:]
        return [item for item in recent if item['type'] in ['action', 'command', 'response']]
        
    def search_memory(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Search through long-term memory"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT * FROM interactions 
                WHERE content LIKE ? OR metadata LIKE ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (f'%{query}%', f'%{query}%', limit))
            
            results = []
            for row in cursor.fetchall():
                results.append({
                    'id': row['id'],
                    'timestamp': row['timestamp'],
                    'type': row['type'],
                    'content': json.loads(row['content']),
                    'metadata': json.loads(row['metadata'])
                })
                
            return results
            
        finally:
            conn.close()
            
    def get_context_window(self, window_size: int = 5) -> List[Dict[str, Any]]:
        """Get a context window of recent interactions"""
        return list(self.short_term_memory)[-window_size:]
        
    def store_feedback(self, task_id: str, feedback: str, success: bool):
        """Store user feedback about a task"""
        feedback_data = {
            'task_id': task_id,
            'feedback': feedback,
            'success': success,
            'timestamp': datetime.now().isoformat()
        }
        
        self.add_interaction(feedback_data, 'feedback')
        
    def get_successful_patterns(self) -> List[Dict[str, Any]]:
        """Retrieve patterns from successful interactions"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT * FROM interactions 
                WHERE type = 'feedback' 
                AND json_extract(content, '$.success') = 1
                ORDER BY timestamp DESC
                LIMIT 50
            """)
            
            patterns = []
            for row in cursor.fetchall():
                content = json.loads(row['content'])
                patterns.append({
                    'task_id': content.get('task_id'),
                    'feedback': content.get('feedback'),
                    'timestamp': row['timestamp']
                })
                
            return patterns
            
        finally:
            conn.close()
            
    def get_error_patterns(self) -> List[Dict[str, Any]]:
        """Retrieve patterns from failed interactions"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT * FROM interactions 
                WHERE type IN ('error', 'feedback')
                AND (type = 'error' OR json_extract(content, '$.success') = 0)
                ORDER BY timestamp DESC
                LIMIT 50
            """)
            
            patterns = []
            for row in cursor.fetchall():
                content = json.loads(row['content'])
                patterns.append({
                    'type': row['type'],
                    'content': content,
                    'timestamp': row['timestamp']
                })
                
            return patterns
            
        finally:
            conn.close()
            
    def clear_short_term_memory(self):
        """Clear short-term memory"""
        self.short_term_memory.clear()
        
    def export_memory(self, export_path: str):
        """Export memory to file"""
        memory_data = {
            'short_term': list(self.short_term_memory),
            'export_date': datetime.now().isoformat()
        }
        
        with open(export_path, 'w') as f:
            json.dump(memory_data, f, indent=2)
            
        logger.info(f"Memory exported to {export_path}")
        
    def _get_default_db_path(self) -> str:
        """Get default database path"""
        return os.path.join(os.path.dirname(__file__), '..', '..', '..', 'data', 'agent_memory.db')
        
    def _init_database(self):
        """Initialize the database"""
        # Create directory if needed
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir)
            
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Create interactions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS interactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    type TEXT NOT NULL,
                    content TEXT NOT NULL,
                    metadata TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create indices
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_timestamp 
                ON interactions(timestamp DESC)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_type 
                ON interactions(type)
            """)
            
            conn.commit()
            
        finally:
            conn.close()
            
    def _store_long_term(self, interaction: Dict[str, Any]):
        """Store interaction in long-term memory"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO interactions (timestamp, type, content, metadata)
                VALUES (?, ?, ?, ?)
            """, (
                interaction['timestamp'],
                interaction['type'],
                json.dumps(interaction['content']),
                json.dumps(interaction['metadata'])
            ))
            
            conn.commit()
            
        except Exception as e:
            logger.error(f"Error storing interaction: {e}")
            
        finally:
            conn.close()
            
    def get_statistics(self) -> Dict[str, Any]:
        """Get memory statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Total interactions
            cursor.execute("SELECT COUNT(*) FROM interactions")
            total_interactions = cursor.fetchone()[0]
            
            # Interactions by type
            cursor.execute("""
                SELECT type, COUNT(*) as count 
                FROM interactions 
                GROUP BY type
            """)
            
            type_counts = {row[0]: row[1] for row in cursor.fetchall()}
            
            return {
                'total_interactions': total_interactions,
                'short_term_size': len(self.short_term_memory),
                'interactions_by_type': type_counts,
                'database_path': self.db_path
            }
            
        finally:
            conn.close()