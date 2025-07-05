"""
Agent state management for tracking task progress and status
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum
import uuid


class TaskStatus(Enum):
    """Task status enumeration"""
    PENDING = "pending"
    PLANNING = "planning"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"


class AgentState:
    """Manages the state of the agent and task execution"""
    
    def __init__(self):
        self.tasks = {}  # task_id -> task_info
        self.current_task_id = None
        self.is_busy = False
        self.error_count = 0
        self.success_count = 0
        self.start_time = datetime.now()
        
    def create_task(self, description: str) -> str:
        """Create a new task and return its ID"""
        task_id = str(uuid.uuid4())
        self.tasks[task_id] = {
            'id': task_id,
            'description': description,
            'status': TaskStatus.PENDING,
            'created_at': datetime.now(),
            'started_at': None,
            'completed_at': None,
            'error': None,
            'retries': 0,
            'subtasks': []
        }
        return task_id
        
    def start_task(self, task_id: str):
        """Mark a task as started"""
        if task_id in self.tasks:
            self.tasks[task_id]['status'] = TaskStatus.EXECUTING
            self.tasks[task_id]['started_at'] = datetime.now()
            self.current_task_id = task_id
            self.is_busy = True
            
    def mark_task_complete(self, task_id: str):
        """Mark a task as completed"""
        if task_id in self.tasks:
            self.tasks[task_id]['status'] = TaskStatus.COMPLETED
            self.tasks[task_id]['completed_at'] = datetime.now()
            self.success_count += 1
            if self.current_task_id == task_id:
                self.current_task_id = None
                self.is_busy = False
                
    def mark_task_failed(self, task_id: str, error: str):
        """Mark a task as failed"""
        if task_id in self.tasks:
            self.tasks[task_id]['status'] = TaskStatus.FAILED
            self.tasks[task_id]['error'] = error
            self.tasks[task_id]['completed_at'] = datetime.now()
            self.error_count += 1
            if self.current_task_id == task_id:
                self.current_task_id = None
                self.is_busy = False
                
    def mark_task_retrying(self, task_id: str):
        """Mark a task as retrying"""
        if task_id in self.tasks:
            self.tasks[task_id]['status'] = TaskStatus.RETRYING
            self.tasks[task_id]['retries'] += 1
            
    def add_subtask(self, parent_task_id: str, subtask_description: str) -> str:
        """Add a subtask to a parent task"""
        subtask_id = self.create_task(subtask_description)
        if parent_task_id in self.tasks:
            self.tasks[parent_task_id]['subtasks'].append(subtask_id)
        return subtask_id
        
    def get_task_info(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific task"""
        return self.tasks.get(task_id)
        
    def get_current_task(self) -> Optional[Dict[str, Any]]:
        """Get the current task being executed"""
        if self.current_task_id:
            return self.tasks.get(self.current_task_id)
        return None
        
    def get_task_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent task history"""
        sorted_tasks = sorted(
            self.tasks.values(),
            key=lambda x: x['created_at'],
            reverse=True
        )
        return sorted_tasks[:limit]
        
    def get_statistics(self) -> Dict[str, Any]:
        """Get agent statistics"""
        total_tasks = len(self.tasks)
        uptime = (datetime.now() - self.start_time).total_seconds()
        
        return {
            'total_tasks': total_tasks,
            'success_count': self.success_count,
            'error_count': self.error_count,
            'success_rate': self.success_count / total_tasks if total_tasks > 0 else 0,
            'uptime_seconds': uptime,
            'is_busy': self.is_busy,
            'current_task': self.get_current_task()
        }
        
    def reset_statistics(self):
        """Reset statistics"""
        self.error_count = 0
        self.success_count = 0
        self.start_time = datetime.now()