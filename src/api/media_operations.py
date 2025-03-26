#!/usr/bin/env python3
"""
DaVinci Resolve Media Operations
"""

import logging
import os
from typing import List, Dict, Any

logger = logging.getLogger("davinci-resolve-mcp.media")

def list_media_pool_clips(resolve) -> List[Dict[str, Any]]:
    """List all clips in the media pool of the current project."""
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
    
    # Get the root folder and all its clips
    root_folder = media_pool.GetRootFolder()
    if not root_folder:
        return [{"error": "Failed to get Root Folder"}]
    
    clips = root_folder.GetClipList()
    
    # Format clip info
    clip_info = []
    for clip in clips:
        if clip:
            clip_info.append({
                "name": clip.GetName(),
                "type": clip.GetClipProperty()["Type"],
                "duration": clip.GetClipProperty()["Duration"],
                "fps": clip.GetClipProperty().get("FPS", "Unknown")
            })
    
    return clip_info if clip_info else [{"info": "No clips found in the media pool"}]

def import_media(resolve, file_path: str) -> str:
    """Import a media file into the current project's media pool."""
    if resolve is None:
        return "Error: Not connected to DaVinci Resolve"
    
    # Validate file path
    if not file_path:
        return "Error: File path cannot be empty"
    
    if not os.path.exists(file_path):
        return f"Error: File '{file_path}' does not exist"
    
    project_manager = resolve.GetProjectManager()
    if not project_manager:
        return "Error: Failed to get Project Manager"
    
    current_project = project_manager.GetCurrentProject()
    if not current_project:
        return "Error: No project currently open"
    
    media_pool = current_project.GetMediaPool()
    if not media_pool:
        return "Error: Failed to get Media Pool"
    
    # Import the media file
    # DaVinci Resolve API expects a list of file paths
    imported_media = media_pool.ImportMedia([file_path])
    
    if imported_media and len(imported_media) > 0:
        return f"Successfully imported '{os.path.basename(file_path)}'"
    else:
        return f"Failed to import '{file_path}'. The file may be in an unsupported format."

def create_bin(resolve, name: str) -> str:
    """Create a new bin/folder in the media pool."""
    if resolve is None:
        return "Error: Not connected to DaVinci Resolve"
    
    if not name:
        return "Error: Bin name cannot be empty"
    
    project_manager = resolve.GetProjectManager()
    if not project_manager:
        return "Error: Failed to get Project Manager"
    
    current_project = project_manager.GetCurrentProject()
    if not current_project:
        return "Error: No project currently open"
    
    media_pool = current_project.GetMediaPool()
    if not media_pool:
        return "Error: Failed to get Media Pool"
    
    # Get the root folder to add the bin to
    root_folder = media_pool.GetRootFolder()
    if not root_folder:
        return "Error: Failed to get Root Folder"
    
    # Check if bin already exists (by checking the subfolders)
    folders = root_folder.GetSubFolderList()
    for folder in folders:
        if folder.GetName() == name:
            return f"Error: Bin '{name}' already exists"
    
    # Create the bin
    new_bin = media_pool.AddSubFolder(root_folder, name)
    
    if new_bin:
        return f"Successfully created bin '{name}'"
    else:
        return f"Failed to create bin '{name}'"

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
    
    # Get all video tracks
    video_tracks = current_timeline.GetTrackCount("video")
    
    clip_info = []
    for track_index in range(1, video_tracks + 1):
        # Note: Track indices in Resolve API are 1-based
        clips = current_timeline.GetItemListInTrack("video", track_index)
        
        for clip in clips:
            if clip:
                clip_info.append({
                    "name": clip.GetName(),
                    "track": f"V{track_index}",
                    "start_frame": clip.GetStart(),
                    "end_frame": clip.GetEnd(),
                    "duration": clip.GetDuration()
                })
    
    # Get audio tracks as well
    audio_tracks = current_timeline.GetTrackCount("audio")
    for track_index in range(1, audio_tracks + 1):
        clips = current_timeline.GetItemListInTrack("audio", track_index)
        
        for clip in clips:
            if clip:
                clip_info.append({
                    "name": clip.GetName(),
                    "track": f"A{track_index}",
                    "start_frame": clip.GetStart(),
                    "end_frame": clip.GetEnd(),
                    "duration": clip.GetDuration()
                })
    
    return clip_info if clip_info else [{"info": "No clips found in the current timeline"}]

def add_clip_to_timeline(resolve, clip_name: str, timeline_name: str = None) -> str:
    """Add a media pool clip to the timeline.
    
    Args:
        resolve: The DaVinci Resolve instance
        clip_name: Name of the clip in the media pool
        timeline_name: Optional timeline to target (uses current if not specified)
    """
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
    
    # Get all clips in root folder
    root_folder = media_pool.GetRootFolder()
    clips = root_folder.GetClipList()
    
    target_clip = None
    for clip in clips:
        if clip.GetName() == clip_name:
            target_clip = clip
            break
    
    if not target_clip:
        return f"Error: Clip '{clip_name}' not found in Media Pool"
    
    # Get the target timeline
    timeline = None
    if timeline_name:
        # Switch to the specified timeline
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
        # Use current timeline
        timeline = current_project.GetCurrentTimeline()
        if not timeline:
            return "Error: No timeline currently active"
    
    # Add clip to timeline
    # We need to use media_pool.AppendToTimeline() which expects a list of clips
    result = media_pool.AppendToTimeline([target_clip])
    
    if result and len(result) > 0:
        return f"Successfully added clip '{clip_name}' to timeline"
    else:
        return f"Failed to add clip '{clip_name}' to timeline" 