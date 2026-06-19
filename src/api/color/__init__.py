#!/usr/bin/env python3
"""
DaVinci Resolve Color Operations - Split Module
Re-exports all functions from submodules for backward compatibility.
"""

from .nodes import (
    get_current_node,
    add_node,
    ensure_clip_selected,
)

from .grades import (
    apply_lut,
    copy_grade,
)

from .wheels import (
    get_color_wheels,
    set_color_wheel_param,
)

from .groups import (
    list_color_groups,
    get_color_group_name,
    set_color_group_name,
    get_color_group_clips,
    get_color_group_pre_clip_graph,
    get_color_group_post_clip_graph,
)

from .graph import (
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

__all__ = [
    # Node operations
    "get_current_node",
    "add_node",
    "ensure_clip_selected",
    # Grade operations
    "apply_lut",
    "copy_grade",
    # Wheel operations
    "get_color_wheels",
    "set_color_wheel_param",
    # Color group operations
    "list_color_groups",
    "get_color_group_name",
    "set_color_group_name",
    "get_color_group_clips",
    "get_color_group_pre_clip_graph",
    "get_color_group_post_clip_graph",
    # Graph operations
    "graph_get_num_nodes",
    "graph_get_lut",
    "graph_set_lut",
    "graph_get_node_cache",
    "graph_set_node_cache",
    "graph_get_node_label",
    "graph_get_tools_in_node",
    "graph_set_node_enabled",
    "graph_apply_grade_from_drx",
    "graph_apply_arri_cdl_lut",
    "graph_reset_all_grades",
]
