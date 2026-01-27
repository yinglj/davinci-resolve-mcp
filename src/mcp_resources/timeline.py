#!/usr/bin/env python3
"""
DaVinci Resolve MCP Resources - Timeline related resources
"""

from typing import List, Dict, Any


def register_timeline_resources(mcp, resolve, logger):
    """Register timeline-related resources."""

    @mcp.resource("resolve://timelines")
    def list_timelines() -> List[str]:
        """List all timelines in the current project."""
        if resolve is None:
            return ["Error: Not connected to DaVinci Resolve"]

        project_manager = resolve.GetProjectManager()
        if not project_manager:
            return ["Error: Failed to get Project Manager"]

        current_project = project_manager.GetCurrentProject()
        if not current_project:
            return ["Error: No project currently open"]

        timeline_count = current_project.GetTimelineCount()
        timelines = []

        for i in range(1, timeline_count + 1):
            timeline = current_project.GetTimelineByIndex(i)
            if timeline:
                timelines.append(timeline.GetName())

        if not timelines:
            return ["No timelines found in the current project"]

        return timelines

    @mcp.resource("resolve://current-timeline")
    def get_current_timeline() -> Dict[str, Any]:
        """Get detailed information about the currently active timeline."""
        if resolve is None:
            return {"error": "Not connected to DaVinci Resolve"}

        project_manager = resolve.GetProjectManager()
        if not project_manager:
            return {"error": "Failed to get Project Manager"}

        current_project = project_manager.GetCurrentProject()
        if not current_project:
            return {"error": "No project currently open"}

        current_timeline = current_project.GetCurrentTimeline()
        if not current_timeline:
            return {"error": "No timeline currently active"}

        result = {
            "name": current_timeline.GetName(),
            "fps": current_timeline.GetSetting("timelineFrameRate"),
            "resolution": {
                "width": current_timeline.GetSetting("timelineResolutionWidth"),
                "height": current_timeline.GetSetting("timelineResolutionHeight"),
            },
            "duration": current_timeline.GetEndFrame()
            - current_timeline.GetStartFrame()
            + 1,
        }

        return result

    @mcp.resource("resolve://timeline-tracks/{timeline_name}")
    def get_timeline_tracks(timeline_name: str = None) -> Dict[str, Any]:
        """Get the track structure of a timeline."""
        try:
            from src.api.timeline_operations import (
                get_timeline_tracks as get_tracks_func,
            )
        except ImportError:
            # Fallback if needed
            return {"error": "Could not import timeline operations"}

        return get_tracks_func(resolve, timeline_name)

    logger.info("Timeline resources registered")
