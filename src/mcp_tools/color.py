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

    logger.info("Registered color tools")
