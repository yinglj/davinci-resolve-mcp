#!/usr/bin/env python3
"""
DaVinci Resolve Color Page Operations
Re-exports from split submodules for backward compatibility.
"""

# Re-export all functions from submodules
from src.api.color.nodes import (
    get_current_node,
    add_node,
    ensure_clip_selected,
)

from src.api.color.grades import (
    apply_lut,
    copy_grade,
)

from src.api.color.wheels import (
    get_color_wheels,
    set_color_wheel_param,
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
]
