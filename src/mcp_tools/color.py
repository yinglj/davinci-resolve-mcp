#!/usr/bin/env python3
"""
DaVinci Resolve MCP Color Tools
Color page operations
"""

from typing import Dict, Any, Optional


def register_color_tools(mcp, resolve, logger):
    """Register color page MCP tools."""

    @mcp.tool()
    def apply_lut(lut_path: str, node_index: Optional[int] = None) -> str:
        """Apply a Look-Up Table (LUT) to a specific node in the color page.

        Args:
            lut_path: Full path to the .cube or .3dl LUT file.
            node_index: Index of the target node (None for current node).

        Returns:
            str: Success message or error description.
        """
        from src.api.color import apply_lut as apply_lut_func

        return apply_lut_func(resolve, lut_path, node_index)

    @mcp.tool()
    def set_color_wheel_param(
        wheel: str, param: str, value: float, node_index: Optional[int] = None
    ) -> str:
        """Set a color wheel parameter for a node.

        Args:
            wheel: One of 'lift', 'gamma', 'gain', 'offset'.
            param: Parameter name within the wheel.
            value: New value for the parameter.
            node_index: Index of the target node (None for current node).

        Returns:
            str: Success message or error description.
        """
        from src.api.color import set_color_wheel_param as set_param_func

        return set_param_func(resolve, wheel, param, value, node_index)

    @mcp.tool()
    def add_node(node_type: str = "serial", label: Optional[str] = None) -> str:
        """Add a new node to the current clip's node graph.

        Args:
            node_type: One of 'serial', 'parallel', 'layer', 'outside'.
            label: Optional name label for the node.

        Returns:
            str: Result of the operation.
        """
        from src.api.color import add_node as add_node_func

        return add_node_func(resolve, node_type, label)

    @mcp.tool()
    def copy_grade(
        source_clip_name: Optional[str] = None,
        target_clip_name: Optional[str] = None,
        mode: str = "full",
    ) -> str:
        """Copy a grade from one clip to another in the color page.

        Args:
            source_clip_name: Name of the source clip.
            target_clip_name: Name of the target clip.
            mode: Copy mode (full, color, color_and_saturation).

        Returns:
            str: Success message or error description.
        """
        from src.api.color import copy_grade as copy_grade_func

        return copy_grade_func(resolve, source_clip_name, target_clip_name, mode)

    @mcp.tool()
    def color_group(action: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Manage color groups and their node graphs.

        Actions:
          list() -> {groups}
          get_name(group_name) -> {name}
          set_name(group_name, new_name) -> {success}
          get_clips(group_name) -> {clips}
          get_pre_clip_graph(group_name) -> {available, num_nodes}
          get_post_clip_graph(group_name) -> {available, num_nodes}
        """
        from src.api.color import (
            list_color_groups,
            get_color_group_name,
            set_color_group_name,
            get_color_group_clips,
            get_color_group_pre_clip_graph,
            get_color_group_post_clip_graph,
        )

        if resolve is None:
            return {"error": "Not connected to DaVinci Resolve"}

        p = params or {}
        action_lower = action.lower()

        if action_lower == "list":
            return list_color_groups(resolve)
        elif action_lower == "get_name":
            group_name = p.get("group_name")
            if not group_name:
                return {"error": "group_name is required"}
            return get_color_group_name(resolve, group_name)
        elif action_lower == "set_name":
            group_name = p.get("group_name")
            new_name = p.get("new_name")
            if not group_name or not new_name:
                return {"error": "group_name and new_name are required"}
            return set_color_group_name(resolve, group_name, new_name)
        elif action_lower == "get_clips":
            group_name = p.get("group_name")
            if not group_name:
                return {"error": "group_name is required"}
            return get_color_group_clips(resolve, group_name)
        elif action_lower == "get_pre_clip_graph":
            group_name = p.get("group_name")
            if not group_name:
                return {"error": "group_name is required"}
            return get_color_group_pre_clip_graph(resolve, group_name)
        elif action_lower == "get_post_clip_graph":
            group_name = p.get("group_name")
            if not group_name:
                return {"error": "group_name is required"}
            return get_color_group_post_clip_graph(resolve, group_name)
        else:
            valid = ["list", "get_name", "set_name", "get_clips", "get_pre_clip_graph", "get_post_clip_graph"]
            return {"error": f"Unknown action '{action}'. Valid actions: {', '.join(valid)}"}

    @mcp.tool()
    def graph(action: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Node graph operations (color grading nodes). Source can be timeline, timeline item, or color group.

        Actions:
          get_num_nodes(source?, ...) -> {count}
          get_lut(node_index, source?, ...) -> {lut}
          set_lut(node_index, lut_path, source?, ...) -> {success}
          get_node_cache(node_index, source?, ...) -> {cache}
          set_node_cache(node_index, cache_value, source?, ...) -> {success}
          get_node_label(node_index, source?, ...) -> {label}
          get_tools_in_node(node_index, source?, ...) -> {tools}
          set_node_enabled(node_index, enabled, source?, ...) -> {success}
          apply_grade_from_drx(path, grade_mode?, source?, ...) -> {success}
          apply_arri_cdl_lut(source?, ...) -> {success}
          reset_all_grades(source?, ...) -> {success}

        Source types:
          "timeline" (default) - current timeline's node graph
          "item" (needs track_type, track_index, item_index) - specific timeline item
          "color_group_pre" (needs group_name) - pre-clip graph of a color group
          "color_group_post" (needs group_name) - post-clip graph of a color group
        """
        from src.api.color import (
            graph_get_num_nodes,
            graph_get_lut,
            graph_set_lut,
            graph_get_node_cache,
            graph_set_node_cache,
            graph_get_node_label,
            graph_get_tools_in_node,
            graph_set_node_enabled,
            graph_apply_grade_from_drx,
            graph_apply_arri_cdl_lut,
            graph_reset_all_grades,
        )

        if resolve is None:
            return {"error": "Not connected to DaVinci Resolve"}

        p = params or {}
        action_lower = action.lower()

        # Build common kwargs
        source = p.get("source", "timeline")
        kwargs = {}
        if source == "item":
            kwargs["track_type"] = p.get("track_type", "video")
            kwargs["track_index"] = p.get("track_index", 1)
            kwargs["item_index"] = p.get("item_index", 0)
            kwargs["layer_index"] = p.get("layer_index")
        elif source in ("color_group_pre", "color_group_post"):
            kwargs["group_name"] = p.get("group_name")

        if action_lower == "get_num_nodes":
            return graph_get_num_nodes(resolve, source, **kwargs)
        elif action_lower == "get_lut":
            node_index = p.get("node_index")
            if node_index is None:
                return {"error": "node_index is required"}
            return graph_get_lut(resolve, node_index, source, **kwargs)
        elif action_lower == "set_lut":
            node_index = p.get("node_index")
            lut_path = p.get("lut_path")
            if node_index is None:
                return {"success": False, "error": "node_index is required"}
            if not lut_path:
                return {"success": False, "error": "lut_path is required"}
            return graph_set_lut(resolve, node_index, lut_path, source, **kwargs)
        elif action_lower == "get_node_cache":
            node_index = p.get("node_index")
            if node_index is None:
                return {"error": "node_index is required"}
            return graph_get_node_cache(resolve, node_index, source, **kwargs)
        elif action_lower == "set_node_cache":
            node_index = p.get("node_index")
            cache_value = p.get("cache_value")
            if node_index is None:
                return {"success": False, "error": "node_index is required"}
            if cache_value is None:
                return {"success": False, "error": "cache_value is required"}
            return graph_set_node_cache(resolve, node_index, cache_value, source, **kwargs)
        elif action_lower == "get_node_label":
            node_index = p.get("node_index")
            if node_index is None:
                return {"error": "node_index is required"}
            return graph_get_node_label(resolve, node_index, source, **kwargs)
        elif action_lower == "get_tools_in_node":
            node_index = p.get("node_index")
            if node_index is None:
                return {"error": "node_index is required"}
            return graph_get_tools_in_node(resolve, node_index, source, **kwargs)
        elif action_lower == "set_node_enabled":
            node_index = p.get("node_index")
            enabled = p.get("enabled")
            if node_index is None:
                return {"success": False, "error": "node_index is required"}
            if enabled is None:
                return {"success": False, "error": "enabled is required"}
            return graph_set_node_enabled(resolve, node_index, enabled, source, **kwargs)
        elif action_lower == "apply_grade_from_drx":
            path = p.get("path")
            if not path:
                return {"success": False, "error": "path is required"}
            grade_mode = p.get("grade_mode", 0)
            return graph_apply_grade_from_drx(resolve, path, grade_mode, source, **kwargs)
        elif action_lower == "apply_arri_cdl_lut":
            return graph_apply_arri_cdl_lut(resolve, source, **kwargs)
        elif action_lower == "reset_all_grades":
            return graph_reset_all_grades(resolve, source, **kwargs)
        else:
            valid = [
                "get_num_nodes", "get_lut", "set_lut", "get_node_cache", "set_node_cache",
                "get_node_label", "get_tools_in_node", "set_node_enabled",
                "apply_grade_from_drx", "apply_arri_cdl_lut", "reset_all_grades"
            ]
            return {"error": f"Unknown action '{action}'. Valid actions: {', '.join(valid)}"}

    logger.info("Registered color tools")
