#!/usr/bin/env python3
"""
DaVinci Resolve Color Group Operations
Color group management and node graph access
"""

import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger("davinci-resolve-mcp.color.groups")


def list_color_groups(resolve) -> Dict[str, Any]:
    """List all color groups in the current project.

    Returns:
        Dict with 'groups' key containing list of color group info.
    """
    if resolve is None:
        return {"error": "Not connected to DaVinci Resolve"}

    project_manager = resolve.GetProjectManager()
    if not project_manager:
        return {"error": "Failed to get Project Manager"}

    current_project = project_manager.GetCurrentProject()
    if not current_project:
        return {"error": "No project currently open"}

    try:
        groups = current_project.GetColorGroupsList()
        if not groups:
            return {"groups": []}

        result = []
        for group in groups:
            try:
                result.append({
                    "name": group.GetName(),
                })
            except Exception as e:
                logger.warning(f"Could not get color group info: {e}")

        return {"groups": result}
    except Exception as e:
        return {"error": f"Error listing color groups: {str(e)}"}


def get_color_group_name(resolve, group_name: str) -> Dict[str, Any]:
    """Get the name of a color group.

    Args:
        resolve: DaVinci Resolve connection
        group_name: Name of the color group to look up

    Returns:
        Dict with 'name' key or 'error' key.
    """
    if resolve is None:
        return {"error": "Not connected to DaVinci Resolve"}

    project_manager = resolve.GetProjectManager()
    if not project_manager:
        return {"error": "Failed to get Project Manager"}

    current_project = project_manager.GetCurrentProject()
    if not current_project:
        return {"error": "No project currently open"}

    try:
        groups = current_project.GetColorGroupsList()
        if not groups:
            return {"error": f"Color group '{group_name}' not found"}

        for group in groups:
            if group.GetName() == group_name:
                return {"name": group.GetName()}

        return {"error": f"Color group '{group_name}' not found"}
    except Exception as e:
        return {"error": f"Error getting color group: {str(e)}"}


def set_color_group_name(resolve, group_name: str, new_name: str) -> Dict[str, Any]:
    """Rename a color group.

    Args:
        resolve: DaVinci Resolve connection
        group_name: Current name of the color group
        new_name: New name for the color group

    Returns:
        Dict with 'success' key.
    """
    if resolve is None:
        return {"error": "Not connected to DaVinci Resolve"}

    project_manager = resolve.GetProjectManager()
    if not project_manager:
        return {"error": "Failed to get Project Manager"}

    current_project = project_manager.GetCurrentProject()
    if not current_project:
        return {"error": "No project currently open"}

    try:
        groups = current_project.GetColorGroupsList()
        if not groups:
            return {"success": False, "error": f"Color group '{group_name}' not found"}

        target = None
        for group in groups:
            if group.GetName() == group_name:
                target = group
                break

        if not target:
            return {"success": False, "error": f"Color group '{group_name}' not found"}

        result = target.SetName(new_name)
        return {"success": bool(result)}
    except Exception as e:
        return {"success": False, "error": f"Error renaming color group: {str(e)}"}


def get_color_group_clips(resolve, group_name: str) -> Dict[str, Any]:
    """Get all clips assigned to a color group.

    Args:
        resolve: DaVinci Resolve connection
        group_name: Name of the color group

    Returns:
        Dict with 'clips' key containing list of clip names, or 'error' key.
    """
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

    try:
        groups = current_project.GetColorGroupsList()
        if not groups:
            return {"clips": [], "error": f"Color group '{group_name}' not found"}

        target = None
        for group in groups:
            if group.GetName() == group_name:
                target = group
                break

        if not target:
            return {"clips": [], "error": f"Color group '{group_name}' not found"}

        clips = []
        video_track_count = current_timeline.GetTrackCount("video")
        for track_index in range(1, video_track_count + 1):
            track_items = current_timeline.GetItemListInTrack("video", track_index)
            if track_items:
                for item in track_items:
                    try:
                        item_group = item.GetColorGroup()
                        if item_group and item_group.GetName() == group_name:
                            clips.append(item.GetName())
                    except Exception:
                        pass

        return {"clips": clips}
    except Exception as e:
        return {"clips": [], "error": f"Error getting color group clips: {str(e)}"}


def get_color_group_pre_clip_graph(resolve, group_name: str) -> Dict[str, Any]:
    """Get the pre-clip node graph for a color group.

    Args:
        resolve: DaVinci Resolve connection
        group_name: Name of the color group

    Returns:
        Dict with 'available' and 'num_nodes' keys, or 'error' key.
    """
    if resolve is None:
        return {"error": "Not connected to DaVinci Resolve"}

    project_manager = resolve.GetProjectManager()
    if not project_manager:
        return {"error": "Failed to get Project Manager"}

    current_project = project_manager.GetCurrentProject()
    if not current_project:
        return {"error": "No project currently open"}

    try:
        groups = current_project.GetColorGroupsList()
        if not groups:
            return {"available": False, "num_nodes": 0, "error": f"Color group '{group_name}' not found"}

        target = None
        for group in groups:
            if group.GetName() == group_name:
                target = group
                break

        if not target:
            return {"available": False, "num_nodes": 0, "error": f"Color group '{group_name}' not found"}

        graph = target.GetPreClipNodeGraph()
        if graph:
            num_nodes = graph.GetNumNodes()
            return {"available": True, "num_nodes": num_nodes}
        return {"available": False, "num_nodes": 0}
    except Exception as e:
        return {"available": False, "num_nodes": 0, "error": f"Error getting pre-clip graph: {str(e)}"}


def get_color_group_post_clip_graph(resolve, group_name: str) -> Dict[str, Any]:
    """Get the post-clip node graph for a color group.

    Args:
        resolve: DaVinci Resolve connection
        group_name: Name of the color group

    Returns:
        Dict with 'available' and 'num_nodes' keys, or 'error' key.
    """
    if resolve is None:
        return {"error": "Not connected to DaVinci Resolve"}

    project_manager = resolve.GetProjectManager()
    if not project_manager:
        return {"error": "Failed to get Project Manager"}

    current_project = project_manager.GetCurrentProject()
    if not current_project:
        return {"error": "No project currently open"}

    try:
        groups = current_project.GetColorGroupsList()
        if not groups:
            return {"available": False, "num_nodes": 0, "error": f"Color group '{group_name}' not found"}

        target = None
        for group in groups:
            if group.GetName() == group_name:
                target = group
                break

        if not target:
            return {"available": False, "num_nodes": 0, "error": f"Color group '{group_name}' not found"}

        graph = target.GetPostClipNodeGraph()
        if graph:
            num_nodes = graph.GetNumNodes()
            return {"available": True, "num_nodes": num_nodes}
        return {"available": False, "num_nodes": 0}
    except Exception as e:
        return {"available": False, "num_nodes": 0, "error": f"Error getting post-clip graph: {str(e)}"}