#!/usr/bin/env python3
"""
DaVinci Resolve MCP Resources - Media related resources
"""

import json
from typing import List, Dict, Any

from fastmcp.resources import ResourceContent, ResourceResult

import src.api.media as media_api


def register_media_resources(mcp, resolve, logger):
    """Register media-related resources."""

    def _clip_result(payload: List[Dict[str, Any]]) -> ResourceResult:
        """Normalize a media_api payload into the resource's stable contract.

        Clients read this resource as a JSON array of clip dicts:
        - error/info marker entries degrade to `[]` (a connector failure must
          not look like clip data);
        - every clip carries `name`, `clip_name` and `clipName` so consumers
          written against either key get the same value.
        """
        clips = []
        for entry in payload or []:
            if not isinstance(entry, dict) or "error" in entry or "info" in entry:
                continue
            clip = dict(entry)
            if clip.get("name") is not None:
                clip.setdefault("clip_name", clip["name"])
                clip.setdefault("clipName", clip["name"])
            clips.append(clip)
        return ResourceResult(
            contents=[ResourceContent(content=json.dumps(clips, ensure_ascii=False))]
        )

    @mcp.resource("resolve://media-pool-clips")
    def list_media_pool_clips() -> ResourceResult:
        """List all clips in the root folder of the media pool."""
        # Delegates to src.api.media so the payload logic lives in one place
        # (attribute lookup happens per call — the seam tests patch).
        return _clip_result(media_api.list_media_pool_clips(resolve))

    @mcp.resource("resolve://media-pool-bins")
    def list_media_pool_bins() -> List[Dict[str, Any]]:
        """List all bins/folders in the media pool."""
        # src.api.media_operations moved into the src.api.media package; the
        # old import path made this handler fail the moment it was called.
        return media_api.list_bins(resolve)

    @mcp.resource("resolve://media-pool-bin/{bin_name}")
    def get_media_pool_bin_contents(bin_name: str) -> List[Dict[str, Any]]:
        """Get contents of a specific bin/folder in the media pool."""
        return media_api.get_bin_contents(resolve, bin_name)

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
