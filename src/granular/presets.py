#!/usr/bin/env python3
"""DaVinci Resolve MCP - Presets Operations (Granular Tools)."""

from typing import Any, Dict, List, Optional, Union, Tuple
from .common import mcp, get_resolve

@mcp.tool()
def save_color_preset(clip_name: str = None, preset_name: str = None, album_name: str = "DaVinci Resolve") -> str:
    """Save a color preset from the specified clip.
    
    Args:
        clip_name: Name of the clip to save preset from (uses current clip if None)
        preset_name: Name to give the preset (uses clip name if None)
        album_name: Album to save the preset to (default: "DaVinci Resolve")
    """
    pm, current_project = get_current_project()
    if not current_project:
        return "Error: No project currently open"
    
    # Switch to color page
    current_page = resolve.GetCurrentPage()
    if current_page != "color":
        resolve.OpenPage("color")
    
    try:
        # Get the current timeline
        current_timeline = current_project.GetCurrentTimeline()
        if not current_timeline:
            return "Error: No timeline is currently open"
        
        # Get the specific clip or current clip
        if clip_name:
            # Find the clip by name in the timeline
            timeline_clips = current_timeline.GetItemListInTrack("video", 1)
            target_clip = None
            
            for clip in timeline_clips:
                if clip.GetName() == clip_name:
                    target_clip = clip
                    break
            
            if not target_clip:
                return f"Error: Clip '{clip_name}' not found in the timeline"
            
            # Select the clip
            current_timeline.SetCurrentSelectedItem(target_clip)
        
        # Get gallery
        gallery = current_project.GetGallery()
        if not gallery:
            return "Error: Failed to get gallery"
        
        # Get or create album
        album = None
        albums = gallery.GetAlbums()
        
        if albums:
            for a in albums:
                if a.GetName() == album_name:
                    album = a
                    break
        
        if not album:
            # Create a new album if it doesn't exist
            album = gallery.CreateAlbum(album_name)
            if not album:
                return f"Error: Failed to create album '{album_name}'"
        
        # Set preset name if specified
        final_preset_name = preset_name
        if not final_preset_name:
            if clip_name:
                final_preset_name = f"{clip_name} Preset"
            else:
                # Get current clip name if available
                current_clip = current_timeline.GetCurrentVideoItem()
                if current_clip:
                    final_preset_name = f"{current_clip.GetName()} Preset"
                else:
                    final_preset_name = f"Preset {len(album.GetStills()) + 1}"
        
        # Capture still
        result = gallery.GrabStill()
        
        if not result:
            return "Error: Failed to grab still for the preset"
        
        # Get the still that was just created
        stills = album.GetStills()
        if stills:
            latest_still = stills[-1]  # Assume the last one is the one we just grabbed
            # Set the label
            latest_still.SetLabel(final_preset_name)
        
        # Return to the original page if we switched
        if current_page != "color":
            resolve.OpenPage(current_page)
        
        return f"Successfully saved color preset '{final_preset_name}' to album '{album_name}'"
    
    except Exception as e:
        # Return to the original page if we switched
        if current_page != "color":
            resolve.OpenPage(current_page)
        return f"Error saving color preset: {str(e)}"

@mcp.tool()
def apply_color_preset(preset_id: str = None, preset_name: str = None, 
                     clip_name: str = None, album_name: str = "DaVinci Resolve") -> str:
    """Apply a color preset to the specified clip.
    
    Args:
        preset_id: ID of the preset to apply (if known)
        preset_name: Name of the preset to apply (searches in album)
        clip_name: Name of the clip to apply preset to (uses current clip if None)
        album_name: Album containing the preset (default: "DaVinci Resolve")
    """
    resolve = get_resolve()
    if resolve is None:
        return "Error: Not connected to DaVinci Resolve"
    
    if not preset_id and not preset_name:
        return "Error: Must provide either preset_id or preset_name"
    
    project_manager = resolve.GetProjectManager()
    if not project_manager:
        return "Error: Failed to get Project Manager"
    
    current_project = project_manager.GetCurrentProject()
    if not current_project:
        return "Error: No project currently open"
    
    # Switch to color page
    current_page = resolve.GetCurrentPage()
    if current_page != "color":
        resolve.OpenPage("color")
    
    try:
        # Get the current timeline
        current_timeline = current_project.GetCurrentTimeline()
        if not current_timeline:
            return "Error: No timeline is currently open"
        
        # Get the specific clip or current clip
        if clip_name:
            # Find the clip by name in the timeline
            timeline_clips = current_timeline.GetItemListInTrack("video", 1)
            target_clip = None
            
            for clip in timeline_clips:
                if clip.GetName() == clip_name:
                    target_clip = clip
                    break
            
            if not target_clip:
                return f"Error: Clip '{clip_name}' not found in the timeline"
            
            # Select the clip
            current_timeline.SetCurrentSelectedItem(target_clip)
        
        # Get gallery
        gallery = current_project.GetGallery()
        if not gallery:
            return "Error: Failed to get gallery"
        
        # Find the album
        album = None
        albums = gallery.GetAlbums()
        
        if albums:
            for a in albums:
                if a.GetName() == album_name:
                    album = a
                    break
        
        if not album:
            return f"Error: Album '{album_name}' not found"
        
        # Find the still to apply
        stills = album.GetStills()
        if not stills:
            return f"Error: No presets found in album '{album_name}'"
        
        target_still = None
        
        if preset_id:
            # Find by ID
            for still in stills:
                if still.GetUniqueId() == preset_id:
                    target_still = still
                    break
        elif preset_name:
            # Find by name
            for still in stills:
                if still.GetLabel() == preset_name:
                    target_still = still
                    break
        
        if not target_still:
            search_term = preset_id if preset_id else preset_name
            return f"Error: Preset '{search_term}' not found in album '{album_name}'"
        
        # Apply the preset
        result = target_still.ApplyToClip()
        
        # Return to the original page if we switched
        if current_page != "color":
            resolve.OpenPage(current_page)
        
        if result:
            return f"Successfully applied color preset to {'specified clip' if clip_name else 'current clip'}"
        else:
            return f"Failed to apply color preset"
    
    except Exception as e:
        # Return to the original page if we switched
        if current_page != "color":
            resolve.OpenPage(current_page)
        return f"Error applying color preset: {str(e)}"

@mcp.tool()
def delete_color_preset(preset_id: str = None, preset_name: str = None, 
                       album_name: str = "DaVinci Resolve") -> str:
    """Delete a color preset.
    
    Args:
        preset_id: ID of the preset to delete (if known)
        preset_name: Name of the preset to delete (searches in album)
        album_name: Album containing the preset (default: "DaVinci Resolve")
    """
    resolve = get_resolve()
    if resolve is None:
        return "Error: Not connected to DaVinci Resolve"
    
    if not preset_id and not preset_name:
        return "Error: Must provide either preset_id or preset_name"
    
    project_manager = resolve.GetProjectManager()
    if not project_manager:
        return "Error: Failed to get Project Manager"
    
    current_project = project_manager.GetCurrentProject()
    if not current_project:
        return "Error: No project currently open"
    
    # Switch to color page
    current_page = resolve.GetCurrentPage()
    if current_page != "color":
        resolve.OpenPage("color")
    
    try:
        # Get gallery
        gallery = current_project.GetGallery()
        if not gallery:
            return "Error: Failed to get gallery"
        
        # Find the album
        album = None
        albums = gallery.GetAlbums()
        
        if albums:
            for a in albums:
                if a.GetName() == album_name:
                    album = a
                    break
        
        if not album:
            return f"Error: Album '{album_name}' not found"
        
        # Find the still to delete
        stills = album.GetStills()
        if not stills:
            return f"Error: No presets found in album '{album_name}'"
        
        target_still = None
        
        if preset_id:
            # Find by ID
            for still in stills:
                if still.GetUniqueId() == preset_id:
                    target_still = still
                    break
        elif preset_name:
            # Find by name
            for still in stills:
                if still.GetLabel() == preset_name:
                    target_still = still
                    break
        
        if not target_still:
            search_term = preset_id if preset_id else preset_name
            return f"Error: Preset '{search_term}' not found in album '{album_name}'"
        
        # Delete the preset
        result = album.DeleteStill(target_still)
        
        # Return to the original page if we switched
        if current_page != "color":
            resolve.OpenPage(current_page)
        
        if result:
            return f"Successfully deleted color preset from album '{album_name}'"
        else:
            return f"Failed to delete color preset"
    
    except Exception as e:
        # Return to the original page if we switched
        if current_page != "color":
            resolve.OpenPage(current_page)
        return f"Error deleting color preset: {str(e)}"

@mcp.tool()
def create_color_preset_album(album_name: str) -> str:
    """Create a new album for color presets.
    
    Args:
        album_name: Name for the new album
    """
    pm, current_project = get_current_project()
    if not current_project:
        return "Error: No project currently open"
    
    # Switch to color page
    current_page = resolve.GetCurrentPage()
    if current_page != "color":
        resolve.OpenPage("color")
    
    try:
        # Get gallery
        gallery = current_project.GetGallery()
        if not gallery:
            return "Error: Failed to get gallery"
        
        # Check if album already exists
        albums = gallery.GetAlbums()
        
        if albums:
            for a in albums:
                if a.GetName() == album_name:
                    # Return to the original page if we switched
                    if current_page != "color":
                        resolve.OpenPage(current_page)
                    return f"Album '{album_name}' already exists"
        
        # Create a new album
        album = gallery.CreateAlbum(album_name)
        
        # Return to the original page if we switched
        if current_page != "color":
            resolve.OpenPage(current_page)
        
        if album:
            return f"Successfully created album '{album_name}'"
        else:
            return f"Failed to create album '{album_name}'"
    
    except Exception as e:
        # Return to the original page if we switched
        if current_page != "color":
            resolve.OpenPage(current_page)
        return f"Error creating album: {str(e)}"

@mcp.tool()
def delete_color_preset_album(album_name: str) -> str:
    """Delete a color preset album.
    
    Args:
        album_name: Name of the album to delete
    """
    pm, current_project = get_current_project()
    if not current_project:
        return "Error: No project currently open"
    
    # Switch to color page
    current_page = resolve.GetCurrentPage()
    if current_page != "color":
        resolve.OpenPage("color")
    
    try:
        # Get gallery
        gallery = current_project.GetGallery()
        if not gallery:
            return "Error: Failed to get gallery"
        
        # Find the album
        album = None
        albums = gallery.GetAlbums()
        
        if albums:
            for a in albums:
                if a.GetName() == album_name:
                    album = a
                    break
        
        if not album:
            # Return to the original page if we switched
            if current_page != "color":
                resolve.OpenPage(current_page)
            return f"Error: Album '{album_name}' not found"
        
        # Delete the album
        result = gallery.DeleteAlbum(album)
        
        # Return to the original page if we switched
        if current_page != "color":
            resolve.OpenPage(current_page)
        
        if result:
            return f"Successfully deleted album '{album_name}'"
        else:
            return f"Failed to delete album '{album_name}'"
    
    except Exception as e:
        # Return to the original page if we switched
        if current_page != "color":
            resolve.OpenPage(current_page)
        return f"Error deleting album: {str(e)}"

@mcp.tool()
def export_lut(clip_name: str = None, 
              export_path: str = None, 
              lut_format: str = "Cube", 
              lut_size: str = "33Point") -> str:
    """Export a LUT from the current clip's grade.
    
    Args:
        clip_name: Name of the clip to export grade from (uses current clip if None)
        export_path: Path to save the LUT file (generated if None)
        lut_format: Format of the LUT. Options: 'Cube', 'Davinci', '3dl', 'Panasonic'
        lut_size: Size of the LUT. Options: '17Point', '33Point', '65Point'
    """
    pm, current_project = get_current_project()
    if not current_project:
        return "Error: No project currently open"
    
    # Switch to color page
    current_page = resolve.GetCurrentPage()
    if current_page != "color":
        resolve.OpenPage("color")
    
    try:
        # Get the current timeline
        current_timeline = current_project.GetCurrentTimeline()
        if not current_timeline:
            return "Error: No timeline is currently open"
        
        # Get the specific clip or current clip
        if clip_name:
            # Find the clip by name in the timeline
            timeline_clips = current_timeline.GetItemListInTrack("video", 1)
            target_clip = None
            
            for clip in timeline_clips:
                if clip.GetName() == clip_name:
                    target_clip = clip
                    break
            
            if not target_clip:
                return f"Error: Clip '{clip_name}' not found in the timeline"
            
            # Select the clip
            current_timeline.SetCurrentSelectedItem(target_clip)
        
        # Generate export path if not provided
        if not export_path:
            import tempfile
            clip_name_safe = clip_name if clip_name else "current_clip"
            clip_name_safe = clip_name_safe.replace(' ', '_').replace(':', '-')
            
            extension = ".cube"
            if lut_format.lower() == "davinci":
                extension = ".ilut"
            elif lut_format.lower() == "3dl":
                extension = ".3dl"
            elif lut_format.lower() == "panasonic":
                extension = ".vlut"
                
            export_path = os.path.join(tempfile.gettempdir(), f"{clip_name_safe}_lut{extension}")
        
        # Validate LUT format
        valid_formats = ['Cube', 'Davinci', '3dl', 'Panasonic']
        if lut_format not in valid_formats:
            return f"Error: Invalid LUT format. Must be one of: {', '.join(valid_formats)}"
        
        # Validate LUT size
        valid_sizes = ['17Point', '33Point', '65Point']
        if lut_size not in valid_sizes:
            return f"Error: Invalid LUT size. Must be one of: {', '.join(valid_sizes)}"
        
        # Map format string to numeric value expected by DaVinci Resolve API
        format_map = {
            'Cube': 0,
            'Davinci': 1,
            '3dl': 2,
            'Panasonic': 3
        }
        
        # Map size string to numeric value
        size_map = {
            '17Point': 0,
            '33Point': 1,
            '65Point': 2
        }
        
        # Get current clip
        current_clip = current_timeline.GetCurrentVideoItem()
        if not current_clip:
            return "Error: No clip is currently selected"
        
        # Create a directory for the export path if it doesn't exist
        export_dir = os.path.dirname(export_path)
        if export_dir and not os.path.exists(export_dir):
            os.makedirs(export_dir, exist_ok=True)
        
        # Export the LUT
        colorpage = resolve.GetCurrentPage() == "color"
        if not colorpage:
            resolve.OpenPage("color")
        
        # Access Color page functionality 
        result = current_project.ExportCurrentGradeAsLUT(
            format_map[lut_format], 
            size_map[lut_size], 
            export_path
        )
        
        # Return to the original page if we switched
        if current_page != "color":
            resolve.OpenPage(current_page)
        
        if result:
            return f"Successfully exported LUT to '{export_path}' in {lut_format} format with {lut_size} size"
        else:
            return f"Failed to export LUT"
    
    except Exception as e:
        # Return to the original page if we switched
        if current_page != "color":
            resolve.OpenPage(current_page)
        return f"Error exporting LUT: {str(e)}"

@mcp.resource("resolve://color/lut-formats")
def get_lut_formats() -> Dict[str, Any]:
    """Get available LUT export formats and sizes."""
    formats = {
        "formats": [
            {
                "name": "Cube",
                "extension": ".cube",
                "description": "Industry standard LUT format supported by most applications"
            },
            {
                "name": "Davinci",
                "extension": ".ilut",
                "description": "DaVinci Resolve's native LUT format"
            },
            {
                "name": "3dl",
                "extension": ".3dl",
                "description": "ASSIMILATE SCRATCH and some Autodesk applications"
            },
            {
                "name": "Panasonic",
                "extension": ".vlut",
                "description": "Panasonic VariCam and other Panasonic cameras"
            }
        ],
        "sizes": [
            {
                "name": "17Point",
                "description": "Smaller file size, less precision (17x17x17)"
            },
            {
                "name": "33Point",
                "description": "Standard size with good balance of precision and file size (33x33x33)"
            },
            {
                "name": "65Point",
                "description": "Highest precision but larger file size (65x65x65)"
            }
        ]
    }
    return formats

@mcp.tool()
def export_all_powergrade_luts(export_dir: str) -> str:
    """Export all PowerGrade presets as LUT files.
    
    Args:
        export_dir: Directory to save the exported LUTs
    """
    pm, current_project = get_current_project()
    if not current_project:
        return "Error: No project currently open"
    
    # Switch to color page
    current_page = resolve.GetCurrentPage()
    if current_page != "color":
        resolve.OpenPage("color")
    
    try:
        # Get gallery
        gallery = current_project.GetGallery()
        if not gallery:
            return "Error: Failed to get gallery"
        
        # Get PowerGrade album
        powergrade_album = None
        albums = gallery.GetAlbums()
        
        if albums:
            for album in albums:
                if album.GetName() == "PowerGrade":
                    powergrade_album = album
                    break
        
        if not powergrade_album:
            return "Error: PowerGrade album not found"
        
        # Get all stills in the PowerGrade album
        stills = powergrade_album.GetStills()
        if not stills:
            return "Error: No stills found in PowerGrade album"
        
        # Create export directory if it doesn't exist
        if not os.path.exists(export_dir):
            os.makedirs(export_dir, exist_ok=True)
        
        # Export each still as a LUT
        exported_count = 0
        failed_stills = []
        
        for still in stills:
            still_name = still.GetLabel()
            if not still_name:
                still_name = f"PowerGrade_{still.GetUniqueId()}"
            
            # Create safe filename
            safe_name = ''.join(c if c.isalnum() or c in ['-', '_'] else '_' for c in still_name)
            lut_path = os.path.join(export_dir, f"{safe_name}.cube")
            
            # Apply the still to the current clip
            current_clip = current_timeline.GetCurrentVideoItem()
            if not current_clip:
                failed_stills.append(f"{still_name} (no clip selected)")
                continue
            
            # Apply the grade from the still
            applied = still.ApplyToClip()
            if not applied:
                failed_stills.append(f"{still_name} (could not apply grade)")
                continue
            
            # Export as LUT
            result = current_project.ExportCurrentGradeAsLUT(0, 1, lut_path)  # Cube format, 33-point
            
            if result:
                exported_count += 1
            else:
                failed_stills.append(f"{still_name} (export failed)")
        
        # Return to the original page if we switched
        if current_page != "color":
            resolve.OpenPage(current_page)
        
        if failed_stills:
            return f"Exported {exported_count} LUTs to '{export_dir}'. Failed to export: {', '.join(failed_stills)}"
        else:
            return f"Successfully exported all {exported_count} PowerGrade LUTs to '{export_dir}'"
    
    except Exception as e:
        # Return to the original page if we switched
        if current_page != "color":
            resolve.OpenPage(current_page)
        return f"Error exporting PowerGrade LUTs: {str(e)}"

# ------------------
# Object Inspection
# ------------------

@mcp.resource("resolve://inspect/resolve")
def inspect_resolve_object() -> Dict[str, Any]:
    """Inspect the main resolve object and return its methods and properties."""
    resolve = get_resolve()
    if resolve is None:
        return {"error": "Not connected to DaVinci Resolve"}
    
    return inspect_object(resolve)

@mcp.resource("resolve://inspect/project-manager")
def inspect_project_manager_object() -> Dict[str, Any]:
    """Inspect the project manager object and return its methods and properties."""
    project_manager = get_project_manager()
    if not project_manager:
        return {"error": "Failed to get Project Manager"}
    
    return inspect_object(project_manager)

@mcp.resource("resolve://inspect/current-project")
def inspect_current_project_object() -> Dict[str, Any]:
    """Inspect the current project object and return its methods and properties."""
    pm, current_project = get_current_project()
    if not current_project:
        return {"error": "No project currently open"}
    
    return inspect_object(current_project)

@mcp.resource("resolve://inspect/media-pool")
def inspect_media_pool_object() -> Dict[str, Any]:
    """Inspect the media pool object and return its methods and properties."""
    pm, current_project = get_current_project()
    if not current_project:
        return {"error": "No project currently open"}
    
    media_pool = current_project.GetMediaPool()
    if not media_pool:
        return {"error": "Failed to get Media Pool"}
    
    return inspect_object(media_pool)

@mcp.resource("resolve://inspect/current-timeline")
def inspect_current_timeline_object() -> Dict[str, Any]:
    """Inspect the current timeline object and return its methods and properties."""
    pm, current_project = get_current_project()
    if not current_project:
        return {"error": "No project currently open"}
    
    current_timeline = current_project.GetCurrentTimeline()
    if not current_timeline:
        return {"error": "No timeline currently active"}
    
    return inspect_object(current_timeline)

@mcp.tool()
def import_burn_in_preset(preset_path: str) -> Dict[str, Any]:
    """Import a burn-in preset from a file.

    Args:
        preset_path: Absolute path to the burn-in preset file.
    """
    resolve = get_resolve()
    if resolve is None:
        return {"error": "Not connected to DaVinci Resolve"}
    result = resolve.ImportBurnInPreset(preset_path)
    return {"success": bool(result), "preset_path": preset_path}

@mcp.tool()
def export_burn_in_preset(preset_name: str, export_path: str) -> Dict[str, Any]:
    """Export a burn-in preset to a file.

    Args:
        preset_name: Name of the burn-in preset to export.
        export_path: Absolute path where the preset file will be saved.
    """
    resolve = get_resolve()
    if resolve is None:
        return {"error": "Not connected to DaVinci Resolve"}
    result = resolve.ExportBurnInPreset(preset_name, export_path)
    return {"success": bool(result), "preset_name": preset_name, "export_path": export_path}

@mcp.tool()
def refresh_lut_list() -> Dict[str, Any]:
    """Refresh the LUT list in the project. Call after adding new LUT files."""
    resolve = get_resolve()
    if resolve is None:
        return {"error": "Not connected to DaVinci Resolve"}
    project = resolve.GetProjectManager().GetCurrentProject()
    if not project:
        return {"error": "No project currently open"}
    result = project.RefreshLUTList()
    return {"success": bool(result)}

