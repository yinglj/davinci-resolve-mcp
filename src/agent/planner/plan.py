"""
Plan representation for task execution
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import uuid
from enum import Enum


class StepType(Enum):
    """Types of plan steps"""
    RESOLVE_API = "resolve_api"
    VIDEO_ANALYSIS = "video_analysis"
    DOCUMENTATION = "documentation"
    VALIDATION = "validation"
    COMPOSITE = "composite"


@dataclass
class PlanStep:
    """Represents a single step in a plan"""
    step_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    step_type: StepType = StepType.RESOLVE_API
    action: str = ""
    parameters: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)  # step_ids this depends on
    expected_outcome: str = ""
    validation_criteria: Dict[str, Any] = field(default_factory=dict)
    retry_count: int = 0
    max_retries: int = 3
    executed: bool = False
    result: Optional[Any] = None
    error: Optional[str] = None
    
    def can_execute(self, completed_steps: List[str]) -> bool:
        """Check if this step can be executed based on dependencies"""
        return all(dep in completed_steps for dep in self.dependencies)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'step_id': self.step_id,
            'step_type': self.step_type.value,
            'action': self.action,
            'parameters': self.parameters,
            'dependencies': self.dependencies,
            'expected_outcome': self.expected_outcome,
            'validation_criteria': self.validation_criteria,
            'executed': self.executed,
            'result': self.result,
            'error': self.error
        }


@dataclass
class Plan:
    """Represents a complete execution plan"""
    task_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    summary: str = ""
    steps: List[PlanStep] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    context: Dict[str, Any] = field(default_factory=dict)
    completed_steps: List[str] = field(default_factory=list)
    failed_steps: List[str] = field(default_factory=list)
    
    def add_step(self, step: PlanStep):
        """Add a step to the plan"""
        self.steps.append(step)
        
    def get_next_steps(self) -> List[PlanStep]:
        """Get the next steps that can be executed"""
        return [
            step for step in self.steps
            if not step.executed and step.can_execute(self.completed_steps)
        ]
        
    def mark_step_complete(self, step_id: str, result: Any = None):
        """Mark a step as completed"""
        for step in self.steps:
            if step.step_id == step_id:
                step.executed = True
                step.result = result
                if step_id not in self.completed_steps:
                    self.completed_steps.append(step_id)
                break
                
    def mark_step_failed(self, step_id: str, error: str):
        """Mark a step as failed"""
        for step in self.steps:
            if step.step_id == step_id:
                step.error = error
                step.retry_count += 1
                if step_id not in self.failed_steps:
                    self.failed_steps.append(step_id)
                break
                
    def get_executed_actions(self) -> List[Dict[str, Any]]:
        """Get list of executed actions with their results"""
        return [
            {
                'action': step.action,
                'parameters': step.parameters,
                'result': step.result,
                'error': step.error
            }
            for step in self.steps if step.executed
        ]
        
    def is_complete(self) -> bool:
        """Check if the plan is complete"""
        return all(step.executed for step in self.steps)
        
    def get_progress(self) -> float:
        """Get plan progress as percentage"""
        if not self.steps:
            return 0.0
        return len(self.completed_steps) / len(self.steps) * 100
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'task_id': self.task_id,
            'summary': self.summary,
            'steps': [step.to_dict() for step in self.steps],
            'created_at': self.created_at.isoformat(),
            'context': self.context,
            'completed_steps': self.completed_steps,
            'failed_steps': self.failed_steps,
            'progress': self.get_progress()
        }