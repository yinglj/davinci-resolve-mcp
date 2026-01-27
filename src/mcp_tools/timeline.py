#!/usr/bin/env python3
"""
DaVinci Resolve MCP Timeline Tools
Timeline operations and marker management
"""

from typing import List, Dict, Any


def register_timeline_tools(mcp, resolve, logger):
    """Register timeline MCP tools."""

    @mcp.tool()
    def create_timeline(name: str) -> str:
        """Create a new empty timeline in the current project.

        Args:
            name: The name for the new timeline.

        Returns:
            str: Success or failure message.
        """
        if resolve is None:
            return "Error: Not connected to DaVinci Resolve"

        if not name:
            return "Error: Timeline name cannot be empty"

        project_manager = resolve.GetProjectManager()
        if not project_manager:
            return "Error: Failed to get Project Manager"

        current_project = project_manager.GetCurrentProject()
        if not current_project:
            return "Error: No project currently open"

        media_pool = current_project.GetMediaPool()
        if not media_pool:
            return "Error: Failed to get Media Pool"

        timeline = media_pool.CreateEmptyTimeline(name)
        if timeline:
            return f"Successfully created timeline '{name}'"
        else:
            return f"Failed to create timeline '{name}'"

    @mcp.tool()
    def create_empty_timeline(
        name: str,
        frame_rate: str = None,
        resolution_width: int = None,
        resolution_height: int = None,
        start_timecode: str = None,
        video_tracks: int = None,
        audio_tracks: int = None,
    ) -> str:
        """Create a new timeline with custom settings.

        Args:
            name: The name for the new timeline.
            frame_rate: The frame rate for the new timeline.
            resolution_width: The resolution width for the new timeline.
            resolution_height: The resolution height for the new timeline.
            start_timecode: The start timecode for the new timeline.
            video_tracks: The number of video tracks for the new timeline.
            audio_tracks: The number of audio tracks for the new timeline.

        Returns:
            str: Success or failure message.
        """
        from src.api.timeline_operations import (
            create_empty_timeline as create_empty_timeline_func,
        )

        return create_empty_timeline_func(
            resolve,
            name,
            frame_rate,
            resolution_width,
            resolution_height,
            start_timecode,
            video_tracks,
            audio_tracks,
        )

    @mcp.tool()
    def delete_timeline(name: str) -> str:
        """Delete a timeline by name.

        Args:
            name: The name of the timeline to delete.

        Returns:
            str: Success or failure message.
        """
        from src.api.timeline_operations import delete_timeline as delete_timeline_func

        return delete_timeline_func(resolve, name)

    @mcp.tool()
    def set_current_timeline(name: str) -> str:
        """Switch the active timeline to the one specified by name.

        Args:
            name: The name of the timeline to activate.

        Returns:
            str: Success or error message.
        """
        if resolve is None:
            return "Error: Not connected to DaVinci Resolve"

        if not name:
            return "Error: Timeline name cannot be empty"

        project_manager = resolve.GetProjectManager()
        if not project_manager:
            return "Error: Failed to get Project Manager"

        current_project = project_manager.GetCurrentProject()
        if not current_project:
            return "Error: No project currently open"

        timeline_count = current_project.GetTimelineCount()
        for i in range(1, timeline_count + 1):
            timeline = current_project.GetTimelineByIndex(i)
            if timeline and timeline.GetName() == name:
                result = current_project.SetCurrentTimeline(timeline)
                if result:
                    return f"Successfully switched to timeline '{name}'"
                else:
                    return f"Failed to switch to timeline '{name}'"

        return f"Error: Timeline '{name}' not found"

    @mcp.tool()
    def add_marker(frame: int = None, color: str = "Blue", note: str = "") -> str:
        """Add a marker at the specified frame in the current timeline.

        Args:
            frame: The frame number to add the marker at.
            color: The color of the marker (e.g., 'Blue', 'Green', 'Red').
            note: A note to add to the marker.

        Returns:
            str: Success or failure message.
        """
        from src.api.timeline_operations import add_marker as add_marker_func

        return add_marker_func(resolve, frame, color, note)

    @mcp.tool()
    def list_timelines_tool() -> List[str]:
        """List all timelines in the current project as a tool."""
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

        return timelines if timelines else ["No timelines found"]

    logger.info("Registered timeline tools")
