"""
DaVinci Resolve AI Agent - An intelligent copilot for video editing
"""

from .core import ResolveAgent, AgentContext, AgentState
from .planner import TaskPlanner, Plan, PlanStep
from .executor import TaskExecutor
from .vision import VideoAnalyzer
from .rag import ResolveDocRAG
from .feedback import FeedbackLoop, ValidationResult
from .memory import MemoryManager

__version__ = "1.0.0"

__all__ = [
    'ResolveAgent',
    'AgentContext',
    'AgentState',
    'TaskPlanner',
    'Plan',
    'PlanStep',
    'TaskExecutor',
    'VideoAnalyzer',
    'ResolveDocRAG',
    'FeedbackLoop',
    'ValidationResult',
    'MemoryManager'
]