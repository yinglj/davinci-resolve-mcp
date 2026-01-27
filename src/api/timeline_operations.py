#!/usr/bin/env python3
"""
DaVinci Resolve Timeline Operations
Re-exports from split submodules for backward compatibility.
"""

# Re-export all functions from submodules
from src.api.timeline.basic import (
    list_timelines,
    get_current_timeline_info,
    create_timeline,
    create_empty_timeline,
    set_current_timeline,
    delete_timeline,
    get_timeline_tracks,
)

from src.api.timeline.markers import (
    add_marker,
)

__all__ = [
    # Basic timeline operations
    "list_timelines",
    "get_current_timeline_info",
    "create_timeline",
    "create_empty_timeline",
    "set_current_timeline",
    "delete_timeline",
    "get_timeline_tracks",
    # Marker operations
    "add_marker",
]
