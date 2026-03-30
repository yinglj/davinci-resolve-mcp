#!/usr/bin/env python3
"""
DaVinci Resolve MCP Resources - Media related resources
"""

import json
from typing import List, Dict, Any

from fastmcp.resources import ResourceContent, ResourceResult


def register_media_resources(mcp, resolve, logger):
    """Register media-related resources."""

    def to_resource_result(payload: Any) -> ResourceResult:
        if isinstance(payload, list):
            return ResourceResult([ResourceContent(item) for item in payload])
        return ResourceResult([ResourceContent(payload)])

    def to_json_text_result(payload: Any) -> ResourceResult:
        return ResourceResult([ResourceContent(json.dumps(payload, ensure_ascii=False))])

    def safe_invoke(obj: Any, method_name: str, *args: Any) -> Any:
        method = getattr(obj, method_name, None)
        if not callable(method):
            return None
        try:
            return method(*args)
        except Exception:
            return None

    def safe_clip_duration(clip: Any) -> Any:
        # Resolve bridge may expose GetDuration as None/non-callable for some clips.
        duration = safe_invoke(clip, "GetDuration")
        if duration is not None:
            return duration

        clip_prop = safe_invoke(clip, "GetClipProperty", "Duration")
        if clip_prop in (None, ""):
            clip_prop = safe_invoke(clip, "GetClipProperty", "Frames")
        return clip_prop if clip_prop not in (None, "") else 0

    @mcp.resource("resolve://media-pool-clips")
    def list_media_pool_clips() -> ResourceResult:
        """List all clips in the root folder of the media pool."""
        try:
            from src.api.media import list_media_pool_clips as list_media_pool_clips_func
        except ImportError:
            return to_json_text_result([])

        clips = list_media_pool_clips_func(resolve)
        if not clips:
            return to_json_text_result([])
        if isinstance(clips, list) and len(clips) > 0 and isinstance(clips[0], dict) and "error" in clips[0]:
            return to_json_text_result([])

        result = []
        for clip in clips:
            name = str(clip.get("name", "Unknown Clip")) if isinstance(clip, dict) else "Unknown Clip"
            duration = clip.get("duration", 0) if isinstance(clip, dict) else 0
            fps = clip.get("fps", "Unknown") if isinstance(clip, dict) else "Unknown"
            result.append(
                {
                    "name": name,
                    "clip_name": name,
                    "clipName": name,
                    "duration": duration,
                    "fps": fps,
                }
            )

        return to_json_text_result(result)

    @mcp.resource("resolve://media-pool-bins")
    def list_media_pool_bins() -> ResourceResult:
        """List all bins/folders in the media pool."""
        try:
            from src.api.media import list_bins as list_bins_func
        except ImportError:
            return to_resource_result({"error": "Could not import media operations"})

        return to_resource_result(list_bins_func(resolve))

    @mcp.resource("resolve://media-pool-bin/{bin_name}")
    def get_media_pool_bin_contents(bin_name: str) -> ResourceResult:
        """Get contents of a specific bin/folder in the media pool."""
        try:
            from src.api.media import (
                get_bin_contents as get_bin_contents_func,
            )
        except ImportError:
            return to_resource_result({"error": "Could not import media operations"})

        return to_resource_result(get_bin_contents_func(resolve, bin_name))

    @mcp.resource("resolve://timeline-clips")
    def list_timeline_clips() -> ResourceResult:
        """List all clips in the current timeline."""
        if resolve is None:
            return to_resource_result({"error": "Not connected to DaVinci Resolve"})

        project_manager = resolve.GetProjectManager()
        if not project_manager:
            return to_resource_result({"error": "Failed to get Project Manager"})

        current_project = project_manager.GetCurrentProject()
        if not current_project:
            return to_resource_result({"error": "No project currently open"})

        current_timeline = current_project.GetCurrentTimeline()
        if not current_timeline:
            return to_resource_result({"error": "No timeline currently active"})

        try:
            video_track_count = current_timeline.GetTrackCount("video")
            audio_track_count = current_timeline.GetTrackCount("audio")

            clips = []

            for track_index in range(1, video_track_count + 1):
                track_items = current_timeline.GetItemListInTrack("video", track_index)
                if track_items:
                    for item in track_items:
                        clips.append(
                            {
                                "name": item.GetName(),
                                "type": "video",
                                "track": track_index,
                                "start_frame": item.GetStart(),
                                "end_frame": item.GetEnd(),
                                "duration": item.GetDuration(),
                            }
                        )

            for track_index in range(1, audio_track_count + 1):
                track_items = current_timeline.GetItemListInTrack("audio", track_index)
                if track_items:
                    for item in track_items:
                        clips.append(
                            {
                                "name": item.GetName(),
                                "type": "audio",
                                "track": track_index,
                                "start_frame": item.GetStart(),
                                "end_frame": item.GetEnd(),
                                "duration": item.GetDuration(),
                            }
                        )

            if not clips:
                return to_resource_result({"info": "No clips found in the current timeline"})

            return to_resource_result(clips)
        except Exception as e:
            return to_resource_result({"error": f"Error listing timeline clips: {str(e)}"})

    logger.info("Media resources registered")
