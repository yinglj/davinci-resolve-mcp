"""
Feedback loop for error correction and continuous improvement
"""

import logging
import re
from typing import Dict, Any, List, Optional
from .validation import ValidationResult, ValidationError

logger = logging.getLogger(__name__)


class FeedbackLoop:
    """Handles validation, error correction, and learning from feedback"""
    
    def __init__(self):
        self.error_patterns = self._initialize_error_patterns()
        self.correction_strategies = self._initialize_correction_strategies()
        self.learned_patterns = {}
        
    async def validate_result(self, plan: Any, result: Dict[str, Any], context: Any) -> ValidationResult:
        """
        Validate the result of plan execution
        
        Args:
            plan: The executed plan
            result: The execution result
            context: Current context
            
        Returns:
            ValidationResult with any errors found
        """
        validation = ValidationResult(is_valid=True)
        
        # Check if plan completed successfully
        if not result.get('success', False):
            validation.add_error(
                'execution_failed',
                'Plan execution did not complete successfully',
                {'progress': result.get('progress', 0)}
            )
            
        # Validate individual step results
        for action in result.get('executed_actions', []):
            if action.get('error'):
                validation.add_error(
                    'step_error',
                    f"Step '{action['action']}' failed: {action['error']}",
                    {'action': action['action'], 'parameters': action.get('parameters')}
                )
                
        # Check expected outcomes
        for step in plan.steps:
            if step.executed and step.expected_outcome:
                if not self._check_outcome(step.result, step.expected_outcome):
                    validation.add_warning(
                        f"Step '{step.action}' outcome differs from expected: {step.expected_outcome}"
                    )
                    
        return validation
        
    async def fix_plan(self, plan: Any, errors: List[ValidationError], doc_rag: Any) -> Any:
        """
        Attempt to fix a plan based on validation errors
        
        Args:
            plan: The original plan
            errors: List of validation errors
            doc_rag: Documentation RAG for looking up fixes
            
        Returns:
            Fixed plan
        """
        # Clone the plan for modification
        fixed_plan = self._clone_plan(plan)
        
        for error in errors:
            # Find correction strategy
            strategy = self._find_correction_strategy(error)
            
            if strategy:
                # Apply the correction
                await self._apply_correction(fixed_plan, error, strategy, doc_rag)
            else:
                # Look up in documentation
                fix_info = await doc_rag.query(f"fix error: {error.message}")
                if fix_info:
                    await self._apply_documentation_fix(fixed_plan, error, fix_info)
                    
        return fixed_plan
        
    async def create_recovery_plan(self, plan: Any, exception: Exception, doc_rag: Any) -> Optional[Any]:
        """
        Create a recovery plan from an exception
        
        Args:
            plan: The failed plan
            exception: The exception that occurred
            doc_rag: Documentation RAG
            
        Returns:
            Recovery plan or None if recovery not possible
        """
        error_msg = str(exception).lower()
        
        # Check known error patterns
        for pattern, recovery_func in self.error_patterns.items():
            if re.search(pattern, error_msg):
                return await recovery_func(plan, exception, doc_rag)
                
        # Generic recovery attempt
        return await self._generic_recovery(plan, exception, doc_rag)
        
    async def update_patterns(self, task_id: str, feedback: str, success: bool):
        """Learn from user feedback"""
        # Store the pattern for future use
        self.learned_patterns[task_id] = {
            'feedback': feedback,
            'success': success
        }
        
        # Update correction strategies if needed
        if not success:
            # Extract potential fix from feedback
            fix_pattern = self._extract_fix_pattern(feedback)
            if fix_pattern:
                self.correction_strategies[fix_pattern['error']] = fix_pattern['fix']
                
    def _initialize_error_patterns(self) -> Dict[str, Any]:
        """Initialize known error patterns and recovery functions"""
        return {
            r'not connected.*resolve': self._recover_connection_error,
            r'no project.*open': self._recover_no_project,
            r'timeline.*not found': self._recover_timeline_not_found,
            r'media.*not found': self._recover_media_not_found,
            r'permission.*denied': self._recover_permission_error,
        }
        
    def _initialize_correction_strategies(self) -> Dict[str, Dict[str, Any]]:
        """Initialize correction strategies for known errors"""
        return {
            'execution_failed': {
                'strategy': 'retry_with_modifications',
                'modifications': ['check_prerequisites', 'add_validation_steps']
            },
            'step_error': {
                'strategy': 'fix_parameters',
                'modifications': ['validate_parameters', 'add_error_handling']
            },
            'missing_dependency': {
                'strategy': 'add_dependency_steps',
                'modifications': ['create_missing_resources']
            }
        }
        
    async def _recover_connection_error(self, plan: Any, exception: Exception, doc_rag: Any) -> Any:
        """Recover from connection errors"""
        from ..planner.plan import Plan, PlanStep, StepType
        
        recovery_plan = Plan(summary="Recovery: Reconnect to DaVinci Resolve")
        
        # Add steps to check and restart Resolve if needed
        recovery_plan.add_step(PlanStep(
            step_type=StepType.VALIDATION,
            action="check_resolve_running",
            expected_outcome="DaVinci Resolve is running"
        ))
        
        recovery_plan.add_step(PlanStep(
            step_type=StepType.RESOLVE_API,
            action="restart_app",
            parameters={'wait_seconds': 10},
            expected_outcome="DaVinci Resolve restarted"
        ))
        
        # Then retry original plan
        for step in plan.steps:
            if not step.executed:
                recovery_plan.add_step(step)
                
        return recovery_plan
        
    async def _recover_no_project(self, plan: Any, exception: Exception, doc_rag: Any) -> Any:
        """Recover from no project open error"""
        from ..planner.plan import Plan, PlanStep, StepType
        
        recovery_plan = Plan(summary="Recovery: Open project")
        
        # Try to open the last project or create a new one
        recovery_plan.add_step(PlanStep(
            step_type=StepType.RESOLVE_API,
            action="list_projects",
            expected_outcome="Get available projects"
        ))
        
        recovery_plan.add_step(PlanStep(
            step_type=StepType.RESOLVE_API,
            action="open_project",
            parameters={'name': 'AutoRecovery'},  # This would be dynamic
            expected_outcome="Project opened"
        ))
        
        # Then continue with original plan
        for step in plan.steps:
            if not step.executed:
                recovery_plan.add_step(step)
                
        return recovery_plan
        
    async def _recover_timeline_not_found(self, plan: Any, exception: Exception, doc_rag: Any) -> Any:
        """Recover from timeline not found error"""
        from ..planner.plan import Plan, PlanStep, StepType
        
        recovery_plan = Plan(summary="Recovery: Create timeline")
        
        # Create a new timeline
        recovery_plan.add_step(PlanStep(
            step_type=StepType.RESOLVE_API,
            action="create_empty_timeline",
            parameters={'name': 'Recovery Timeline'},
            expected_outcome="Timeline created"
        ))
        
        # Continue with modified plan
        for step in plan.steps:
            if not step.executed and 'timeline' not in step.action.lower():
                recovery_plan.add_step(step)
                
        return recovery_plan
        
    async def _recover_media_not_found(self, plan: Any, exception: Exception, doc_rag: Any) -> Any:
        """Recover from media not found error"""
        # This would implement media recovery logic
        return None
        
    async def _recover_permission_error(self, plan: Any, exception: Exception, doc_rag: Any) -> Any:
        """Recover from permission errors"""
        # This would handle permission issues
        return None
        
    async def _generic_recovery(self, plan: Any, exception: Exception, doc_rag: Any) -> Any:
        """Generic recovery attempt"""
        # Look up the error in documentation
        error_info = await doc_rag.query(f"error: {str(exception)}")
        
        if error_info:
            # Create recovery plan based on documentation
            # This would be more sophisticated in practice
            return None
            
        return None
        
    def _clone_plan(self, plan: Any) -> Any:
        """Create a deep copy of a plan"""
        # This would implement proper plan cloning
        # For now, return the original
        return plan
        
    def _find_correction_strategy(self, error: ValidationError) -> Optional[Dict[str, Any]]:
        """Find correction strategy for an error"""
        return self.correction_strategies.get(error.error_type)
        
    async def _apply_correction(self, plan: Any, error: ValidationError, strategy: Dict[str, Any], doc_rag: Any):
        """Apply a correction strategy to a plan"""
        if strategy['strategy'] == 'retry_with_modifications':
            # Add validation steps before failed steps
            for step in plan.steps:
                if step.error:
                    # Add prerequisite check
                    self._add_validation_step(plan, step)
                    
        elif strategy['strategy'] == 'fix_parameters':
            # Fix parameters based on error
            for step in plan.steps:
                if step.error and error.context.get('action') == step.action:
                    # Look up correct parameters
                    correct_params = await doc_rag.query(f"parameters for {step.action}")
                    if correct_params:
                        step.parameters.update(correct_params)
                        
    async def _apply_documentation_fix(self, plan: Any, error: ValidationError, fix_info: str):
        """Apply fix from documentation"""
        # Parse fix info and modify plan accordingly
        # This would be more sophisticated in practice
        pass
        
    def _add_validation_step(self, plan: Any, before_step: Any):
        """Add a validation step before another step"""
        from ..planner.plan import PlanStep, StepType
        
        validation_step = PlanStep(
            step_type=StepType.VALIDATION,
            action="validate_prerequisites",
            parameters={'for_action': before_step.action},
            expected_outcome="Prerequisites met"
        )
        
        # Insert before the target step
        idx = plan.steps.index(before_step)
        plan.steps.insert(idx, validation_step)
        
        # Update dependencies
        before_step.dependencies.append(validation_step.step_id)
        
    def _check_outcome(self, result: Any, expected: str) -> bool:
        """Check if result matches expected outcome"""
        # Simple string matching for now
        # Could be more sophisticated
        return expected.lower() in str(result).lower()
        
    def _extract_fix_pattern(self, feedback: str) -> Optional[Dict[str, str]]:
        """Extract fix pattern from user feedback"""
        # Look for patterns like "should have done X instead of Y"
        fix_match = re.search(r'should (?:have )?(.+) instead of (.+)', feedback, re.IGNORECASE)
        if fix_match:
            return {
                'fix': fix_match.group(1),
                'error': fix_match.group(2)
            }
            
        return None