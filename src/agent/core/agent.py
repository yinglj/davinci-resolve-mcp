"""
Main agent class for DaVinci Resolve AI Copilot
Handles planning, execution, and self-correction
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
import json

from ..planner import TaskPlanner
from ..executor import TaskExecutor
from ..vision import VideoAnalyzer
from ..rag import ResolveDocRAG
from ..feedback import FeedbackLoop
from ..memory import MemoryManager
from .context import AgentContext
from .state import AgentState

logger = logging.getLogger(__name__)


class ResolveAgent:
    """
    Main AI agent that controls DaVinci Resolve through intelligent planning and execution
    """
    
    def __init__(self, resolve_server=None):
        """Initialize the agent with all necessary components"""
        self.resolve_server = resolve_server
        self.state = AgentState()
        self.context = AgentContext()
        
        # Initialize core components
        self.planner = TaskPlanner()
        self.executor = TaskExecutor(resolve_server)
        self.video_analyzer = VideoAnalyzer()
        self.doc_rag = ResolveDocRAG()
        self.feedback_loop = FeedbackLoop()
        self.memory = MemoryManager()
        
        # Track current task and history
        self.current_task = None
        self.task_history = []
        
        logger.info("ResolveAgent initialized")
    
    async def process_request(self, user_request: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Process a user request through the full agent pipeline
        
        Args:
            user_request: Natural language request from user
            context: Optional context information
            
        Returns:
            Dict containing result and any relevant information
        """
        try:
            # Update context with user request
            self.context.update_user_request(user_request)
            if context:
                self.context.update_external_context(context)
            
            # Store in memory
            self.memory.add_interaction(user_request, "request")
            
            # Plan the task
            plan = await self.planner.create_plan(
                user_request, 
                self.context,
                self.doc_rag
            )
            
            # Execute the plan with feedback loop
            result = await self._execute_with_feedback(plan)
            
            # Store result in memory
            self.memory.add_interaction(result, "response")
            
            # Update state
            self.state.mark_task_complete(plan.task_id)
            
            return {
                'success': True,
                'result': result,
                'plan_summary': plan.summary,
                'actions_taken': plan.get_executed_actions()
            }
            
        except Exception as e:
            logger.error(f"Error processing request: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'recovery_suggestions': self._get_recovery_suggestions(e)
            }
    
    async def _execute_with_feedback(self, plan):
        """Execute a plan with automatic error correction"""
        max_retries = 3
        current_retry = 0
        
        while current_retry < max_retries:
            try:
                # Execute the plan
                result = await self.executor.execute_plan(plan)
                
                # Validate the result
                validation = await self.feedback_loop.validate_result(
                    plan, 
                    result,
                    self.context
                )
                
                if validation.is_valid:
                    return result
                else:
                    # Fix identified issues
                    fixed_plan = await self.feedback_loop.fix_plan(
                        plan,
                        validation.errors,
                        self.doc_rag
                    )
                    plan = fixed_plan
                    current_retry += 1
                    
            except Exception as e:
                logger.error(f"Execution error (attempt {current_retry + 1}): {str(e)}")
                
                # Try to recover from error
                recovery_plan = await self.feedback_loop.create_recovery_plan(
                    plan,
                    e,
                    self.doc_rag
                )
                
                if recovery_plan:
                    plan = recovery_plan
                    current_retry += 1
                else:
                    raise
        
        raise Exception(f"Failed to execute plan after {max_retries} attempts")
    
    async def analyze_video(self, video_path: str, analysis_type: str = "general") -> Dict[str, Any]:
        """
        Analyze video content using vision models
        
        Args:
            video_path: Path to video file or timeline clip
            analysis_type: Type of analysis (general, color, composition, etc.)
        """
        return await self.video_analyzer.analyze(video_path, analysis_type)
    
    async def get_documentation(self, topic: str) -> str:
        """Retrieve relevant documentation using RAG"""
        return await self.doc_rag.query(topic)
    
    async def suggest_next_actions(self) -> List[str]:
        """Suggest next actions based on current context"""
        return await self.planner.suggest_next_actions(
            self.context,
            self.memory.get_recent_actions()
        )
    
    def _get_recovery_suggestions(self, error: Exception) -> List[str]:
        """Get suggestions for recovering from an error"""
        suggestions = []
        
        error_msg = str(error).lower()
        
        if "not connected" in error_msg:
            suggestions.append("Ensure DaVinci Resolve is running")
            suggestions.append("Check if the API server is properly initialized")
        elif "project" in error_msg:
            suggestions.append("Verify a project is open")
            suggestions.append("Check project permissions")
        elif "timeline" in error_msg:
            suggestions.append("Ensure a timeline exists and is selected")
        elif "media" in error_msg:
            suggestions.append("Check if media files are accessible")
            suggestions.append("Verify media pool contains the referenced clips")
        
        return suggestions
    
    async def learn_from_feedback(self, task_id: str, feedback: str, success: bool):
        """Learn from user feedback to improve future performance"""
        await self.memory.store_feedback(task_id, feedback, success)
        await self.feedback_loop.update_patterns(task_id, feedback, success)