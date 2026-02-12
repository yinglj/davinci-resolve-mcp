#!/usr/bin/env python3
"""
DaVinci Resolve Clip Operations
Clip management: timeline clips, adding, deleting, moving, subclips
"""

import logging
from typing import List, Dict, Any

from .pool import get_all_media_pool_clips

logger = logging.getLogger("davinci-resolve-mcp.media.clips")


def list_timeline_clips(resolve) -> List[Dict[str, Any]]:
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

    video_tracks = current_timeline.GetTrackCount("video")

    clip_info = []
    for track_index in range(1, video_tracks + 1):
        clips = current_timeline.GetItemListInTrack("video", track_index)
        for clip in clips:
            if clip:
                clip_info.append(
                    {
                        "name": clip.GetName(),
                        "track": f"V{track_index}",
                        "start_frame": clip.GetStart(),
                        "end_frame": clip.GetEnd(),
                        "duration": clip.GetDuration(),
                    }
                )

    audio_tracks = current_timeline.GetTrackCount("audio")
    for track_index in range(1, audio_tracks + 1):
        clips = current_timeline.GetItemListInTrack("audio", track_index)
        for clip in clips:
            if clip:
                clip_info.append(
                    {
                        "name": clip.GetName(),
                        "track": f"A{track_index}",
                        "start_frame": clip.GetStart(),
                        "end_frame": clip.GetEnd(),
                        "duration": clip.GetDuration(),
                    }
                )

    return (
        clip_info if clip_info else [{"info": "No clips found in the current timeline"}]
    )


def append_to_timeline(
    resolve,
    clip_name: str,
    start_frame: int = None,
    end_frame: int = None,
    track_index: int = 1,
    record_frame: int = None,
    timeline_name: str = None,
) -> str:
    """Append a media pool clip (or a frame range of it) to the timeline.

    Uses Resolve's native AppendToTimeline API which supports startFrame/endFrame
    for "virtual subclip" semantics — no need to create subclips first.

    Args:
        resolve: Resolve instance.
        clip_name: Name of the clip in the media pool.
        start_frame: Optional start frame for subclip range.
        end_frame: Optional end frame for subclip range.
        track_index: Target video track (default 1).
        record_frame: Optional position on the timeline to place the clip.
        timeline_name: Optional timeline name (uses current if not specified).

    Returns:
        str: Success or failure message.
    """
    if not resolve:
        return "Error: Not connected to DaVinci Resolve"

    # Get all clips from media pool (root + subfolders)
    pool_result = get_all_media_pool_clips(resolve)
    if isinstance(pool_result, dict) and "error" in pool_result:
        return f"Error: {pool_result['error']}"

    all_clips = pool_result["clips"]
    media_pool = pool_result["media_pool"]

    # Find target clip by name
    target_clip = None
    for clip in all_clips:
        if clip and clip.GetName() == clip_name:
            target_clip = clip
            break

    if not target_clip:
        available = [c.GetName() for c in all_clips if c]
        return f"Error: Clip '{clip_name}' not found in Media Pool. Available clips: {available}"

    # Switch timeline if specified
    if timeline_name:
        project_manager = resolve.GetProjectManager()
        current_project = project_manager.GetCurrentProject()
        timeline_count = current_project.GetTimelineCount()
        found = False
        for i in range(1, timeline_count + 1):
            t = current_project.GetTimelineByIndex(i)
            if t and t.GetName() == timeline_name:
                current_project.SetCurrentTimeline(t)
                found = True
                break
        if not found:
            return f"Error: Timeline '{timeline_name}' not found"

    # Build AppendToTimeline clip info dict
    clip_info = {"mediaPoolItem": target_clip}

    if start_frame is not None:
        clip_info["startFrame"] = int(start_frame)
    if end_frame is not None:
        clip_info["endFrame"] = int(end_frame)
    if track_index is not None:
        clip_info["trackIndex"] = int(track_index)
    if record_frame is not None:
        clip_info["recordFrame"] = int(record_frame)

    result = media_pool.AppendToTimeline([clip_info])

    if result and len(result) > 0:
        frame_info = ""
        if start_frame is not None and end_frame is not None:
            frame_info = f" (frames {start_frame}-{end_frame})"
        return f"Successfully appended clip '{clip_name}'{frame_info} to timeline"
    else:
        return f"Failed to append clip '{clip_name}' to timeline. Check if a timeline is active."


def get_clip_metadata(resolve, clip_name: str) -> Dict[str, Any]:
    """Get detailed metadata for a media pool clip by name.

    Args:
        resolve: Resolve instance.
        clip_name: Name of the clip to look for.

    Returns:
        dict: metadata including duration, fps, resolution, etc.
    """
    if not resolve:
        return {"error": "Not connected to DaVinci Resolve"}

    pool_result = get_all_media_pool_clips(resolve)
    if isinstance(pool_result, dict) and "error" in pool_result:
        return pool_result

    all_clips = pool_result["clips"]

    target_clip = None
    for clip in all_clips:
        if clip and clip.GetName() == clip_name:
            target_clip = clip
            break

    if not target_clip:
        return {"error": f"Clip '{clip_name}' not found in Media Pool"}

    props = target_clip.GetClipProperty()

    # Convert numeric values where possible
    metadata = {
        "name": target_clip.GetName(),
        "type": props.get("Type", "Unknown"),
        "duration": props.get("Duration", "Unknown"),
        "frames": props.get("Frames", "Unknown"),
        "fps": props.get("FPS", "Unknown"),
        "video_codec": props.get("Video Codec", "Unknown"),
        "audio_codec": props.get("Audio Codec", "Unknown"),
        "resolution": f"{props.get('Width', '?')}x{props.get('Height', '?')}",
        "width": props.get("Width", "Unknown"),
        "height": props.get("Height", "Unknown"),
        "start_timecode": props.get("Start TC", "Unknown"),
        "end_timecode": props.get("End TC", "Unknown"),
        "file_path": props.get("File Path", "Unknown"),
    }

    return metadata


def add_clip_to_timeline(resolve, clip_name: str, timeline_name: str = None) -> str:
    """Add a media pool clip to the timeline."""
    if not resolve:
        return "Error: Not connected to DaVinci Resolve"

    project_manager = resolve.GetProjectManager()
    if not project_manager:
        return "Error: Failed to get Project Manager"

    current_project = project_manager.GetCurrentProject()
    if not current_project:
        return "Error: No project currently open"

    media_pool = current_project.GetMediaPool()
    if not media_pool:
        return "Error: Failed to get Media Pool"

    root_folder = media_pool.GetRootFolder()
    clips = root_folder.GetClipList()

    target_clip = None
    for clip in clips:
        if clip.GetName() == clip_name:
            target_clip = clip
            break

    if not target_clip:
        return f"Error: Clip '{clip_name}' not found in Media Pool"

    timeline = None
    if timeline_name:
        timeline_count = current_project.GetTimelineCount()
        for i in range(1, timeline_count + 1):
            t = current_project.GetTimelineByIndex(i)
            if t and t.GetName() == timeline_name:
                timeline = t
                current_project.SetCurrentTimeline(timeline)
                break

        if not timeline:
            return f"Error: Timeline '{timeline_name}' not found"
    else:
        timeline = current_project.GetCurrentTimeline()
        if not timeline:
            return "Error: No timeline currently active"

    result = media_pool.AppendToTimeline([target_clip])

    if result and len(result) > 0:
        return f"Successfully added clip '{clip_name}' to timeline"
    else:
        return f"Failed to add clip '{clip_name}' to timeline"


def delete_media(resolve, clip_name: str) -> str:
    """Delete a media clip from the media pool by name."""
    result = get_all_media_pool_clips(resolve)
    if isinstance(result, dict) and "error" in result:
        return f"Error: {result['error']}"

    all_clips = result["clips"]
    media_pool = result["media_pool"]

    target_clip = None
    for clip in all_clips:
        if clip and clip.GetName() == clip_name:
            target_clip = clip
            break

    if not target_clip:
        return f"Error: Clip '{clip_name}' not found in Media Pool"

    try:
        delete_result = media_pool.DeleteClips([target_clip])
        if delete_result:
            return f"Successfully deleted clip '{clip_name}' from Media Pool"
        else:
            return f"Failed to delete clip '{clip_name}' from Media Pool"
    except Exception as e:
        return f"Error deleting clip: {str(e)}"


def move_media_to_bin(resolve, clip_name: str, bin_name: str) -> str:
    """Move a media clip to a specific bin in the media pool."""
    result = get_all_media_pool_clips(resolve)
    if isinstance(result, dict) and "error" in result:
        return f"Error: {result['error']}"

    all_clips = result["clips"]
    root_folder = result["root_folder"]
    folders = result["folders"]
    media_pool = result["media_pool"]

    # Find target bin
    target_folder = None
    if bin_name.lower() == "master" or bin_name == root_folder.GetName():
        target_folder = root_folder
    else:
        for folder in folders:
            if folder and folder.GetName() == bin_name:
                target_folder = folder
                break

    if not target_folder:
        return f"Error: Bin '{bin_name}' not found in Media Pool"

    # Find target clip
    target_clip = None
    for clip in all_clips:
        if clip and clip.GetName() == clip_name:
            target_clip = clip
            break

    if not target_clip:
        return f"Error: Clip '{clip_name}' not found in Media Pool"

    try:
        move_result = media_pool.MoveClips([target_clip], target_folder)
        if move_result:
            return f"Successfully moved clip '{clip_name}' to bin '{bin_name}'"
        else:
            return f"Failed to move clip '{clip_name}' to bin '{bin_name}'"
    except Exception as e:
        return f"Error moving clip: {str(e)}"


def create_sub_clip(
    resolve,
    clip_name: str,
    start_frame: int,
    end_frame: int,
    sub_clip_name: str = None,
    bin_name: str = None,
) -> str:
    """Create a subclip from the specified clip using in and out points."""
    if resolve is None:
        return "Error: Not connected to DaVinci Resolve"

    if not clip_name:
        return "Error: Clip name cannot be empty"

    if start_frame >= end_frame:
        return "Error: Start frame must be less than end frame"

    if start_frame < 0:
        return "Error: Start frame cannot be negative"

    result = get_all_media_pool_clips(resolve)
    if isinstance(result, dict) and "error" in result:
        return f"Error: {result['error']}"

    all_clips = result["clips"]
    root_folder = result["root_folder"]
    folders = result["folders"]
    media_pool = result["media_pool"]

    # Find source clip
    source_clip = None
    for clip in all_clips:
        if clip and clip.GetName() == clip_name:
            source_clip = clip
            break

    if not source_clip:
        return f"Error: Source clip '{clip_name}' not found in Media Pool"

    # Set target folder
    target_folder = root_folder
    if bin_name:
        target_folder = None
        if bin_name.lower() == "master" or bin_name == root_folder.GetName():
            target_folder = root_folder
        else:
            for folder in folders:
                if folder and folder.GetName() == bin_name:
                    target_folder = folder
                    break

            if not target_folder:
                return f"Error: Target bin '{bin_name}' not found in Media Pool"

    folder_result = media_pool.SetCurrentFolder(target_folder)
    if not folder_result:
        return f"Error: Failed to set current folder to '{target_folder.GetName()}'"

    if not sub_clip_name:
        sub_clip_name = f"{clip_name}_subclip"

    mark_result = source_clip.SetMarkInOut(start_frame, end_frame)
    if not mark_result:
        return f"Error: Failed to set in/out points on clip '{clip_name}'"

    try:
        sub_clip = media_pool.CreateSubClip(sub_clip_name, source_clip)

        if sub_clip:
            source_clip.ClearMarkInOut()
            return f"Successfully created subclip '{sub_clip_name}' from frames {start_frame} to {end_frame}"
        else:
            source_clip.ClearMarkInOut()
            return f"Error: Failed to create subclip from '{clip_name}'"

    except Exception as e:
        try:
            source_clip.ClearMarkInOut()
        except Exception:
            pass
        return f"Error creating subclip: {str(e)}"
