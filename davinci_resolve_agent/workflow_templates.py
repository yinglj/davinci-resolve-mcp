# davinci_resolve_agent/workflow_templates.py
"""
Predefined workflow templates for common video editing scenarios.
Each template defines a sequence of tasks that can be executed by the agent delegation framework.
"""

from typing import Dict, List, Any, Optional
from logger import logger


class WorkflowTemplate:
    """Represents a predefined workflow template."""

    def __init__(
        self,
        name: str,
        description: str,
        tasks: List[Dict[str, Any]],
        estimated_duration: str = "",
    ):
        self.name = name
        self.description = description
        self.tasks = tasks
        self.estimated_duration = estimated_duration

    def get_tasks(self, **kwargs) -> List[Dict[str, Any]]:
        """Get tasks with parameters substituted."""
        tasks = []
        for task in self.tasks:
            task_copy = task.copy()
            # Substitute parameters in task descriptions
            for key, value in kwargs.items():
                if "task" in task_copy and isinstance(task_copy["task"], str):
                    task_copy["task"] = task_copy["task"].format(**kwargs)
                if "context" in task_copy and isinstance(task_copy["context"], dict):
                    for ctx_key, ctx_value in task_copy["context"].items():
                        if isinstance(ctx_value, str):
                            task_copy["context"][ctx_key] = ctx_value.format(**kwargs)
            tasks.append(task_copy)
        return tasks


class WorkflowManager:
    """Manages workflow templates and custom workflows."""

    def __init__(self):
        self.templates = {}
        self._initialize_templates()

    def _initialize_templates(self):
        """Initialize predefined workflow templates."""

        # 1. Quick Edit + Color + Music
        quick_edit_template = WorkflowTemplate(
            name="quick_edit_color_music",
            description="快速剪辑 + 自动调色 + 背景音乐添加",
            estimated_duration="10-15分钟",
            tasks=[
                {
                    "role": "editor",
                    "task": "Analyze footage and create quick cuts at {duration} seconds",
                    "context": {
                        "style": "fast-paced",
                        "target_duration": "{duration}",
                        "music_beat": "{bpm} BPM",
                    },
                },
                {
                    "role": "colorist",
                    "task": "Apply automatic color grading with {style} look",
                    "context": {
                        "style": "{color_style}",
                        "auto_match": True,
                        "intensity": "medium",
                    },
                },
                {
                    "role": "sound_engineer",
                    "task": "Add background music and normalize audio levels",
                    "context": {
                        "music_style": "{music_style}",
                        "target_loudness": "-23 LUFS",
                        "normalize_audio": True,
                    },
                },
            ],
        )

        # 2. Promotional Video Creator
        promo_template = WorkflowTemplate(
            name="promo_video_creator",
            description="创建专业的宣传视频：剪辑 + 特效 + 配音 + 导出",
            estimated_duration="20-30分钟",
            tasks=[
                {
                    "role": "editor",
                    "task": "Create engaging cuts with transitions for {duration} second promotional video",
                    "context": {
                        "target_duration": "{duration}",
                        "style": "promotional",
                        "add_transitions": True,
                        "effects": ["dynamic_transitions", "text_overlays"],
                    },
                },
                {
                    "role": "colorist",
                    "task": "Apply cinematic color grading and enhance visual appeal",
                    "context": {
                        "style": "cinematic",
                        "enhance_contrast": True,
                        "add_vignette": True,
                    },
                },
                {
                    "role": "sound_engineer",
                    "task": "Generate voiceover narration and add background music",
                    "context": {
                        "voiceover_text": "{voiceover_text}",
                        "voice": "professional",
                        "music_style": "uplifting",
                        "fade_in_out": True,
                    },
                },
                {
                    "role": "editor",
                    "task": "Add final effects and prepare for export",
                    "context": {
                        "add_logo": True,
                        "add_call_to_action": True,
                        "optimize_for_platform": "{platform}",
                    },
                },
            ],
        )

        # 3. Social Media Content Factory
        social_template = WorkflowTemplate(
            name="social_media_factory",
            description="批量处理社交媒体内容：多格式剪辑 + 统一风格 + 自动发布",
            estimated_duration="15-25分钟",
            tasks=[
                {
                    "role": "editor",
                    "task": "Create multiple format versions (TikTok, Instagram, YouTube) from source footage",
                    "context": {
                        "formats": ["9:16", "1:1", "16:9"],
                        "platforms": ["tiktok", "instagram", "youtube"],
                        "max_duration": "{max_duration}",
                        "add_text_overlays": True,
                    },
                },
                {
                    "role": "colorist",
                    "task": "Apply consistent color grading across all versions",
                    "context": {
                        "style": "modern_social",
                        "consistent_look": True,
                        "enhance_saturation": True,
                    },
                },
                {
                    "role": "sound_engineer",
                    "task": "Add trending music and sound effects",
                    "context": {
                        "music_trending": True,
                        "add_sound_effects": True,
                        "normalize_for_social": True,
                    },
                },
            ],
        )

        # 4. Tutorial Video Assembly
        tutorial_template = WorkflowTemplate(
            name="tutorial_video_assembly",
            description="教程视频制作：屏幕录制同步 + 字幕 + 章节标记",
            estimated_duration="12-18分钟",
            tasks=[
                {
                    "role": "editor",
                    "task": "Sync voiceover with screen recording and create smooth cuts",
                    "context": {
                        "sync_audio_video": True,
                        "add_zoom_effects": True,
                        "highlight_actions": True,
                    },
                },
                {
                    "role": "sound_engineer",
                    "task": "Add background music and normalize voiceover levels",
                    "context": {
                        "voiceover_enhancement": True,
                        "background_music": "educational",
                        "add_fade_out": True,
                    },
                },
                {
                    "role": "editor",
                    "task": "Generate automatic captions and chapter markers",
                    "context": {
                        "generate_captions": True,
                        "add_chapters": True,
                        "chapter_detection": "topic_change",
                        "caption_style": "modern",
                    },
                },
                {
                    "role": "colorist",
                    "task": "Enhance readability and visual clarity",
                    "context": {
                        "improve_contrast": True,
                        "enhance_text_visibility": True,
                        "subtle_background_effects": True,
                    },
                },
            ],
        )

        # 5. Live Event Highlights
        highlights_template = WorkflowTemplate(
            name="live_event_highlights",
            description="直播活动精彩片段：智能检测 + 快速剪辑 + 动态转场",
            estimated_duration="18-25分钟",
            tasks=[
                {
                    "role": "editor",
                    "task": "Detect highlight moments and create fast-paced montage",
                    "context": {
                        "auto_detect_highlights": True,
                        "energy_analysis": True,
                        "fast_cut_style": True,
                        "target_duration": "{duration}",
                    },
                },
                {
                    "role": "colorist",
                    "task": "Apply dynamic color grading with energy-based effects",
                    "context": {
                        "dynamic_grading": True,
                        "energy_based_effects": True,
                        "enhance_colors": True,
                    },
                },
                {
                    "role": "sound_engineer",
                    "task": "Enhance crowd reactions and add impactful sound design",
                    "context": {
                        "enhance_crowd_audio": True,
                        "add_impact_sounds": True,
                        "normalize_levels": True,
                        "add_reverb": "arena",
                    },
                },
                {
                    "role": "editor",
                    "task": "Add lower thirds, graphics, and final polish",
                    "context": {
                        "add_lower_thirds": True,
                        "add_event_graphics": True,
                        "final_color_correction": True,
                    },
                },
            ],
        )

        # Register all templates
        self.templates = {
            "quick_edit": quick_edit_template,
            "promo_video": promo_template,
            "social_media": social_template,
            "tutorial": tutorial_template,
            "highlights": highlights_template,
        }

        logger.info(f"Initialized {len(self.templates)} workflow templates")

    def get_template(self, template_name: str) -> Optional[WorkflowTemplate]:
        """Get a workflow template by name."""
        return self.templates.get(template_name)

    def get_available_templates(self) -> Dict[str, Dict[str, str]]:
        """Get list of available templates with descriptions."""
        return {
            name: {
                "description": template.description,
                "estimated_duration": template.estimated_duration,
            }
            for name, template in self.templates.items()
        }

    def create_custom_workflow(
        self,
        name: str,
        description: str,
        tasks: List[Dict[str, Any]],
        estimated_duration: str = "",
    ) -> WorkflowTemplate:
        """Create a custom workflow template."""
        template = WorkflowTemplate(name, description, tasks, estimated_duration)
        self.templates[name] = template
        logger.info(f"Created custom workflow template: {name}")
        return template

    async def execute_workflow(
        self, template_name: str, agent_delegator, **kwargs
    ) -> Dict[str, Any]:
        """
        Execute a workflow template using the agent delegator.

        Args:
            template_name: Name of the template to execute
            agent_delegator: AgentDelegator instance
            **kwargs: Parameters to substitute in the template

        Returns:
            Dict containing execution results
        """
        template = self.get_template(template_name)
        if not template:
            return {"success": False, "error": f"Template '{template_name}' not found"}

        try:
            tasks = template.get_tasks(**kwargs)
            logger.info(f"Executing workflow '{template_name}' with {len(tasks)} tasks")

            # Execute tasks using the delegator in sequence
            # Video production tasks are typically sequential (Edit -> Color -> Audio)
            execution_result = await agent_delegator.delegate_sequence(tasks)

            success = execution_result.get("success", False)
            results = execution_result.get("results", [])

            return {
                "success": success,
                "template": template_name,
                "tasks_executed": len(results),
                "total_tasks": len(tasks),
                "results": results,
                "description": template.description,
                "error": execution_result.get("error") if not success else None,
            }

        except Exception as e:
            logger.error(f"Workflow execution failed: {e}")
            return {"success": False, "error": str(e), "template": template_name}


# Global workflow manager instance
workflow_manager = WorkflowManager()


def get_workflow_manager() -> WorkflowManager:
    """Get the global workflow manager instance."""
    return workflow_manager
