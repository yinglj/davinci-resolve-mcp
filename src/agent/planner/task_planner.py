"""
Task planner that converts user requests into executable plans
"""

import re
import logging
from typing import List, Dict, Any, Optional, Tuple
from .plan import Plan, PlanStep, StepType
from .skills import parse_script_to_shots

logger = logging.getLogger(__name__)


class TaskPlanner:
    """Plans tasks based on user requests and context"""
    
    def __init__(self):
        self.action_patterns = self._initialize_action_patterns()
        
    async def create_plan(self, user_request: str, context: Any, doc_rag: Any) -> Plan:
        """
        Create an execution plan from a user request
        
        Args:
            user_request: Natural language request
            context: Current agent context
            doc_rag: Documentation RAG for looking up commands
        """
        # Analyze the request
        intent, entities = await self._analyze_request(user_request)
        
        # Get relevant documentation if needed
        if self._needs_documentation(intent):
            docs = await doc_rag.query(intent)
        else:
            docs = None
            
        # Create plan based on intent
        plan = Plan(summary=f"Plan for: {user_request[:100]}...")
        plan.context = context.get_full_context()
        
        # Build steps based on intent
        if intent == "create_timeline":
            await self._plan_create_timeline(plan, entities)
        elif intent == "import_media":
            await self._plan_import_media(plan, entities)
        elif intent == "color_grade":
            await self._plan_color_grade(plan, entities)
        elif intent == "export_video":
            await self._plan_export_video(plan, entities)
        elif intent == "analyze_video":
            await self._plan_analyze_video(plan, entities)
        elif intent == "composite_effect":
            await self._plan_composite_effect(plan, entities, docs)
        else:
            # Generic planning based on action patterns
            await self._plan_generic(plan, user_request, context)
            
        return plan
        
    async def suggest_next_actions(self, context: Any, recent_actions: List[Dict]) -> List[str]:
        """Suggest next actions based on context and recent actions"""
        suggestions = []
        
        # Analyze current state
        current_state = context.resolve_state
        
        if not current_state.get('project'):
            suggestions.append("Open or create a project to start working")
        elif not current_state.get('timeline'):
            suggestions.append("Create a timeline to begin editing")
        elif not current_state.get('media_pool_has_clips'):
            suggestions.append("Import media files to the media pool")
        else:
            # Suggest based on recent actions
            last_action = recent_actions[0] if recent_actions else None
            if last_action:
                if 'import' in last_action.get('action', ''):
                    suggestions.append("Add imported clips to timeline")
                    suggestions.append("Create proxies for better performance")
                elif 'timeline' in last_action.get('action', ''):
                    suggestions.append("Apply color grading")
                    suggestions.append("Add transitions between clips")
                elif 'color' in last_action.get('action', ''):
                    suggestions.append("Export the graded timeline")
                    suggestions.append("Save color preset for future use")
                    
        return suggestions
        
    def _initialize_action_patterns(self) -> Dict[str, List[Tuple[str, str]]]:
        """Initialize patterns for detecting actions in requests"""
        return {
            'create_timeline': [
                (r'create.*timeline', 'create_timeline'),
                (r'new timeline', 'create_timeline'),
                (r'make.*timeline', 'create_timeline')
            ],
            'import_media': [
                (r'import.*media', 'import_media'),
                (r'import.*video', 'import_media'),
                (r'add.*media.*pool', 'import_media'),
                (r'import.*clips?', 'import_media')
            ],
            'color_grade': [
                (r'color grade', 'color_grade'),
                (r'apply.*lut', 'apply_lut'),
                (r'color correct', 'color_grade'),
                (r'grade.*clips?', 'color_grade')
            ],
            'export_video': [
                (r'export.*video', 'export_video'),
                (r'render.*timeline', 'export_video'),
                (r'deliver.*video', 'export_video'),
                (r'export.*project', 'export_video')
            ],
            'analyze_video': [
                (r'analyze.*video', 'analyze_video'),
                (r'check.*quality', 'analyze_video'),
                (r'detect.*scenes?', 'analyze_video'),
                (r'find.*objects?', 'analyze_video')
            ],
            'script_to_shots': [
                (r'from script', 'script_to_shots'),
                (r'script to', 'script_to_shots'),
                (r'create.*from script', 'script_to_shots'),
                (r'shot list', 'script_to_shots')
            ]
        }
        
    async def _analyze_request(self, request: str) -> Tuple[str, Dict[str, Any]]:
        """Analyze user request to extract intent and entities"""
        request_lower = request.lower()
        
        # Check action patterns
        for intent, patterns in self.action_patterns.items():
            for pattern, action in patterns:
                if re.search(pattern, request_lower):
                    # Extract entities based on intent
                    entities = await self._extract_entities(request, intent)
                    return intent, entities
                    
        # Default to generic intent
        return 'generic', {'request': request}
        
    async def _extract_entities(self, request: str, intent: str) -> Dict[str, Any]:
        """Extract entities from request based on intent"""
        entities = {}
        
        if intent == 'create_timeline':
            # Extract timeline name
            match = re.search(r'"([^"]+)"', request)
            if match:
                entities['name'] = match.group(1)
                
            # Extract resolution
            res_match = re.search(r'(\d+)x(\d+)', request)
            if res_match:
                entities['width'] = int(res_match.group(1))
                entities['height'] = int(res_match.group(2))
                
            # Extract frame rate
            fps_match = re.search(r'(\d+(?:\.\d+)?)\s*fps', request.lower())
            if fps_match:
                entities['frame_rate'] = float(fps_match.group(1))
                
        elif intent == 'import_media':
            # Extract file paths
            path_matches = re.findall(r'["\']([^"\']+)["\']', request)
            if path_matches:
                entities['paths'] = path_matches
        elif intent == 'script_to_shots':
            # For script-based requests, capture the entire request as script text
            # If user includes a colon followed by the script, extract that part
            m = re.search(r':\s*(.+)$', request, re.S)
            if m:
                entities['script'] = m.group(1).strip()
            else:
                # Fallback: use whole request
                entities['script'] = request.strip()

            # Detect BPM if the user mentions music tempo and set an auto-cut flag when present
            bpm_match = re.search(r'(\d+)\s*bpm', request.lower())
            if bpm_match:
                try:
                    entities['bpm'] = int(bpm_match.group(1))
                except Exception:
                    pass

            if 'auto cut' in request.lower() or 'autocut' in request.lower() or 'beat match' in request.lower():
                entities['auto_cut'] = True
                
        elif intent == 'color_grade':
            # Extract LUT path if mentioned
            lut_match = re.search(r'lut["\s]+([^"\s]+)', request.lower())
            if lut_match:
                entities['lut_path'] = lut_match.group(1)
                
        return entities
        
    def _needs_documentation(self, intent: str) -> bool:
        """Check if documentation lookup is needed for this intent"""
        return intent in ['composite_effect', 'generic', 'complex_workflow']
        
    async def _plan_create_timeline(self, plan: Plan, entities: Dict[str, Any]):
        """Plan timeline creation"""
        step = PlanStep(
            step_type=StepType.RESOLVE_API,
            action="create_empty_timeline",
            parameters=entities,
            expected_outcome="New timeline created"
        )
        plan.add_step(step)
        
    async def _plan_import_media(self, plan: Plan, entities: Dict[str, Any]):
        """Plan media import"""
        paths = entities.get('paths', [])
        
        for path in paths:
            step = PlanStep(
                step_type=StepType.RESOLVE_API,
                action="import_media",
                parameters={'file_path': path},
                expected_outcome=f"Media imported: {path}"
            )
            plan.add_step(step)
            
    async def _plan_color_grade(self, plan: Plan, entities: Dict[str, Any]):
        """Plan color grading operations"""
        if 'lut_path' in entities:
            step = PlanStep(
                step_type=StepType.RESOLVE_API,
                action="apply_lut",
                parameters={'lut_path': entities['lut_path']},
                expected_outcome="LUT applied to current clip"
            )
            plan.add_step(step)
        else:
            # Basic color grading
            step = PlanStep(
                step_type=StepType.RESOLVE_API,
                action="add_node",
                parameters={'node_type': 'serial', 'label': 'Color Correction'},
                expected_outcome="Color node added"
            )
            plan.add_step(step)
            
    async def _plan_export_video(self, plan: Plan, entities: Dict[str, Any]):
        """Plan video export"""
        # Add to render queue
        step1 = PlanStep(
            step_type=StepType.RESOLVE_API,
            action="add_to_render_queue",
            parameters={'preset_name': entities.get('preset', 'YouTube 1080p')},
            expected_outcome="Added to render queue"
        )
        plan.add_step(step1)
        
        # Start render
        step2 = PlanStep(
            step_type=StepType.RESOLVE_API,
            action="start_render",
            parameters={},
            dependencies=[step1.step_id],
            expected_outcome="Render started"
        )
        plan.add_step(step2)
        
    async def _plan_analyze_video(self, plan: Plan, entities: Dict[str, Any]):
        """Plan video analysis"""
        step = PlanStep(
            step_type=StepType.VIDEO_ANALYSIS,
            action="analyze_video",
            parameters={
                'video_path': entities.get('path', 'current_timeline'),
                'analysis_type': entities.get('type', 'general')
            },
            expected_outcome="Video analysis complete"
        )
        plan.add_step(step)
        
    async def _plan_composite_effect(self, plan: Plan, entities: Dict[str, Any], docs: Optional[str]):
        """Plan composite effect based on documentation"""
        # This would use the documentation to figure out the steps
        # For now, a simple implementation
        step = PlanStep(
            step_type=StepType.RESOLVE_API,
            action="switch_page",
            parameters={'page': 'fusion'},
            expected_outcome="Switched to Fusion page"
        )
        plan.add_step(step)

    async def _plan_script_to_shots(self, plan: Plan, entities: Dict[str, Any]):
        """Parse the provided script text into shots and create placeholder timeline steps"""
        script_text = entities.get('script', '')
        shots = []
        try:
            shots = parse_script_to_shots(script_text)
        except Exception as e:
            logger.exception("Failed to parse script to shots")
            # Add a documentation lookup step as fallback
            step = PlanStep(
                step_type=StepType.DOCUMENTATION,
                action="lookup_command",
                parameters={'query': script_text},
                expected_outcome="Found relevant commands or examples"
            )
            plan.add_step(step)
            return

        # Add a step that records the generated shot list
        step_shots = PlanStep(
            step_type=StepType.VALIDATION,
            action="script_to_shots",
            parameters={'shots': shots},
            expected_outcome="Shot list generated"
        )
        plan.add_step(step_shots)

        # Optionally add an AutoCut step if the user requested beat-matching or provided a BPM
        auto_cut_enabled = entities.get('auto_cut') or (entities.get('bpm') is not None)
        step_autocut = None
        if auto_cut_enabled:
            step_autocut = PlanStep(
                step_type=StepType.COMPOSITE,
                action="auto_cut",
                parameters={'shots_reference_step': step_shots.step_id, 'bpm': entities.get('bpm')},
                dependencies=[step_shots.step_id],
                expected_outcome="AutoCut computed in/out for shots"
            )
            plan.add_step(step_autocut)

        # Add a dependent step to create a placeholder timeline (depend on autotcut if present)
        timeline_dep = step_autocut.step_id if step_autocut else step_shots.step_id
        step_tl = PlanStep(
            step_type=StepType.RESOLVE_API,
            action="create_placeholder_timeline",
            parameters={'shots_reference_step': timeline_dep},
            dependencies=[timeline_dep],
            expected_outcome="Placeholder timeline created"
        )
        plan.add_step(step_tl)
        
    async def _plan_generic(self, plan: Plan, request: str, context: Any):
        """Generic planning for unrecognized requests"""
        # Break down into potential actions
        # This is where more sophisticated NLP would help
        step = PlanStep(
            step_type=StepType.DOCUMENTATION,
            action="lookup_command",
            parameters={'query': request},
            expected_outcome="Found relevant commands"
        )
        plan.add_step(step)