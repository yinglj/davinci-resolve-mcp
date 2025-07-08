"""
Task executor that runs plans against DaVinci Resolve
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from concurrent.futures import ThreadPoolExecutor
import traceback

from ..planner.plan import Plan, PlanStep, StepType

logger = logging.getLogger(__name__)


class TaskExecutor:
    """Executes plans by calling the appropriate APIs"""
    
    def __init__(self, resolve_server):
        self.resolve_server = resolve_server
        self.executor = ThreadPoolExecutor(max_workers=4)
        
    async def execute_plan(self, plan: Plan) -> Dict[str, Any]:
        """
        Execute a complete plan
        
        Args:
            plan: The plan to execute
            
        Returns:
            Dict with execution results
        """
        results = []
        
        while not plan.is_complete():
            # Get next steps that can be executed
            next_steps = plan.get_next_steps()
            
            if not next_steps:
                # No steps can be executed - might be dependency issue
                logger.error("No executable steps found but plan not complete")
                break
                
            # Execute steps in parallel where possible
            step_results = await asyncio.gather(
                *[self._execute_step(step) for step in next_steps],
                return_exceptions=True
            )
            
            # Process results
            for step, result in zip(next_steps, step_results):
                if isinstance(result, Exception):
                    plan.mark_step_failed(step.step_id, str(result))
                    logger.error(f"Step {step.step_id} failed: {result}")
                    
                    # Check if we should retry
                    if step.retry_count < step.max_retries:
                        step.executed = False  # Reset for retry
                        continue
                    else:
                        # Max retries exceeded
                        raise result
                else:
                    plan.mark_step_complete(step.step_id, result)
                    results.append({
                        'step': step.action,
                        'result': result
                    })
                    
        return {
            'success': plan.is_complete(),
            'results': results,
            'progress': plan.get_progress(),
            'executed_actions': plan.get_executed_actions()
        }
        
    async def _execute_step(self, step: PlanStep) -> Any:
        """Execute a single step"""
        logger.info(f"Executing step: {step.action} ({step.step_type.value})")
        
        try:
            if step.step_type == StepType.RESOLVE_API:
                return await self._execute_resolve_api(step)
            elif step.step_type == StepType.VIDEO_ANALYSIS:
                return await self._execute_video_analysis(step)
            elif step.step_type == StepType.DOCUMENTATION:
                return await self._execute_documentation_lookup(step)
            elif step.step_type == StepType.VALIDATION:
                return await self._execute_validation(step)
            elif step.step_type == StepType.COMPOSITE:
                return await self._execute_composite(step)
            else:
                raise ValueError(f"Unknown step type: {step.step_type}")
                
        except Exception as e:
            logger.error(f"Error executing step {step.step_id}: {e}")
            logger.error(traceback.format_exc())
            raise
            
    async def _execute_resolve_api(self, step: PlanStep) -> Any:
        """Execute a DaVinci Resolve API call"""
        action = step.action
        params = step.parameters
        
        # Get all tools from the MCP server
        tools = {}
        
        # Tools are stored in the _tools dictionary
        if hasattr(self.resolve_server, '_tools'):
            tools.update(self.resolve_server._tools)
        
        # Resources are stored in the _resources dictionary
        if hasattr(self.resolve_server, '_resources'):
            # Resources can be called as read-only operations
            for resource_name, resource_func in self.resolve_server._resources.items():
                # Convert resource to callable tool format
                tools[f"get_{resource_name}"] = resource_func
        
        # Find the matching tool
        if action in tools:
            tool_func = tools[action]
            
            # Run in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                self.executor,
                lambda: tool_func(**params) if params else tool_func()
            )
            return result
        else:
            # Try with get_ prefix for resources
            if f"get_{action}" in tools:
                tool_func = tools[f"get_{action}"]
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(
                    self.executor,
                    lambda: tool_func(**params) if params else tool_func()
                )
                return result
            
            raise ValueError(f"Unknown Resolve API action: {action}")
            
    async def _execute_video_analysis(self, step: PlanStep) -> Any:
        """Execute video analysis (placeholder for now)"""
        # This would integrate with video understanding models
        logger.info(f"Video analysis requested: {step.parameters}")
        
        # Placeholder implementation
        return {
            'analysis_type': step.parameters.get('analysis_type', 'general'),
            'video_path': step.parameters.get('video_path'),
            'results': {
                'scenes_detected': 5,
                'average_brightness': 0.7,
                'dominant_colors': ['blue', 'green'],
                'motion_intensity': 'medium'
            }
        }
        
    async def _execute_documentation_lookup(self, step: PlanStep) -> Any:
        """Execute documentation lookup"""
        query = step.parameters.get('query', '')
        
        # This would use the RAG system
        # Placeholder for now
        return {
            'query': query,
            'results': [
                {
                    'command': 'example_command',
                    'description': 'Example command description',
                    'parameters': ['param1', 'param2']
                }
            ]
        }
        
    async def _execute_validation(self, step: PlanStep) -> Any:
        """Execute validation step"""
        # Validate previous step results
        validation_criteria = step.validation_criteria
        
        # Placeholder validation
        return {
            'valid': True,
            'criteria_met': list(validation_criteria.keys())
        }
        
    async def _execute_composite(self, step: PlanStep) -> Any:
        """Execute composite step (multiple actions)"""
        sub_results = []
        
        for sub_action in step.parameters.get('actions', []):
            sub_step = PlanStep(
                step_type=StepType.RESOLVE_API,
                action=sub_action['action'],
                parameters=sub_action.get('parameters', {})
            )
            result = await self._execute_step(sub_step)
            sub_results.append(result)
            
        return {
            'composite_results': sub_results
        }
        
    def cleanup(self):
        """Cleanup resources"""
        self.executor.shutdown(wait=True)