#!/usr/bin/env python3
"""DaVinci Resolve MCP - Graph Operations (Granular Tools)."""

from typing import Any, Dict, List, Optional, Union, Tuple
from .common import mcp, get_resolve

@mcp.tool()
def apply_lut(lut_path: str, node_index: int = None) -> str:
    """Apply a LUT to a node in the color page.
    
    Args:
        lut_path: Path to the LUT file to apply
        node_index: Index of the node to apply the LUT to (uses current node if None)
    """
    from api.color_operations import apply_lut as apply_lut_func
    return apply_lut_func(resolve, lut_path, node_index)

@mcp.tool()
def set_color_wheel_param(wheel: str, param: str, value: float, node_index: int = None) -> str:
    """Set a color wheel parameter for a node.
    
    Args:
        wheel: Which color wheel to adjust ('lift', 'gamma', 'gain', 'offset')
        param: Which parameter to adjust ('red', 'green', 'blue', 'master')
        value: The value to set (typically between -1.0 and 1.0)
        node_index: Index of the node to set parameter for (uses current node if None)
    """
    from api.color_operations import set_color_wheel_param as set_param_func
    return set_param_func(resolve, wheel, param, value, node_index)

@mcp.tool()
def add_node(node_type: str = "serial", label: str = None) -> str:
    """Add a new node to the current grade in the color page.
    
    Args:
        node_type: Type of node to add. Options: 'serial', 'parallel', 'layer'
        label: Optional label/name for the new node
    """
    from api.color_operations import add_node as add_node_func
    return add_node_func(resolve, node_type, label)

@mcp.tool()
def copy_grade(source_clip_name: str = None, target_clip_name: str = None, mode: str = "full") -> str:
    """Copy a grade from one clip to another in the color page.
    
    Args:
        source_clip_name: Name of the source clip to copy grade from (uses current clip if None)
        target_clip_name: Name of the target clip to apply grade to (uses current clip if None)
        mode: What to copy - 'full' (entire grade), 'current_node', or 'all_nodes'
    """
    from api.color_operations import copy_grade as copy_grade_func
    return copy_grade_func(resolve, source_clip_name, target_clip_name, mode)

# ------------------
# Delivery Page Operations
# ------------------

@mcp.resource("resolve://delivery/render-presets")
def get_render_presets() -> List[Dict[str, Any]]:
    """Get all available render presets in the current project."""
    from api.delivery_operations import get_render_presets as get_presets_func
    return get_presets_func(resolve)

@mcp.tool()
def add_keyframe(timeline_item_id: str, property_name: str, frame: int, value: float) -> str:
    """Add a keyframe at the specified frame for a timeline item property.
    
    Args:
        timeline_item_id: The ID of the timeline item to add keyframe to
        property_name: The name of the property to keyframe (e.g., 'Pan', 'ZoomX')
        frame: Frame position for the keyframe
        value: Value to set at the keyframe
    """
    pm, current_project = get_current_project()
    if not current_project:
        return "Error: No project currently open"
    
    current_timeline = current_project.GetCurrentTimeline()
    if not current_timeline:
        return "Error: No timeline currently active"
    
    # Valid keyframeable properties
    video_properties = [
        'Pan', 'Tilt', 'ZoomX', 'ZoomY', 'Rotation', 'AnchorPointX', 'AnchorPointY',
        'Pitch', 'Yaw', 'Opacity', 'CropLeft', 'CropRight', 'CropTop', 'CropBottom'
    ]
    
    audio_properties = ['Volume', 'Pan']
    
    valid_properties = video_properties + audio_properties
    
    if property_name not in valid_properties:
        return f"Error: Invalid property name. Must be one of: {', '.join(valid_properties)}"
    
    try:
        # Find the timeline item by ID
        video_track_count = current_timeline.GetTrackCount("video")
        audio_track_count = current_timeline.GetTrackCount("audio")
        
        timeline_item = None
        is_audio = False
        
        # Search video tracks
        for track_index in range(1, video_track_count + 1):
            items = current_timeline.GetItemListInTrack("video", track_index)
            if items:
                for item in items:
                    if str(item.GetUniqueId()) == timeline_item_id:
                        timeline_item = item
                        break
            if timeline_item:
                break
        
        # If not found, search audio tracks
        if not timeline_item:
            for track_index in range(1, audio_track_count + 1):
                items = current_timeline.GetItemListInTrack("audio", track_index)
                if items:
                    for item in items:
                        if str(item.GetUniqueId()) == timeline_item_id:
                            timeline_item = item
                            is_audio = True
                            break
                if timeline_item:
                    break
        
        if not timeline_item:
            return f"Error: Timeline item with ID '{timeline_item_id}' not found"
        
        # Check if the specified property is valid for this item type
        if is_audio and property_name not in audio_properties:
            return f"Error: Property '{property_name}' is not available for audio items"
        
        if not is_audio and property_name not in video_properties and timeline_item.GetType() != "Video":
            return f"Error: Property '{property_name}' is not available for this item type"
            
        # Validate frame is within the item's range
        start_frame = timeline_item.GetStart()
        end_frame = timeline_item.GetEnd()
        
        if frame < start_frame or frame > end_frame:
            return f"Error: Frame {frame} is outside the item's range ({start_frame} to {end_frame})"
        
        # Add the keyframe
        result = timeline_item.AddKeyframe(property_name, frame, value)
        
        if result:
            return f"Successfully added keyframe for {property_name} at frame {frame} with value {value}"
        else:
            return f"Failed to add keyframe for {property_name} at frame {frame}"
        
    except Exception as e:
        return f"Error adding keyframe: {str(e)}"

@mcp.tool()
def modify_keyframe(timeline_item_id: str, property_name: str, frame: int, new_value: float = None, new_frame: int = None) -> str:
    """Modify an existing keyframe by changing its value or frame position.
    
    Args:
        timeline_item_id: The ID of the timeline item
        property_name: The name of the property with keyframe
        frame: Current frame position of the keyframe to modify
        new_value: Optional new value for the keyframe
        new_frame: Optional new frame position for the keyframe
    """
    pm, current_project = get_current_project()
    if not current_project:
        return "Error: No project currently open"
    
    current_timeline = current_project.GetCurrentTimeline()
    if not current_timeline:
        return "Error: No timeline currently active"
    
    if new_value is None and new_frame is None:
        return "Error: Must specify at least one of new_value or new_frame"
    
    try:
        # Find the timeline item by ID
        video_track_count = current_timeline.GetTrackCount("video")
        audio_track_count = current_timeline.GetTrackCount("audio")
        
        timeline_item = None
        
        # Search video tracks
        for track_index in range(1, video_track_count + 1):
            items = current_timeline.GetItemListInTrack("video", track_index)
            if items:
                for item in items:
                    if str(item.GetUniqueId()) == timeline_item_id:
                        timeline_item = item
                        break
            if timeline_item:
                break
        
        # If not found, search audio tracks
        if not timeline_item:
            for track_index in range(1, audio_track_count + 1):
                items = current_timeline.GetItemListInTrack("audio", track_index)
                if items:
                    for item in items:
                        if str(item.GetUniqueId()) == timeline_item_id:
                            timeline_item = item
                            break
                if timeline_item:
                    break
        
        if not timeline_item:
            return f"Error: Timeline item with ID '{timeline_item_id}' not found"
        
        # Check if the property has keyframes
        keyframe_count = timeline_item.GetKeyframeCount(property_name)
        if keyframe_count == 0:
            return f"Error: No keyframes found for property '{property_name}'"
        
        # Find the keyframe at the specified frame
        keyframe_index = -1
        for i in range(keyframe_count):
            kf = timeline_item.GetKeyframeAtIndex(property_name, i)
            if kf["frame"] == frame:
                keyframe_index = i
                break
        
        if keyframe_index == -1:
            return f"Error: No keyframe found at frame {frame} for property '{property_name}'"
        
        if new_frame is not None:
            # Check if new frame is within the item's range
            start_frame = timeline_item.GetStart()
            end_frame = timeline_item.GetEnd()
            
            if new_frame < start_frame or new_frame > end_frame:
                return f"Error: New frame {new_frame} is outside the item's range ({start_frame} to {end_frame})"
                
            # Delete the keyframe at the current frame
            current_value = timeline_item.GetPropertyAtKeyframeIndex(property_name, keyframe_index)
            timeline_item.DeleteKeyframe(property_name, frame)
            
            # Add a new keyframe at the new frame position with the current value (or new value if specified)
            value = new_value if new_value is not None else current_value
            result = timeline_item.AddKeyframe(property_name, new_frame, value)
            
            if result:
                return f"Successfully moved keyframe for {property_name} from frame {frame} to frame {new_frame}"
            else:
                return f"Failed to move keyframe for {property_name}"
        else:
            # Only changing the value, not the frame position
            # We need to delete and re-add the keyframe with the new value
            timeline_item.DeleteKeyframe(property_name, frame)
            result = timeline_item.AddKeyframe(property_name, frame, new_value)
            
            if result:
                return f"Successfully updated keyframe value for {property_name} at frame {frame} to {new_value}"
            else:
                return f"Failed to update keyframe value for {property_name} at frame {frame}"
        
    except Exception as e:
        return f"Error modifying keyframe: {str(e)}"

@mcp.tool()
def delete_keyframe(timeline_item_id: str, property_name: str, frame: int) -> str:
    """Delete a keyframe at the specified frame for a timeline item property.
    
    Args:
        timeline_item_id: The ID of the timeline item
        property_name: The name of the property with keyframe to delete
        frame: Frame position of the keyframe to delete
    """
    pm, current_project = get_current_project()
    if not current_project:
        return "Error: No project currently open"
    
    current_timeline = current_project.GetCurrentTimeline()
    if not current_timeline:
        return "Error: No timeline currently active"
    
    try:
        # Find the timeline item by ID
        video_track_count = current_timeline.GetTrackCount("video")
        audio_track_count = current_timeline.GetTrackCount("audio")
        
        timeline_item = None
        
        # Search video tracks
        for track_index in range(1, video_track_count + 1):
            items = current_timeline.GetItemListInTrack("video", track_index)
            if items:
                for item in items:
                    if str(item.GetUniqueId()) == timeline_item_id:
                        timeline_item = item
                        break
            if timeline_item:
                break
        
        # If not found, search audio tracks
        if not timeline_item:
            for track_index in range(1, audio_track_count + 1):
                items = current_timeline.GetItemListInTrack("audio", track_index)
                if items:
                    for item in items:
                        if str(item.GetUniqueId()) == timeline_item_id:
                            timeline_item = item
                            break
                if timeline_item:
                    break
        
        if not timeline_item:
            return f"Error: Timeline item with ID '{timeline_item_id}' not found"
        
        # Check if the property has keyframes
        keyframe_count = timeline_item.GetKeyframeCount(property_name)
        if keyframe_count == 0:
            return f"Error: No keyframes found for property '{property_name}'"
        
        # Check if there's a keyframe at the specified frame
        keyframe_exists = False
        for i in range(keyframe_count):
            kf = timeline_item.GetKeyframeAtIndex(property_name, i)
            if kf["frame"] == frame:
                keyframe_exists = True
                break
        
        if not keyframe_exists:
            return f"Error: No keyframe found at frame {frame} for property '{property_name}'"
        
        # Delete the keyframe
        result = timeline_item.DeleteKeyframe(property_name, frame)
        
        if result:
            return f"Successfully deleted keyframe for {property_name} at frame {frame}"
        else:
            return f"Failed to delete keyframe for {property_name} at frame {frame}"
        
    except Exception as e:
        return f"Error deleting keyframe: {str(e)}"

@mcp.tool()
def set_keyframe_interpolation(timeline_item_id: str, property_name: str, frame: int, interpolation_type: str) -> str:
    """Set the interpolation type for a keyframe.
    
    Args:
        timeline_item_id: The ID of the timeline item
        property_name: The name of the property with keyframe
        frame: Frame position of the keyframe
        interpolation_type: Type of interpolation. Options: 'Linear', 'Bezier', 'Ease-In', 'Ease-Out'
    """
    pm, current_project = get_current_project()
    if not current_project:
        return "Error: No project currently open"
    
    current_timeline = current_project.GetCurrentTimeline()
    if not current_timeline:
        return "Error: No timeline currently active"
    
    # Validate interpolation type
    valid_interpolation_types = ['Linear', 'Bezier', 'Ease-In', 'Ease-Out']
    if interpolation_type not in valid_interpolation_types:
        return f"Error: Invalid interpolation type. Must be one of: {', '.join(valid_interpolation_types)}"
    
    try:
        # Find the timeline item by ID
        video_track_count = current_timeline.GetTrackCount("video")
        audio_track_count = current_timeline.GetTrackCount("audio")
        
        timeline_item = None
        
        # Search video tracks
        for track_index in range(1, video_track_count + 1):
            items = current_timeline.GetItemListInTrack("video", track_index)
            if items:
                for item in items:
                    if str(item.GetUniqueId()) == timeline_item_id:
                        timeline_item = item
                        break
            if timeline_item:
                break
        
        # If not found, search audio tracks
        if not timeline_item:
            for track_index in range(1, audio_track_count + 1):
                items = current_timeline.GetItemListInTrack("audio", track_index)
                if items:
                    for item in items:
                        if str(item.GetUniqueId()) == timeline_item_id:
                            timeline_item = item
                            break
                if timeline_item:
                    break
        
        if not timeline_item:
            return f"Error: Timeline item with ID '{timeline_item_id}' not found"
        
        # Check if the property has keyframes
        keyframe_count = timeline_item.GetKeyframeCount(property_name)
        if keyframe_count == 0:
            return f"Error: No keyframes found for property '{property_name}'"
        
        # Check if there's a keyframe at the specified frame
        keyframe_exists = False
        for i in range(keyframe_count):
            kf = timeline_item.GetKeyframeAtIndex(property_name, i)
            if kf["frame"] == frame:
                keyframe_exists = True
                break
        
        if not keyframe_exists:
            return f"Error: No keyframe found at frame {frame} for property '{property_name}'"
        
        # Set the interpolation type
        interpolation_map = {
            'Linear': 0,
            'Bezier': 1,
            'Ease-In': 2,
            'Ease-Out': 3
        }
        
        # Get current keyframe value
        value = None
        for i in range(keyframe_count):
            kf = timeline_item.GetKeyframeAtIndex(property_name, i)
            if kf["frame"] == frame:
                value = timeline_item.GetPropertyAtKeyframeIndex(property_name, i)
                break
        
        # Delete the old keyframe
        timeline_item.DeleteKeyframe(property_name, frame)
        
        # Add a new keyframe with the same value but different interpolation
        result = timeline_item.AddKeyframe(property_name, frame, value, interpolation_map[interpolation_type])
        
        if result:
            return f"Successfully set interpolation for {property_name} keyframe at frame {frame} to {interpolation_type}"
        else:
            return f"Failed to set interpolation for {property_name} keyframe at frame {frame}"
        
    except Exception as e:
        return f"Error setting keyframe interpolation: {str(e)}"

@mcp.tool()
def enable_keyframes(timeline_item_id: str, keyframe_mode: str = "All") -> str:
    """Enable keyframe mode for a timeline item.
    
    Args:
        timeline_item_id: The ID of the timeline item
        keyframe_mode: Keyframe mode to enable. Options: 'All', 'Color', 'Sizing'
    """
    pm, current_project = get_current_project()
    if not current_project:
        return "Error: No project currently open"
    
    current_timeline = current_project.GetCurrentTimeline()
    if not current_timeline:
        return "Error: No timeline currently active"
    
    # Validate keyframe mode
    valid_keyframe_modes = ['All', 'Color', 'Sizing']
    if keyframe_mode not in valid_keyframe_modes:
        return f"Error: Invalid keyframe mode. Must be one of: {', '.join(valid_keyframe_modes)}"
    
    try:
        # Find the timeline item by ID
        video_track_count = current_timeline.GetTrackCount("video")
        
        timeline_item = None
        
        # Search video tracks
        for track_index in range(1, video_track_count + 1):
            items = current_timeline.GetItemListInTrack("video", track_index)
            if items:
                for item in items:
                    if str(item.GetUniqueId()) == timeline_item_id:
                        timeline_item = item
                        break
            if timeline_item:
                break
        
        if not timeline_item:
            return f"Error: Video timeline item with ID '{timeline_item_id}' not found"
        
        if timeline_item.GetType() != "Video":
            return f"Error: Timeline item with ID '{timeline_item_id}' is not a video item"
        
        # Set the keyframe mode
        keyframe_mode_map = {
            'All': 0,
            'Color': 1,
            'Sizing': 2
        }
        
        result = timeline_item.SetProperty("KeyframeMode", keyframe_mode_map[keyframe_mode])
        
        if result:
            return f"Successfully enabled {keyframe_mode} keyframe mode for timeline item '{timeline_item.GetName()}'"
        else:
            return f"Failed to enable {keyframe_mode} keyframe mode for timeline item '{timeline_item.GetName()}'"
        
    except Exception as e:
        return f"Error enabling keyframe mode: {str(e)}"

# ------------------
# Color Preset Management
# ------------------

@mcp.resource("resolve://color/presets")
def get_color_presets() -> List[Dict[str, Any]]:
    """Get all available color presets in the current project."""
    pm, current_project = get_current_project()
    if not current_project:
        return [{"error": "No project currently open"}]
    
    # Switch to color page to access presets
    current_page = resolve.GetCurrentPage()
    if current_page != "color":
        resolve.OpenPage("color")
    
    try:
        # Get gallery
        gallery = current_project.GetGallery()
        if not gallery:
            return [{"error": "Failed to get gallery"}]
        
        # Get all albums
        albums = gallery.GetAlbums()
        if not albums:
            return [{"info": "No albums found in gallery"}]
        
        result = []
        for album in albums:
            # Get stills in the album
            stills = album.GetStills()
            album_info = {
                "name": album.GetName(),
                "stills": []
            }
            
            if stills:
                for still in stills:
                    still_info = {
                        "id": still.GetUniqueId(),
                        "label": still.GetLabel(),
                        "timecode": still.GetTimecode(),
                        "isGrabbed": still.IsGrabbed()
                    }
                    album_info["stills"].append(still_info)
            
            result.append(album_info)
        
        # Return to the original page if we switched
        if current_page != "color":
            resolve.OpenPage(current_page)
            
        return result
    
    except Exception as e:
        # Return to the original page if we switched
        if current_page != "color":
            resolve.OpenPage(current_page)
        return [{"error": f"Error retrieving color presets: {str(e)}"}]

@mcp.tool()
def set_project_property_tool(property_name: str, property_value: Any) -> str:
    """Set a project property value.
    
    Args:
        property_name: Name of the property to set
        property_value: Value to set for the property
    """
    pm, current_project = get_current_project()
    if not current_project:
        return "Error: No project currently open"
    
    result = set_project_property(current_project, property_name, property_value)
    
    if result:
        return f"Successfully set project property '{property_name}' to '{property_value}'"
    else:
        return f"Failed to set project property '{property_name}'"

@mcp.resource("resolve://project/timeline-format")
def get_timeline_format() -> Dict[str, Any]:
    """Get timeline format settings for the current project."""
    pm, current_project = get_current_project()
    if not current_project:
        return {"error": "No project currently open"}
    
    return get_timeline_format_settings(current_project)

@mcp.tool()
def set_timeline_format_tool(width: int, height: int, frame_rate: float, interlaced: bool = False) -> str:
    """Set timeline format (resolution and frame rate).
    
    Args:
        width: Timeline width in pixels
        height: Timeline height in pixels
        frame_rate: Timeline frame rate
        interlaced: Whether the timeline should use interlaced processing
    """
    pm, current_project = get_current_project()
    if not current_project:
        return "Error: No project currently open"
    
    result = set_timeline_format(current_project, width, height, frame_rate, interlaced)
    
    if result:
        interlace_status = "interlaced" if interlaced else "progressive"
        return f"Successfully set timeline format to {width}x{height} at {frame_rate} fps ({interlace_status})"
    else:
        return "Failed to set timeline format"

@mcp.resource("resolve://project/superscale")
def get_superscale_settings_endpoint() -> Dict[str, Any]:
    """Get SuperScale settings for the current project."""
    pm, current_project = get_current_project()
    if not current_project:
        return {"error": "No project currently open"}
    
    return get_superscale_settings(current_project)

@mcp.tool()
def set_superscale_settings_tool(enabled: bool, quality: int = 0) -> str:
    """Set SuperScale settings for the current project.
    
    Args:
        enabled: Whether SuperScale is enabled
        quality: SuperScale quality (0=Auto, 1=Better Quality, 2=Smoother)
    """
    pm, current_project = get_current_project()
    if not current_project:
        return "Error: No project currently open"
    
    quality_names = {
        0: "Auto",
        1: "Better Quality",
        2: "Smoother"
    }
    
    result = set_superscale_settings(current_project, enabled, quality)
    
    if result:
        status = "enabled" if enabled else "disabled"
        quality_name = quality_names.get(quality, "Unknown")
        return f"Successfully {status} SuperScale with quality set to {quality_name}"
    else:
        return "Failed to set SuperScale settings"

@mcp.resource("resolve://project/color-settings")
def get_color_settings_endpoint() -> Dict[str, Any]:
    """Get color science and color space settings for the current project."""
    pm, current_project = get_current_project()
    if not current_project:
        return {"error": "No project currently open"}
    
    return get_color_settings(current_project)

@mcp.tool()
def set_color_science_mode_tool(mode: str) -> str:
    """Set color science mode for the current project.
    
    Args:
        mode: Color science mode ('YRGB', 'YRGB Color Managed', 'ACEScct', or numeric value)
    """
    pm, current_project = get_current_project()
    if not current_project:
        return "Error: No project currently open"
    
    result = set_color_science_mode(current_project, mode)
    
    if result:
        return f"Successfully set color science mode to '{mode}'"
    else:
        return f"Failed to set color science mode to '{mode}'"

@mcp.tool()
def set_color_space_tool(color_space: str, gamma: str = None) -> str:
    """Set timeline color space and gamma.
    
    Args:
        color_space: Timeline color space (e.g., 'Rec.709', 'DCI-P3 D65', 'Rec.2020')
        gamma: Timeline gamma (e.g., 'Rec.709 Gamma', 'Gamma 2.4')
    """
    pm, current_project = get_current_project()
    if not current_project:
        return "Error: No project currently open"
    
    result = set_color_space(current_project, color_space, gamma)
    
    if result:
        if gamma:
            return f"Successfully set timeline color space to '{color_space}' with gamma '{gamma}'"
        else:
            return f"Successfully set timeline color space to '{color_space}'"
    else:
        return "Failed to set timeline color space"

@mcp.resource("resolve://project/metadata")
def get_project_metadata_endpoint() -> Dict[str, Any]:
    """Get metadata for the current project."""
    pm, current_project = get_current_project()
    if not current_project:
        return {"error": "No project currently open"}
    
    return get_project_metadata(current_project)

@mcp.resource("resolve://project/info")
def get_project_info_endpoint() -> Dict[str, Any]:
    """Get comprehensive information about the current project."""
    pm, current_project = get_current_project()
    if not current_project:
        return {"error": "No project currently open"}
    
    return get_project_info(current_project)

# ------------------
# MediaStorage Tools
# ------------------

@mcp.tool()
def graph_get_num_nodes(item_index: int = 0, track_type: str = "video", track_index: int = 1) -> Dict[str, Any]:
    """Get number of nodes in the color graph for a timeline item.

    Args:
        item_index: 0-based item index. Default: 0.
        track_type: 'video' or 'audio'. Default: 'video'.
        track_index: 1-based track index. Default: 1.
    """
    item, err = _get_timeline_item(track_type, track_index, item_index)
    if err:
        return err
    graph = item.GetNodeGraph()
    if not graph:
        return {"error": "No node graph available"}
    return {"num_nodes": graph.GetNumNodes()}

@mcp.tool()
def graph_set_lut(node_index: int, lut_path: str, item_index: int = 0, track_type: str = "video", track_index: int = 1) -> Dict[str, Any]:
    """Set LUT on a node in the color graph.

    Args:
        node_index: 1-based node index.
        lut_path: Absolute or relative LUT path.
        item_index: 0-based timeline item index. Default: 0.
        track_type: 'video' or 'audio'. Default: 'video'.
        track_index: 1-based track index. Default: 1.
    """
    item, err = _get_timeline_item(track_type, track_index, item_index)
    if err:
        return err
    graph = item.GetNodeGraph()
    if not graph:
        return {"error": "No node graph available"}
    result = graph.SetLUT(node_index, lut_path)
    return {"success": bool(result)}

@mcp.tool()
def graph_get_lut(node_index: int, item_index: int = 0, track_type: str = "video", track_index: int = 1) -> Dict[str, Any]:
    """Get LUT path on a node in the color graph.

    Args:
        node_index: 1-based node index.
        item_index: 0-based timeline item index. Default: 0.
        track_type: 'video' or 'audio'. Default: 'video'.
        track_index: 1-based track index. Default: 1.
    """
    item, err = _get_timeline_item(track_type, track_index, item_index)
    if err:
        return err
    graph = item.GetNodeGraph()
    if not graph:
        return {"error": "No node graph available"}
    lut = graph.GetLUT(node_index)
    return {"node_index": node_index, "lut_path": lut if lut else ""}

@mcp.tool()
def graph_set_node_cache_mode(node_index: int, cache_value: int, item_index: int = 0, track_type: str = "video", track_index: int = 1) -> Dict[str, Any]:
    """Set the cache mode on a node.

    Args:
        node_index: 1-based node index.
        cache_value: -1=Auto, 0=Disabled, 1=Enabled.
        item_index: 0-based timeline item index. Default: 0.
        track_type: 'video' or 'audio'. Default: 'video'.
        track_index: 1-based track index. Default: 1.
    """
    item, err = _get_timeline_item(track_type, track_index, item_index)
    if err:
        return err
    graph = item.GetNodeGraph()
    if not graph:
        return {"error": "No node graph available"}
    result = graph.SetNodeCacheMode(node_index, cache_value)
    return {"success": bool(result)}

@mcp.tool()
def graph_get_node_cache_mode(node_index: int, item_index: int = 0, track_type: str = "video", track_index: int = 1) -> Dict[str, Any]:
    """Get the cache mode of a node.

    Args:
        node_index: 1-based node index.
        item_index: 0-based timeline item index. Default: 0.
        track_type: 'video' or 'audio'. Default: 'video'.
        track_index: 1-based track index. Default: 1.
    """
    item, err = _get_timeline_item(track_type, track_index, item_index)
    if err:
        return err
    graph = item.GetNodeGraph()
    if not graph:
        return {"error": "No node graph available"}
    mode = graph.GetNodeCacheMode(node_index)
    modes = {-1: "Auto", 0: "Disabled", 1: "Enabled"}
    return {"node_index": node_index, "cache_mode": mode, "mode_name": modes.get(mode, "Unknown")}

@mcp.tool()
def graph_get_node_label(node_index: int, item_index: int = 0, track_type: str = "video", track_index: int = 1) -> Dict[str, Any]:
    """Get the label of a node.

    Args:
        node_index: 1-based node index.
        item_index: 0-based timeline item index. Default: 0.
        track_type: 'video' or 'audio'. Default: 'video'.
        track_index: 1-based track index. Default: 1.
    """
    item, err = _get_timeline_item(track_type, track_index, item_index)
    if err:
        return err
    graph = item.GetNodeGraph()
    if not graph:
        return {"error": "No node graph available"}
    label = graph.GetNodeLabel(node_index)
    return {"node_index": node_index, "label": label if label else ""}

@mcp.tool()
def graph_get_tools_in_node(node_index: int, item_index: int = 0, track_type: str = "video", track_index: int = 1) -> Dict[str, Any]:
    """Get list of tools used in a node.

    Args:
        node_index: 1-based node index.
        item_index: 0-based timeline item index. Default: 0.
        track_type: 'video' or 'audio'. Default: 'video'.
        track_index: 1-based track index. Default: 1.
    """
    item, err = _get_timeline_item(track_type, track_index, item_index)
    if err:
        return err
    graph = item.GetNodeGraph()
    if not graph:
        return {"error": "No node graph available"}
    tools = graph.GetToolsInNode(node_index)
    return {"node_index": node_index, "tools": tools if tools else []}

@mcp.tool()
def graph_set_node_enabled(node_index: int, is_enabled: bool, item_index: int = 0, track_type: str = "video", track_index: int = 1) -> Dict[str, Any]:
    """Enable or disable a node.

    Args:
        node_index: 1-based node index.
        is_enabled: True to enable, False to disable.
        item_index: 0-based timeline item index. Default: 0.
        track_type: 'video' or 'audio'. Default: 'video'.
        track_index: 1-based track index. Default: 1.
    """
    item, err = _get_timeline_item(track_type, track_index, item_index)
    if err:
        return err
    graph = item.GetNodeGraph()
    if not graph:
        return {"error": "No node graph available"}
    result = graph.SetNodeEnabled(node_index, is_enabled)
    return {"success": bool(result)}

@mcp.tool()
def graph_apply_grade_from_drx(drx_path: str, grade_mode: int = 0, item_index: int = 0, track_type: str = "video", track_index: int = 1) -> Dict[str, Any]:
    """Apply a grade from a .drx file to a timeline item's graph.

    Args:
        drx_path: Absolute path to the .drx file.
        grade_mode: 0=No keyframes, 1=Source Timecode aligned, 2=Start Frames aligned.
        item_index: 0-based timeline item index. Default: 0.
        track_type: 'video' or 'audio'. Default: 'video'.
        track_index: 1-based track index. Default: 1.
    """
    item, err = _get_timeline_item(track_type, track_index, item_index)
    if err:
        return err
    graph = item.GetNodeGraph()
    if not graph:
        return {"error": "No node graph available"}
    result = graph.ApplyGradeFromDRX(drx_path, grade_mode)
    return {"success": bool(result)}

@mcp.tool()
def graph_apply_arri_cdl_lut(item_index: int = 0, track_type: str = "video", track_index: int = 1) -> Dict[str, Any]:
    """Apply ARRI CDL and LUT to a timeline item's graph.

    Args:
        item_index: 0-based timeline item index. Default: 0.
        track_type: 'video' or 'audio'. Default: 'video'.
        track_index: 1-based track index. Default: 1.
    """
    item, err = _get_timeline_item(track_type, track_index, item_index)
    if err:
        return err
    graph = item.GetNodeGraph()
    if not graph:
        return {"error": "No node graph available"}
    result = graph.ApplyArriCdlLut()
    return {"success": bool(result)}

@mcp.tool()
def graph_reset_all_grades(item_index: int = 0, track_type: str = "video", track_index: int = 1) -> Dict[str, Any]:
    """Reset all grades on a timeline item's graph.

    Args:
        item_index: 0-based timeline item index. Default: 0.
        track_type: 'video' or 'audio'. Default: 'video'.
        track_index: 1-based track index. Default: 1.
    """
    item, err = _get_timeline_item(track_type, track_index, item_index)
    if err:
        return err
    graph = item.GetNodeGraph()
    if not graph:
        return {"error": "No node graph available"}
    result = graph.ResetAllGrades()
    return {"success": bool(result)}


# ------------------
# ColorGroup Tools
# ------------------

