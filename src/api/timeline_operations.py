#!/usr/bin/env python3
"""
DaVinci Resolve Timeline Operations
"""

import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger("davinci-resolve-mcp.timeline")

def list_timelines(resolve) -> List[str]:
    """List all timelines in the current project."""
    if resolve is None:
        return ["Error: Not connected to DaVinci Resolve"]
    
    project_manager = resolve.GetProjectManager()
    if not project_manager:
        return ["Error: Failed to get Project Manager"]
    
    current_project = project_manager.GetCurrentProject()
    if not current_project:
        return ["Error: No project currently open"]
    
    timeline_count = current_project.GetTimelineCount()
    timelines = []
    
    for i in range(1, timeline_count + 1):
        timeline = current_project.GetTimelineByIndex(i)
        if timeline:
            timelines.append(timeline.GetName())
    
    return timelines if timelines else ["No timelines found in the current project"]

def get_current_timeline_info(resolve) -> Dict[str, Any]:
    """Get information about the current timeline."""
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
    
    # Get basic timeline info
    info = {
        "name": current_timeline.GetName(),
        "framerate": current_timeline.GetSetting("timelineFrameRate"),
        "resolution": {
            "width": current_timeline.GetSetting("timelineResolutionWidth"),
            "height": current_timeline.GetSetting("timelineResolutionHeight")
        },
        "start_timecode": current_timeline.GetStartTimecode()
    }
    
    return info

def create_timeline(resolve, name: str) -> str:
    """Create a new timeline with the given name."""
    if resolve is None:
        return "Error: Not connected to DaVinci Resolve"
    
    if not name:
        return "Error: Timeline name cannot be empty"
    
    project_manager = resolve.GetProjectManager()
    if not project_manager:
        return "Error: Failed to get Project Manager"
    
    current_project = project_manager.GetCurrentProject()
    if not current_project:
        return "Error: No project currently open"
    
    media_pool = current_project.GetMediaPool()
    if not media_pool:
        return "Error: Failed to get Media Pool"
    
    # Check if timeline already exists to avoid duplicates
    existing_timelines = list_timelines(resolve)
    if name in existing_timelines:
        return f"Error: Timeline '{name}' already exists"
    
    # Create the timeline
    timeline = media_pool.CreateEmptyTimeline(name)
    if timeline:
        return f"Successfully created timeline '{name}'"
    else:
        return f"Failed to create timeline '{name}'"

def set_current_timeline(resolve, name: str) -> str:
    """Switch to a timeline by name."""
    if resolve is None:
        return "Error: Not connected to DaVinci Resolve"
    
    if not name:
        return "Error: Timeline name cannot be empty"
    
    project_manager = resolve.GetProjectManager()
    if not project_manager:
        return "Error: Failed to get Project Manager"
    
    current_project = project_manager.GetCurrentProject()
    if not current_project:
        return "Error: No project currently open"
    
    # First get a list of all timelines
    timeline_count = current_project.GetTimelineCount()
    
    for i in range(1, timeline_count + 1):
        timeline = current_project.GetTimelineByIndex(i)
        if timeline and timeline.GetName() == name:
            # Found the timeline, set it as current
            current_project.SetCurrentTimeline(timeline)
            # Verify it was set
            current_timeline = current_project.GetCurrentTimeline()
            if current_timeline and current_timeline.GetName() == name:
                return f"Successfully switched to timeline '{name}'"
            else:
                return f"Error: Failed to switch to timeline '{name}'"
    
    return f"Error: Timeline '{name}' not found"

def add_marker(resolve, frame: Optional[int] = None, color: str = "Blue", note: str = "") -> str:
    """Add a marker at the specified frame in the current timeline.
    
    Args:
        resolve: The DaVinci Resolve instance
        frame: The frame number to add the marker at (defaults to auto-selection if None)
        color: The marker color (Blue, Cyan, Green, Yellow, Red, Pink, Purple, Fuchsia, 
               Rose, Lavender, Sky, Mint, Lemon, Sand, Cocoa, Cream)
        note: Text note to add to the marker
    
    Returns:
        String indicating success or failure with detailed error message
    """
    if resolve is None:
        return "Error: Not connected to DaVinci Resolve"
    
    project_manager = resolve.GetProjectManager()
    if not project_manager:
        return "Error: Failed to get Project Manager"
    
    current_project = project_manager.GetCurrentProject()
    if not current_project:
        return "Error: No project currently open"
    
    current_timeline = current_project.GetCurrentTimeline()
    if not current_timeline:
        return "Error: No timeline currently active"
    
    # Get timeline information
    try:
        timeline_start = current_timeline.GetStartFrame()
        timeline_end = current_timeline.GetEndFrame()
        timeline_name = current_timeline.GetName()
        print(f"Timeline '{timeline_name}' frame range: {timeline_start}-{timeline_end}")
    except Exception as e:
        return f"Error: Failed to get timeline information: {str(e)}"
    
    # Validate marker color
    valid_colors = [
        "Blue", "Cyan", "Green", "Yellow", "Red", "Pink", 
        "Purple", "Fuchsia", "Rose", "Lavender", "Sky", 
        "Mint", "Lemon", "Sand", "Cocoa", "Cream"
    ]
    
    if color not in valid_colors:
        return f"Error: Invalid marker color. Valid colors are: {', '.join(valid_colors)}"
    
    try:
        # Get information about clips in the timeline
        clips = []
        for track_idx in range(1, 5):  # Check first 4 video tracks
            try:
                track_clips = current_timeline.GetItemListInTrack("video", track_idx)
                if track_clips and len(track_clips) > 0:
                    clips.extend(track_clips)
            except:
                continue
        
        if not clips:
            return "Error: No clips found in timeline. Add media to the timeline first."
        
        # Get existing markers to avoid conflicts
        existing_markers = current_timeline.GetMarkers() or {}
        
        # If no frame specified, find a good position
        if frame is None:
            # Try to find a frame in the middle of a clip that doesn't have a marker
            for clip in clips:
                clip_start = clip.GetStart()
                clip_end = clip.GetEnd()
                
                # Try middle of clip
                mid_frame = clip_start + ((clip_end - clip_start) // 2)
                if mid_frame not in existing_markers:
                    frame = mid_frame
                    break
                
                # Try middle + 1
                if (mid_frame + 1) not in existing_markers:
                    frame = mid_frame + 1
                    break
                
                # Try other positions in the clip
                for offset in [10, 20, 30, 40, 50]:
                    test_frame = clip_start + offset
                    if clip_start <= test_frame <= clip_end and test_frame not in existing_markers:
                        frame = test_frame
                        break
            
            # If we still don't have a frame, use the first valid position we can find
            if frame is None:
                for f in range(timeline_start, timeline_end, 10):
                    if f not in existing_markers:
                        # Check if this frame is within a clip
                        for clip in clips:
                            if clip.GetStart() <= f <= clip.GetEnd():
                                frame = f
                                break
                    if frame is not None:
                        break
            
            # If we still don't have a frame, report error
            if frame is None:
                return "Error: Could not find a valid frame position for marker. Try specifying a frame number."
        
        # Frame specified - validate it
        else:
            # Check if frame is within timeline bounds
            if frame < timeline_start or frame > timeline_end:
                return f"Error: Frame {frame} is out of timeline bounds ({timeline_start}-{timeline_end})"
            
            # Check if frame already has a marker
            if frame in existing_markers:
                # Suggest an alternate frame
                alternate_found = False
                alternates = [frame + 1, frame - 1, frame + 2, frame + 5, frame + 10]
                
                for alt_frame in alternates:
                    if timeline_start <= alt_frame <= timeline_end and alt_frame not in existing_markers:
                        # Check if frame is within a clip
                        for clip in clips:
                            if clip.GetStart() <= alt_frame <= clip.GetEnd():
                                return f"Error: A marker already exists at frame {frame}. Try frame {alt_frame} instead."
                
                return f"Error: A marker already exists at frame {frame}. Try a different frame position."
            
            # Verify frame is within a clip
            frame_in_clip = False
            for clip in clips:
                if clip.GetStart() <= frame <= clip.GetEnd():
                    frame_in_clip = True
                    break
            
            if not frame_in_clip:
                return f"Error: Frame {frame} is not within any media in the timeline. Markers must be on actual clips."
        
        # Add the marker
        print(f"Adding marker at frame {frame} with color {color}")
        result = current_timeline.AddMarker(
            frame,
            color,
            note or "Marker",
            note,
            1,
            ""
        )
        
        if result:
            return f"Successfully added {color} marker at frame {frame}"
        else:
            # One last check if a marker was created despite returning False
            updated_markers = current_timeline.GetMarkers() or {}
            if frame in updated_markers:
                return f"Successfully added marker at frame {frame} (unexpected response)"
            else:
                return f"Failed to add marker at frame {frame}. Try a different frame position."
    
    except Exception as e:
        return f"Error adding marker: {str(e)}" 