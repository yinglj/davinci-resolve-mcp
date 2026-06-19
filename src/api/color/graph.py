#!/usr/bin/env python3
"""
DaVinci Resolve Node Graph Operations
Node graph operations for timeline, timeline item, or color group
"""

import logging
import os
from typing import Dict, Any, Optional

logger = logging.getLogger("davinci-resolve-mcp.color.graph")


def _get_graph_source(resolve, source: str = "timeline", **kwargs):
    """Get the appropriate graph object based on source type.

    Args:
        resolve: DaVinci Resolve connection
        source: "timeline", "item", "color_group_pre", or "color_group_post"
        **kwargs: Additional parameters for specific source types

    Returns:
        Tuple of (graph_object, description) or (None, error_dict)
    """
    if resolve is None:
        return None, {"error": "Not connected to DaVinci Resolve"}

    project_manager = resolve.GetProjectManager()
    if not project_manager:
        return None, {"error": "Failed to get Project Manager"}

    current_project = project_manager.GetCurrentProject()
    if not current_project:
        return None, {"error": "No project currently open"}

    if source == "timeline":
        timeline = current_project.GetCurrentTimeline()
        if not timeline:
            return None, {"error": "No timeline currently active"}
        graph = timeline.GetNodeGraph()
        return graph, f"timeline"

    elif source in ("color_group_pre", "color_group_post"):
        group_name = kwargs.get("group_name")
        if not group_name:
            return None, {"error": "group_name is required for color group source"}

        groups = current_project.GetColorGroupsList()
        if not groups:
            return None, {"error": f"Color group '{group_name}' not found"}

        target = None
        for group in groups:
            if group.GetName() == group_name:
                target = group
                break

        if not target:
            return None, {"error": f"Color group '{group_name}' not found"}

        if source == "color_group_pre":
            graph = target.GetPreClipNodeGraph()
        else:
            graph = target.GetPostClipNodeGraph()

        return graph, f"color_group:{group_name}:{source}"

    elif source == "item":
        track_type = kwargs.get("track_type", "video")
        track_index = kwargs.get("track_index", 1)
        item_index = kwargs.get("item_index", 0)

        timeline = current_project.GetCurrentTimeline()
        if not timeline:
            return None, {"error": "No timeline currently active"}

        items = timeline.GetItemListInTrack(track_type, track_index) or []
        if item_index < 0 or item_index >= len(items):
            return None, {"error": f"Item index {item_index} out of range"}

        item = items[item_index]
        layer_index = kwargs.get("layer_index")
        if layer_index is not None:
            graph = item.GetNodeGraph(layer_index)
        else:
            graph = item.GetNodeGraph()

        return graph, f"item:{track_type}:{track_index}:{item_index}"

    return None, {"error": f"Unknown source type: {source}"}


def graph_get_num_nodes(resolve, source: str = "timeline", **kwargs) -> Dict[str, Any]:
    """Get the number of nodes in a graph.

    Args:
        resolve: DaVinci Resolve connection
        source: "timeline" (default), "item", "color_group_pre", "color_group_post"

    Returns:
        Dict with 'count' key or 'error' key.
    """
    graph, result = _get_graph_source(resolve, source, **kwargs)
    if graph is None:
        return result

    try:
        count = graph.GetNumNodes()
        return {"count": count}
    except Exception as e:
        return {"error": f"Error getting node count: {str(e)}"}


def graph_get_lut(resolve, node_index: int, source: str = "timeline", **kwargs) -> Dict[str, Any]:
    """Get the LUT applied to a specific node.

    Args:
        resolve: DaVinci Resolve connection
        node_index: 1-based node index
        source: "timeline" (default), "item", "color_group_pre", "color_group_post"

    Returns:
        Dict with 'lut' key or 'error' key.
    """
    graph, result = _get_graph_source(resolve, source, **kwargs)
    if graph is None:
        return result

    try:
        lut = graph.GetLUT(node_index)
        return {"lut": lut if lut else ""}
    except Exception as e:
        return {"error": f"Error getting LUT: {str(e)}"}


def graph_set_lut(resolve, node_index: int, lut_path: str, source: str = "timeline", **kwargs) -> Dict[str, Any]:
    """Set a LUT on a specific node.

    Args:
        resolve: DaVinci Resolve connection
        node_index: 1-based node index
        lut_path: Full path to the LUT file
        source: "timeline" (default), "item", "color_group_pre", "color_group_post"

    Returns:
        Dict with 'success' key.
    """
    if resolve is None:
        return {"success": False, "error": "Not connected to DaVinci Resolve"}

    if not lut_path:
        return {"success": False, "error": "LUT path cannot be empty"}

    if not os.path.exists(lut_path):
        return {"success": False, "error": f"LUT file '{lut_path}' does not exist"}

    graph, result = _get_graph_source(resolve, source, **kwargs)
    if graph is None:
        return {"success": False, **result}

    try:
        result_val = graph.SetLUT(node_index, lut_path)
        return {"success": bool(result_val)}
    except Exception as e:
        return {"success": False, "error": f"Error setting LUT: {str(e)}"}


def graph_get_node_cache(resolve, node_index: int, source: str = "timeline", **kwargs) -> Dict[str, Any]:
    """Get the cache setting for a node.

    Args:
        resolve: DaVinci Resolve connection
        node_index: 1-based node index
        source: "timeline" (default), "item", "color_group_pre", "color_group_post"

    Returns:
        Dict with 'cache' key or 'error' key.
    """
    graph, result = _get_graph_source(resolve, source, **kwargs)
    if graph is None:
        return result

    try:
        cache = graph.GetNodeCache(node_index)
        return {"cache": cache}
    except Exception as e:
        return {"error": f"Error getting node cache: {str(e)}"}


def graph_set_node_cache(resolve, node_index: int, cache_value: int, source: str = "timeline", **kwargs) -> Dict[str, Any]:
    """Set the cache setting for a node.

    Args:
        resolve: DaVinci Resolve connection
        node_index: 1-based node index
        cache_value: Cache value to set
        source: "timeline" (default), "item", "color_group_pre", "color_group_post"

    Returns:
        Dict with 'success' key.
    """
    graph, result = _get_graph_source(resolve, source, **kwargs)
    if graph is None:
        return {"success": False, **result}

    try:
        result_val = graph.SetNodeCache(node_index, cache_value)
        return {"success": bool(result_val)}
    except Exception as e:
        return {"success": False, "error": f"Error setting node cache: {str(e)}"}


def graph_get_node_label(resolve, node_index: int, source: str = "timeline", **kwargs) -> Dict[str, Any]:
    """Get the label of a node.

    Args:
        resolve: DaVinci Resolve connection
        node_index: 1-based node index
        source: "timeline" (default), "item", "color_group_pre", "color_group_post"

    Returns:
        Dict with 'label' key or 'error' key.
    """
    graph, result = _get_graph_source(resolve, source, **kwargs)
    if graph is None:
        return result

    try:
        label = graph.GetNodeLabel(node_index)
        return {"label": label if label else ""}
    except Exception as e:
        return {"error": f"Error getting node label: {str(e)}"}


def graph_get_tools_in_node(resolve, node_index: int, source: str = "timeline", **kwargs) -> Dict[str, Any]:
    """Get the tools used in a specific node.

    Args:
        resolve: DaVinci Resolve connection
        node_index: 1-based node index
        source: "timeline" (default), "item", "color_group_pre", "color_group_post"

    Returns:
        Dict with 'tools' key or 'error' key.
    """
    graph, result = _get_graph_source(resolve, source, **kwargs)
    if graph is None:
        return result

    try:
        tools = graph.GetToolsInNode(node_index)
        return {"tools": tools if tools else []}
    except Exception as e:
        return {"error": f"Error getting tools in node: {str(e)}"}


def graph_set_node_enabled(resolve, node_index: int, enabled: bool, source: str = "timeline", **kwargs) -> Dict[str, Any]:
    """Enable or disable a node.

    Args:
        resolve: DaVinci Resolve connection
        node_index: 1-based node index
        enabled: True to enable, False to disable
        source: "timeline" (default), "item", "color_group_pre", "color_group_post"

    Returns:
        Dict with 'success' key.
    """
    graph, result = _get_graph_source(resolve, source, **kwargs)
    if graph is None:
        return {"success": False, **result}

    try:
        result_val = graph.SetNodeEnabled(node_index, enabled)
        return {"success": bool(result_val)}
    except Exception as e:
        return {"success": False, "error": f"Error setting node enabled state: {str(e)}"}


def graph_apply_grade_from_drx(resolve, path: str, grade_mode: int = 0, source: str = "timeline", **kwargs) -> Dict[str, Any]:
    """Apply a grade from a DRX file.

    Args:
        resolve: DaVinci Resolve connection
        path: Full path to the .drx file
        grade_mode: 0="No keyframes" (default), 1="Source Timecode aligned", 2="Start Frames aligned"
        source: "timeline" (default), "item", "color_group_pre", "color_group_post"

    Returns:
        Dict with 'success' key.
    """
    if resolve is None:
        return {"success": False, "error": "Not connected to DaVinci Resolve"}

    if not path:
        return {"success": False, "error": "DRX path cannot be empty"}

    if not os.path.exists(path):
        return {"success": False, "error": f"DRX file '{path}' does not exist"}

    graph, result = _get_graph_source(resolve, source, **kwargs)
    if graph is None:
        return {"success": False, **result}

    try:
        result_val = graph.ApplyGradeFromDRX(path, grade_mode)
        return {"success": bool(result_val)}
    except Exception as e:
        return {"success": False, "error": f"Error applying grade from DRX: {str(e)}"}


def graph_apply_arri_cdl_lut(resolve, source: str = "timeline", **kwargs) -> Dict[str, Any]:
    """Apply ARRI CDL LUT to the graph.

    Args:
        resolve: DaVinci Resolve connection
        source: "timeline" (default), "item", "color_group_pre", "color_group_post"

    Returns:
        Dict with 'success' key.
    """
    graph, result = _get_graph_source(resolve, source, **kwargs)
    if graph is None:
        return {"success": False, **result}

    try:
        result_val = graph.ApplyArriCdlLut()
        return {"success": bool(result_val)}
    except Exception as e:
        return {"success": False, "error": f"Error applying ARRI CDL LUT: {str(e)}"}


def graph_reset_all_grades(resolve, source: str = "timeline", **kwargs) -> Dict[str, Any]:
    """Reset all grades in the graph.

    Args:
        resolve: DaVinci Resolve connection
        source: "timeline" (default), "item", "color_group_pre", "color_group_post"

    Returns:
        Dict with 'success' key.
    """
    graph, result = _get_graph_source(resolve, source, **kwargs)
    if graph is None:
        return {"success": False, **result}

    try:
        result_val = graph.ResetAllGrades()
        return {"success": bool(result_val)}
    except Exception as e:
        return {"success": False, "error": f"Error resetting all grades: {str(e)}"}