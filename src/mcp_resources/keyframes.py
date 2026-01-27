#!/usr/bin/env python3
"""
DaVinci Resolve MCP Resources - Keyframe related resources
"""

from typing import Dict, Any


def find_timeline_item(timeline, timeline_item_id):
    """Find a timeline item by ID across video and audio tracks."""
    video_track_count = timeline.GetTrackCount("video")
    for track_index in range(1, video_track_count + 1):
        items = timeline.GetItemListInTrack("video", track_index)
        if items:
            for item in items:
                if str(item.GetUniqueId()) == timeline_item_id:
                    return item, "video"

    audio_track_count = timeline.GetTrackCount("audio")
    for track_index in range(1, audio_track_count + 1):
        items = timeline.GetItemListInTrack("audio", track_index)
        if items:
            for item in items:
                if str(item.GetUniqueId()) == timeline_item_id:
                    return item, "audio"

    return None, None


def register_keyframe_resources(mcp, resolve, logger):
    """Register keyframe-related resources."""

    @mcp.resource(
        "resolve://timeline-item/{timeline_item_id}/keyframes/{property_name}"
    )
    def get_timeline_item_keyframes_endpoint(
        timeline_item_id: str, property_name: str
    ) -> Dict[str, Any]:
        """Get keyframes for a specific timeline item by ID."""
        if resolve is None:
            return {"error": "Not connected to DaVinci Resolve"}

        project_manager = resolve.GetProjectManager()
        if not project_manager:
            return {"error": "Failed to get Project Manager"}

        current_project = project_manager.GetCurrentProject()
        if not current_project:
            return {"error": "No project currently open"}

        current_timeline = current_project.GetCurrentTimeline()
        if not current_timeline:
            return {"error": "No timeline currently active"}

        try:
            timeline_item, _ = find_timeline_item(current_timeline, timeline_item_id)

            if not timeline_item:
                return {
                    "error": f"Timeline item with ID '{timeline_item_id}' not found"
                }

            video_properties = [
                "Pan",
                "Tilt",
                "ZoomX",
                "ZoomY",
                "Rotation",
                "AnchorPointX",
                "AnchorPointY",
                "Pitch",
                "Yaw",
                "Opacity",
                "CropLeft",
                "CropRight",
                "CropTop",
                "CropBottom",
            ]
            audio_properties = ["Volume", "Pan"]

            keyframeable_properties = []
            keyframes = {}

            if timeline_item.GetType() == "Video":
                for prop in video_properties:
                    if timeline_item.GetKeyframeCount(prop) > 0:
                        keyframeable_properties.append(prop)
                        keyframes[prop] = []
                        keyframe_count = timeline_item.GetKeyframeCount(prop)
                        for i in range(keyframe_count):
                            frame_pos = timeline_item.GetKeyframeAtIndex(prop, i)[
                                "frame"
                            ]
                            value = timeline_item.GetPropertyAtKeyframeIndex(prop, i)
                            keyframes[prop].append({"frame": frame_pos, "value": value})

            if (
                timeline_item.GetType() == "Audio"
                or timeline_item.GetMediaType() == "Audio"
            ):
                for prop in audio_properties:
                    if timeline_item.GetKeyframeCount(prop) > 0:
                        keyframeable_properties.append(prop)
                        keyframes[prop] = []
                        keyframe_count = timeline_item.GetKeyframeCount(prop)
                        for i in range(keyframe_count):
                            frame_pos = timeline_item.GetKeyframeAtIndex(prop, i)[
                                "frame"
                            ]
                            value = timeline_item.GetPropertyAtKeyframeIndex(prop, i)
                            keyframes[prop].append({"frame": frame_pos, "value": value})

            if property_name:
                if property_name in keyframes:
                    return {
                        "item_id": timeline_item_id,
                        "item_name": timeline_item.GetName(),
                        "properties": [property_name],
                        "keyframes": {property_name: keyframes[property_name]},
                    }
                else:
                    return {
                        "item_id": timeline_item_id,
                        "item_name": timeline_item.GetName(),
                        "properties": [],
                        "keyframes": {},
                    }

            return {
                "item_id": timeline_item_id,
                "item_name": timeline_item.GetName(),
                "properties": keyframeable_properties,
                "keyframes": keyframes,
            }

        except Exception as e:
            return {"error": f"Error getting timeline item keyframes: {str(e)}"}

    logger.info("Keyframe resources registered")
