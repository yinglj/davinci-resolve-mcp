"""
Task executor that runs plans against DaVinci Resolve
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from concurrent.futures import ThreadPoolExecutor
import traceback

from ..planner.plan import Plan, PlanStep, StepType
from .skills.create_placeholder_timeline import create_placeholder_timeline

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
        
        # set current plan context for parameter resolution
        self._current_plan = plan

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
            elif step.step_type == StepType.FUSION_COMPOSITION:
                return await self._execute_fusion_composition(step)
            elif step.step_type == StepType.COLOR_AUTOMATION:
                return await self._execute_color_automation(step)
            elif step.step_type == StepType.AUDIO_PROCESSING:
                return await self._execute_audio_processing(step)
            elif step.step_type == StepType.TTS_GENERATION:
                return await self._execute_tts_generation(step)
            else:
                raise ValueError(f"Unknown step type: {step.step_type}")
                
        except Exception as e:
            logger.error(f"Error executing step {step.step_id}: {e}")
            logger.error(traceback.format_exc())
            raise
            
    async def _execute_resolve_api(self, step: PlanStep) -> Any:
        """Execute a DaVinci Resolve API call"""
        action = step.action
        params = step.parameters or {}

        # Resolve any parameter references to previous steps (e.g., shots_reference_step)
        resolved_params = {}
        for k, v in params.items():
            if isinstance(k, str) and k.endswith('_reference_step') and isinstance(v, str):
                # Look up the referenced step in the current plan
                ref_step = None
                if hasattr(self, '_current_plan') and self._current_plan:
                    for s in self._current_plan.steps:
                        if s.step_id == v:
                            ref_step = s
                            break
                if ref_step:
                    # Prefer actual result if available, fallback to parameters
                    if ref_step.result is not None:
                        resolved_params[k.replace('_reference_step', '')] = ref_step.result
                    else:
                        # Common case: the referenced step put 'shots' in its parameters
                        resolved_params[k.replace('_reference_step', '')] = ref_step.parameters.get('shots', ref_step.parameters)
                else:
                    resolved_params[k.replace('_reference_step', '')] = v
            else:
                resolved_params[k] = v
        
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
            
            # Run in thread pool to avoid blocking, using resolved params
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                self.executor,
                lambda: tool_func(**resolved_params) if resolved_params else tool_func()
            )
            return result
        else:
            # Try with get_ prefix for resources
            if f"get_{action}" in tools:
                tool_func = tools[f"get_{action}"]
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(
                    self.executor,
                    lambda: tool_func(**resolved_params) if resolved_params else tool_func()
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
        
    async def _execute_fusion_composition(self, step: PlanStep) -> Any:
        """Execute Fusion Dynamic Composition operations"""
        from .skills.fusion_executor import (
            create_fusion_page,
            create_effect_chain,
            add_transition,
            create_nested_composition,
            get_fusion_composition_status
        )
        from ..planner.skills.fusion_composition import plan_fusion_composition
        
        action = step.action
        params = step.parameters or {}
        
        try:
            if action == "plan_fusion_composition":
                # Call the planner to generate composition plan
                result = plan_fusion_composition(
                    script_summary=params.get("script_summary"),
                    shot_list=params.get("shot_list"),
                    style=params.get("style", "modern"),
                    effect_intensity=params.get("effect_intensity", 0.7),
                    enable_3d=params.get("enable_3d", False)
                )
                logger.info(f"Fusion composition plan generated: {len(result.get('layers', []))} layers")
                return result
                
            elif action == "create_fusion_page":
                # Create Fusion page and apply the composition from previous step
                result = create_fusion_page(self.resolve_server)
                logger.info(f"Fusion page created: {result}")
                return result
                
            elif action == "create_effect_chain":
                # Apply effect chain
                result = create_effect_chain(
                    effect_list=params.get("effect_list", []),
                    layer_name=params.get("layer_name", "Layer1"),
                    resolve_obj=self.resolve_server
                )
                logger.info(f"Effect chain applied to {params.get('layer_name')}")
                return result
                
            elif action == "add_transition":
                # Create transition between layers
                result = add_transition(
                    transition_type=params.get("transition_type", "Dissolve"),
                    duration=params.get("duration", 500),
                    from_layer=params.get("from_layer"),
                    to_layer=params.get("to_layer"),
                    parameters=params.get("parameters", {})
                )
                logger.info(f"Transition added: {params.get('transition_type')}")
                return result
                
            elif action == "create_nested_composition":
                # Create nested composition
                result = create_nested_composition(
                    comp_name=params.get("comp_name"),
                    layer_indices=params.get("layer_indices", []),
                    resolve_obj=self.resolve_server
                )
                logger.info(f"Nested composition created: {params.get('comp_name')}")
                return result
                
            elif action == "get_fusion_status":
                # Get composition status
                result = get_fusion_composition_status(self.resolve_server)
                logger.info(f"Fusion composition status retrieved")
                return result
                
            else:
                raise ValueError(f"Unknown Fusion action: {action}")
                
        except Exception as e:
            logger.error(f"Error executing Fusion composition step: {e}")
            raise
            
    async def _execute_color_automation(self, step: PlanStep) -> Any:
        """Execute Color Automation operations"""
        from .skills.resolve_advanced_integration import (
            apply_color_grade_with_automation,
            export_color_metadata
        )
        
        action = step.action
        params = step.parameters or {}
        
        try:
            if action == "apply_color_grade_with_automation":
                # Apply color grading with automated keyframes
                result = apply_color_grade_with_automation(
                    shots=params.get("shots"),
                    style=params.get("style", "cinematic"),
                    auto_keyframes=params.get("auto_keyframes", True),
                    enable_temporal_smoothing=params.get("enable_temporal_smoothing", True)
                )
                logger.info(f"Color automation applied: {result.get('keyframes_created', 0)} keyframes created")
                return result
                
            elif action == "export_color_metadata":
                # Export color metadata
                result = export_color_metadata(
                    timeline_name=params.get("timeline_name")
                )
                logger.info(f"Color metadata exported")
                return result
                
            else:
                raise ValueError(f"Unknown Color automation action: {action}")
                
        except Exception as e:
            logger.error(f"Error executing Color automation step: {e}")
            raise
            
    async def _execute_audio_processing(self, step: PlanStep) -> Any:
        """Execute Audio Processing operations"""
        from .skills.resolve_advanced_integration import (
            create_fairlight_audio_chain,
            monitor_audio_levels
        )
        
        action = step.action
        params = step.parameters or {}
        
        try:
            if action == "create_fairlight_audio_chain":
                # Create Fairlight audio chain
                result = create_fairlight_audio_chain(
                    target_loudness=params.get("target_loudness", -23.0),
                    compression_ratio=params.get("compression_ratio", 4.0),
                    gate_threshold=params.get("gate_threshold", -40.0),
                    eq_profile=params.get("eq_profile", "neutral"),
                    resolve_obj=self.resolve_server
                )
                logger.info(f"Fairlight audio chain created with EQ profile: {params.get('eq_profile')}")
                return result
                
            elif action == "monitor_audio_levels":
                # Monitor audio levels
                result = monitor_audio_levels(
                    timeline_name=params.get("timeline_name"),
                    duration_seconds=params.get("duration_seconds", 30)
                )
                logger.info(f"Audio levels monitored: LUFS={result.get('lufs', 'N/A')}")
                return result
                
            else:
                raise ValueError(f"Unknown Audio processing action: {action}")
                
        except Exception as e:
            logger.error(f"Error executing Audio processing step: {e}")
            raise

    async def _execute_tts_generation(self, step: PlanStep) -> Any:
        """Execute TTS Generation operations"""
        from .skills.resolve_color_and_audio import generate_tts_voiceover

        action = step.action
        params = step.parameters or {}

        try:
            if action == "generate_tts_voiceover":
                # Generate TTS voiceover
                result = generate_tts_voiceover(
                    text=params.get("text"),
                    voice=params.get("voice", "en-US-Neural2-F"),
                    speed=params.get("speed", 1.0),
                    output_path=params.get("output_path"),
                    resolve_obj=self.resolve_server
                )
                logger.info(f"TTS voiceover generated: {result.get('output_path', 'unknown')}")
                return result

            else:
                raise ValueError(f"Unknown TTS generation action: {action}")

        except Exception as e:
            logger.error(f"Error executing TTS generation step: {e}")
            raise

    def cleanup(self):
        """Cleanup resources"""
        self.executor.shutdown(wait=True)