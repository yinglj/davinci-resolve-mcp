#!/usr/bin/env python3
"""
DaVinci Resolve Fusion Operations
Ported from samuelgursky commit 8ea53b8
"""

from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger("davinci-resolve-mcp.fusion")


def get_item_by_id(resolve, timeline_item_id: str):
    """
    Helper to find a TimelineItem by its unique ID.
    Note: Iterating the whole timeline is expensive.
    """
    pm = resolve.GetProjectManager()
    project = pm.GetCurrentProject()
    timeline = project.GetCurrentTimeline()

    if not timeline:
        return None

    track_count_video = timeline.GetTrackCount("video")

    for i in range(1, track_count_video + 1):
        items = timeline.GetItemListInTrack("video", i)
        if items:
            for item in items:
                try:
                    # In Resolve v19+, TimelineItem has GetUniqueId()
                    uid = item.GetUniqueId()
                    if str(uid) == str(timeline_item_id):
                        return item
                except:
                    pass

                # Fallback to name match for older versions
                if item.GetName() == timeline_item_id:
                    return item
    return None


def set_timeline_item_property(
    resolve, timeline_item_id: str, property_name: str, property_value: Any
) -> Dict[str, Any]:
    """Set a property for a timeline item (transform, crop, composite, etc.)"""
    item = get_item_by_id(resolve, timeline_item_id)
    if not item:
        return {
            "success": False,
            "error": f"Timeline item '{timeline_item_id}' not found",
        }

    try:
        # Resolve API: SetProperty(name, value)
        result = item.SetProperty(property_name, property_value)
        return {
            "success": bool(result),
            "item": item.GetName(),
            "property": property_name,
            "value": property_value,
        }
    except Exception as e:
        logger.error(f"Error setting timeline item property: {e}")
        return {"success": False, "error": str(e)}


def register_tools(proxy):
    """Register Fusion and Timeline Item tools with the proxy."""
    from ..resolve_mcp_server import get_resolve

    def set_transform(timeline_item_id: str, property_name: str, value: float):
        """Set transform property (Pan, Tilt, ZoomX, ZoomY, Rotation)."""
        return set_timeline_item_property(
            get_resolve(), timeline_item_id, property_name, value
        )

    proxy.register_tool(
        "set_timeline_item_transform",
        set_transform,
        "timeline",
        "Set transform property (Pan, Tilt, ZoomX, ZoomY, Rotation) for a specific clip",
        {
            "timeline_item_id": {"type": "string", "description": "Clip ID or Name"},
            "property_name": {
                "type": "string",
                "description": "Property name (e.g., 'Pan', 'ZoomX')",
            },
            "value": {"type": "number", "description": "New value"},
        },
    )
    return 1
