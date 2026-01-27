#!/usr/bin/env python3
"""
DaVinci Resolve MCP Resources - Media related resources
"""

from typing import List, Dict, Any


def register_media_resources(mcp, resolve, logger):
    """Register media-related resources."""

    @mcp.resource("resolve://media-pool-clips")
    def list_media_pool_clips() -> List[Dict[str, Any]]:
        """List all clips in the root folder of the media pool."""
        if resolve is None:
            return [{"error": "Not connected to DaVinci Resolve"}]

        project_manager = resolve.GetProjectManager()
        if not project_manager:
            return [{"error": "Failed to get Project Manager"}]

        current_project = project_manager.GetCurrentProject()
        if not current_project:
            return [{"error": "No project currently open"}]

        media_pool = current_project.GetMediaPool()
        if not media_pool:
            return [{"error": "Failed to get Media Pool"}]

        root_folder = media_pool.GetRootFolder()
        if not root_folder:
            return [{"error": "Failed to get root folder"}]

        clips = root_folder.GetClipList()
        if not clips:
            return [{"info": "No clips found in the root folder"}]

        result = []
        for clip in clips:
            result.append(
                {
                    "name": clip.GetName(),
                    "duration": clip.GetDuration(),
                    "fps": clip.GetClipProperty("FPS"),
                }
            )

        return result

    @mcp.resource("resolve://media-pool-bins")
    def list_media_pool_bins() -> List[Dict[str, Any]]:
        """List all bins/folders in the media pool."""
        try:
            from src.api.media_operations import list_bins as list_bins_func
        except ImportError:
            return [{"error": "Could not import media operations"}]

        return list_bins_func(resolve)

    @mcp.resource("resolve://media-pool-bin/{bin_name}")
    def get_media_pool_bin_contents(bin_name: str) -> List[Dict[str, Any]]:
        """Get contents of a specific bin/folder in the media pool."""
        try:
            from src.api.media_operations import (
                get_bin_contents as get_bin_contents_func,
            )
        except ImportError:
            return [{"error": "Could not import media operations"}]

        return get_bin_contents_func(resolve, bin_name)

    @mcp.resource("resolve://timeline-clips")
    def list_timeline_clips() -> List[Dict[str, Any]]:
        """List all clips in the current timeline."""
        if resolve is None:
            return [{"error": "Not connected to DaVinci Resolve"}]

        project_manager = resolve.GetProjectManager()
        if not project_manager:
            return [{"error": "Failed to get Project Manager"}]

        current_project = project_manager.GetCurrentProject()
        if not current_project:
            return [{"error": "No project currently open"}]

        current_timeline = current_project.GetCurrentTimeline()
        if not current_timeline:
            return [{"error": "No timeline currently active"}]

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
                return [{"info": "No clips found in the current timeline"}]

            return clips
        except Exception as e:
            return [{"error": f"Error listing timeline clips: {str(e)}"}]

    logger.info("Media resources registered")
