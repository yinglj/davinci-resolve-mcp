#!/usr/bin/env python3
"""
DaVinci Resolve MCP Timeline Item Property Tools
Getting timeline item properties
"""

from typing import List, Dict, Any


def find_timeline_item(
    timeline, timeline_item_id, search_video=True, search_audio=True
):
    """Find a timeline item by ID across video and audio tracks."""
    if search_video:
        video_track_count = timeline.GetTrackCount("video")
        for track_index in range(1, video_track_count + 1):
            items = timeline.GetItemListInTrack("video", track_index)
            if items:
                for item in items:
                    if str(item.GetUniqueId()) == timeline_item_id:
                        return item, "video"

    if search_audio:
        audio_track_count = timeline.GetTrackCount("audio")
        for track_index in range(1, audio_track_count + 1):
            items = timeline.GetItemListInTrack("audio", track_index)
            if items:
                for item in items:
                    if str(item.GetUniqueId()) == timeline_item_id:
                        return item, "audio"

    return None, None


def register_timeline_item_property_tools(mcp, resolve, logger):
    """Register timeline item property MCP tools."""
    # All resources moved to mcp_resources/timeline_items.py
    pass

    logger.info("Registered timeline item property tools")
