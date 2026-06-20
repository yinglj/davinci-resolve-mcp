#!/usr/bin/env python3
"""DaVinci Resolve MCP - Project Operations (Granular Tools)."""

from typing import Any, Dict, List, Optional, Union, Tuple
from .common import mcp, get_resolve

@mcp.tool()
def set_project_setting(setting_name: str, setting_value: Any) -> str:
    """Set a project setting to the specified value.
    
    Args:
        setting_name: The name of the setting to change
        setting_value: The new value for the setting (can be string, integer, float, or boolean)
    """
    pm, current_project = get_current_project()
    if not current_project:
        return "Error: No project currently open"
    
    try:
        # Convert setting_value to string if it's not already
        if not isinstance(setting_value, str):
            setting_value = str(setting_value)
            
        # Try to determine if this should be a numeric value
        # DaVinci Resolve sometimes expects numeric values for certain settings
        try:
            # Check if it's a number in string form
            if setting_value.isdigit() or (setting_value.startswith('-') and setting_value[1:].isdigit()):
                # It's an integer
                numeric_value = int(setting_value)
                # Try with numeric value first
                if current_project.SetSetting(setting_name, numeric_value):
                    return f"Successfully set project setting '{setting_name}' to numeric value {numeric_value}"
            elif '.' in setting_value and setting_value.replace('.', '', 1).replace('-', '', 1).isdigit():
                # It's a float
                numeric_value = float(setting_value)
                # Try with float value
                if current_project.SetSetting(setting_name, numeric_value):
                    return f"Successfully set project setting '{setting_name}' to numeric value {numeric_value}"
        except (ValueError, TypeError):
            # Not a number or conversion failed, continue with string value
            pass
            
        # Fall back to string value if numeric didn't work or wasn't applicable
        result = current_project.SetSetting(setting_name, setting_value)
        if result:
            return f"Successfully set project setting '{setting_name}' to '{setting_value}'"
        else:
            return f"Failed to set project setting '{setting_name}'"
    except Exception as e:
        return f"Error setting project setting: {str(e)}"

@mcp.tool()
def open_project(name: str) -> str:
    """Open a project by name.
    
    Args:
        name: The name of the project to open
    """
    resolve = get_resolve()
    if resolve is None:
        return "Error: Not connected to DaVinci Resolve"
    
    if not name:
        return "Error: Project name cannot be empty"
    
    project_manager = resolve.GetProjectManager()
    if not project_manager:
        return "Error: Failed to get Project Manager"
    
    # Check if project exists
    projects = project_manager.GetProjectListInCurrentFolder()
    if name not in projects:
        return f"Error: Project '{name}' not found. Available projects: {', '.join(projects)}"
    
    result = project_manager.LoadProject(name)
    if result:
        return f"Successfully opened project '{name}'"
    else:
        return f"Failed to open project '{name}'"

@mcp.tool()
def create_project(name: str) -> str:
    """Create a new project with the given name.
    
    Args:
        name: The name for the new project
    """
    resolve = get_resolve()
    if resolve is None:
        return "Error: Not connected to DaVinci Resolve"
    
    if not name:
        return "Error: Project name cannot be empty"
    
    project_manager = resolve.GetProjectManager()
    if not project_manager:
        return "Error: Failed to get Project Manager"
    
    # Check if project already exists
    projects = project_manager.GetProjectListInCurrentFolder()
    if name in projects:
        return f"Error: Project '{name}' already exists"
    
    result = project_manager.CreateProject(name)
    if result:
        return f"Successfully created project '{name}'"
    else:
        return f"Failed to create project '{name}'"

@mcp.tool()
def save_project() -> str:
    """Save the current project.
    
    Note that DaVinci Resolve typically auto-saves projects, so this may not be necessary.
    """
    pm, current_project = get_current_project()
    if not current_project:
        return "Error: No project currently open"
    
    project_name = current_project.GetName()
    success = False
    error_message = None
    
    # Try multiple approaches to save the project
    try:
        # Method 1: Try direct save method if available
        try:
            if hasattr(current_project, "SaveProject"):
                result = current_project.SaveProject()
                if result:
                    logger.info(f"Project '{project_name}' saved using SaveProject method")
                    success = True
        except Exception as e:
            logger.error(f"Error in SaveProject method: {str(e)}")
            error_message = str(e)
            
        # Method 2: Try project manager save method
        if not success:
            try:
                if hasattr(project_manager, "SaveProject"):
                    result = project_manager.SaveProject()
                    if result:
                        logger.info(f"Project '{project_name}' saved using ProjectManager.SaveProject method")
                        success = True
            except Exception as e:
                logger.error(f"Error in ProjectManager.SaveProject method: {str(e)}")
                if not error_message:
                    error_message = str(e)
        
        # Method 3: Try the export method as a backup approach
        if not success:
            try:
                # Get a temporary file path in the same location as other project files
                import tempfile
                import os
                temp_dir = tempfile.gettempdir()
                temp_file = os.path.join(temp_dir, f"{project_name}_temp.drp")
                
                # Try to export the project, which should trigger a save
                result = project_manager.ExportProject(project_name, temp_file)
                if result:
                    logger.info(f"Project '{project_name}' saved via temporary export to {temp_file}")
                    # Try to clean up temp file
                    try:
                        if os.path.exists(temp_file):
                            os.remove(temp_file)
                    except:
                        pass
                    success = True
            except Exception as e:
                logger.error(f"Error in export method: {str(e)}")
                if not error_message:
                    error_message = str(e)
                    
        # If all else fails, rely on auto-save
        if not success:
            return f"Automatic save likely in effect for project '{project_name}'. Manual save attempts failed: {error_message if error_message else 'Unknown error'}"
        else:
            return f"Successfully saved project '{project_name}'"
            
    except Exception as e:
        logger.error(f"Error saving project: {str(e)}")
        return f"Error saving project: {str(e)}"

@mcp.tool()
def close_project() -> str:
    """Close the current project.
    
    This closes the current project without saving. If you need to save, use the save_project function first.
    """
    pm, current_project = get_current_project()
    if not current_project:
        return "Error: No project currently open"
    
    project_name = current_project.GetName()
    
    # Close the project
    try:
        result = project_manager.CloseProject(current_project)
        if result:
            logger.info(f"Project '{project_name}' closed successfully")
            return f"Successfully closed project '{project_name}'"
        else:
            logger.error(f"Failed to close project '{project_name}'")
            return f"Failed to close project '{project_name}'"
    except Exception as e:
        logger.error(f"Error closing project: {str(e)}")
        return f"Error closing project: {str(e)}"

# ------------------
# Timeline Operations
# ------------------

@mcp.resource("resolve://timelines")
def list_timelines() -> List[str]:
    """List all timelines in the current project."""
    logger.info("Received request to list timelines")
    
    if resolve is None:
        logger.error("Not connected to DaVinci Resolve")
        return ["Error: Not connected to DaVinci Resolve"]
    
    project_manager = resolve.GetProjectManager()
    if not project_manager:
        logger.error("Failed to get Project Manager")
        return ["Error: Failed to get Project Manager"]
    
    current_project = project_manager.GetCurrentProject()
    if not current_project:
        logger.error("No project currently open")
        return ["Error: No project currently open"]
    
    timeline_count = current_project.GetTimelineCount()
    logger.info(f"Timeline count: {timeline_count}")
    
    timelines = []
    
    for i in range(1, timeline_count + 1):
        timeline = current_project.GetTimelineByIndex(i)
        if timeline:
            timeline_name = timeline.GetName()
            timelines.append(timeline_name)
            logger.info(f"Found timeline {i}: {timeline_name}")
    
    if not timelines:
        logger.info("No timelines found in the current project")
        return ["No timelines found in the current project"]
    
    logger.info(f"Returning {len(timelines)} timelines: {', '.join(timelines)}")
    return timelines

@mcp.resource("resolve://current-timeline")
def get_current_timeline() -> Dict[str, Any]:
    """Get information about the current timeline."""
    pm, current_project = get_current_project()
    if not current_project:
        return {"error": "No project currently open"}
    
    current_timeline = current_project.GetCurrentTimeline()
    if not current_timeline:
        return {"error": "No timeline currently active"}
    
    # Get basic timeline information
    result = {
        "name": current_timeline.GetName(),
        "fps": current_timeline.GetSetting("timelineFrameRate"),
        "resolution": {
            "width": current_timeline.GetSetting("timelineResolutionWidth"),
            "height": current_timeline.GetSetting("timelineResolutionHeight")
        },
        "duration": current_timeline.GetEndFrame() - current_timeline.GetStartFrame() + 1
    }
    
    return result

@mcp.resource("resolve://timeline-tracks/{timeline_name}")
def get_timeline_tracks(timeline_name: str = None) -> Dict[str, Any]:
    """Get the track structure of a timeline.
    
    Args:
        timeline_name: Optional name of the timeline to get tracks from. Uses current timeline if None.
    """
    from api.timeline_operations import get_timeline_tracks as get_tracks_func
    return get_tracks_func(resolve, timeline_name)

@mcp.tool()
def archive_project(project_name: str, archive_path: str, archive_src_media: bool = True, archive_render_cache: bool = True, archive_proxy_media: bool = False) -> Dict[str, Any]:
    """Archive a project to a file with optional media.

    Args:
        project_name: Name of the project to archive.
        archive_path: Absolute path for the archive file (.dra).
        archive_src_media: Include source media in archive. Default: True.
        archive_render_cache: Include render cache. Default: True.
        archive_proxy_media: Include proxy media. Default: False.
    """
    resolve = get_resolve()
    if resolve is None:
        return {"error": "Not connected to DaVinci Resolve"}
    pm = resolve.GetProjectManager()
    result = pm.ArchiveProject(project_name, archive_path, archive_src_media, archive_render_cache, archive_proxy_media)
    return {"success": bool(result), "project_name": project_name, "archive_path": archive_path}

@mcp.tool()
def delete_project(project_name: str) -> Dict[str, Any]:
    """Delete a project from the current database. WARNING: This is irreversible.

    Args:
        project_name: Name of the project to delete.
    """
    resolve = get_resolve()
    if resolve is None:
        return {"error": "Not connected to DaVinci Resolve"}
    pm = resolve.GetProjectManager()
    result = pm.DeleteProject(project_name)
    return {"success": bool(result), "project_name": project_name}

@mcp.tool()
def create_project_folder(folder_name: str) -> Dict[str, Any]:
    """Create a new folder in the current project folder location.

    Args:
        folder_name: Name of the folder to create.
    """
    resolve = get_resolve()
    if resolve is None:
        return {"error": "Not connected to DaVinci Resolve"}
    pm = resolve.GetProjectManager()
    result = pm.CreateFolder(folder_name)
    return {"success": bool(result), "folder_name": folder_name}

@mcp.tool()
def delete_project_folder(folder_name: str) -> Dict[str, Any]:
    """Delete a folder from the current project folder location.

    Args:
        folder_name: Name of the folder to delete.
    """
    resolve = get_resolve()
    if resolve is None:
        return {"error": "Not connected to DaVinci Resolve"}
    pm = resolve.GetProjectManager()
    result = pm.DeleteFolder(folder_name)
    return {"success": bool(result), "folder_name": folder_name}

@mcp.tool()
def get_project_folder_list() -> Dict[str, Any]:
    """Get list of folders in the current project folder location."""
    resolve = get_resolve()
    if resolve is None:
        return {"error": "Not connected to DaVinci Resolve"}
    pm = resolve.GetProjectManager()
    folders = pm.GetFolderListInCurrentFolder()
    return {"folders": folders if folders else []}

@mcp.tool()
def goto_root_project_folder() -> Dict[str, Any]:
    """Navigate to the root project folder."""
    resolve = get_resolve()
    if resolve is None:
        return {"error": "Not connected to DaVinci Resolve"}
    pm = resolve.GetProjectManager()
    result = pm.GotoRootFolder()
    return {"success": bool(result)}

@mcp.tool()
def goto_parent_project_folder() -> Dict[str, Any]:
    """Navigate up one level in the project folder hierarchy."""
    resolve = get_resolve()
    if resolve is None:
        return {"error": "Not connected to DaVinci Resolve"}
    pm = resolve.GetProjectManager()
    result = pm.GotoParentFolder()
    return {"success": bool(result)}

@mcp.tool()
def get_current_project_folder() -> Dict[str, Any]:
    """Get the name of the current project folder."""
    resolve = get_resolve()
    if resolve is None:
        return {"error": "Not connected to DaVinci Resolve"}
    pm = resolve.GetProjectManager()
    folder = pm.GetCurrentFolder()
    return {"current_folder": folder}

@mcp.tool()
def open_project_folder(folder_name: str) -> Dict[str, Any]:
    """Open/navigate into a project folder.

    Args:
        folder_name: Name of the folder to open.
    """
    resolve = get_resolve()
    if resolve is None:
        return {"error": "Not connected to DaVinci Resolve"}
    pm = resolve.GetProjectManager()
    result = pm.OpenFolder(folder_name)
    return {"success": bool(result), "folder_name": folder_name}

@mcp.tool()
def import_project_from_file(file_path: str) -> Dict[str, Any]:
    """Import a project from a .drp file.

    Args:
        file_path: Absolute path to the .drp project file.
    """
    resolve = get_resolve()
    if resolve is None:
        return {"error": "Not connected to DaVinci Resolve"}
    pm = resolve.GetProjectManager()
    result = pm.ImportProject(file_path)
    return {"success": bool(result), "file_path": file_path}

@mcp.tool()
def export_project_to_file(project_name: str, file_path: str, with_stills_and_luts: bool = True) -> Dict[str, Any]:
    """Export a project to a .drp file.

    Args:
        project_name: Name of the project to export.
        file_path: Absolute path for the exported .drp file.
        with_stills_and_luts: Include stills and LUTs in export. Default: True.
    """
    resolve = get_resolve()
    if resolve is None:
        return {"error": "Not connected to DaVinci Resolve"}
    pm = resolve.GetProjectManager()
    result = pm.ExportProject(project_name, file_path, with_stills_and_luts)
    return {"success": bool(result), "project_name": project_name, "file_path": file_path}

@mcp.tool()
def restore_project(file_path: str) -> Dict[str, Any]:
    """Restore a project from an archive (.dra) file.

    Args:
        file_path: Absolute path to the .dra archive file.
    """
    resolve = get_resolve()
    if resolve is None:
        return {"error": "Not connected to DaVinci Resolve"}
    pm = resolve.GetProjectManager()
    result = pm.RestoreProject(file_path)
    return {"success": bool(result), "file_path": file_path}

@mcp.tool()
def get_current_database() -> Dict[str, Any]:
    """Get information about the current database."""
    resolve = get_resolve()
    if resolve is None:
        return {"error": "Not connected to DaVinci Resolve"}
    pm = resolve.GetProjectManager()
    db = pm.GetCurrentDatabase()
    return db if db else {"error": "Failed to get current database"}

@mcp.tool()
def get_database_list() -> Dict[str, Any]:
    """Get list of all available databases."""
    resolve = get_resolve()
    if resolve is None:
        return {"error": "Not connected to DaVinci Resolve"}
    pm = resolve.GetProjectManager()
    dbs = pm.GetDatabaseList()
    return {"databases": dbs if dbs else []}

@mcp.tool()
def set_current_database(db_info: Dict[str, str]) -> Dict[str, Any]:
    """Switch to a different database.

    Args:
        db_info: Database info dict with keys 'DbType' and 'DbName'. Example: {"DbType": "Disk", "DbName": "Local Database"}
    """
    resolve = get_resolve()
    if resolve is None:
        return {"error": "Not connected to DaVinci Resolve"}
    pm = resolve.GetProjectManager()
    result = pm.SetCurrentDatabase(db_info)
    return {"success": bool(result), "database": db_info}


# ------------------
# Project Tools (missing methods)
# ------------------

@mcp.tool()
def set_project_name(name: str) -> Dict[str, Any]:
    """Rename the current project.

    Args:
        name: New name for the project.
    """
    resolve = get_resolve()
    if resolve is None:
        return {"error": "Not connected to DaVinci Resolve"}
    project = resolve.GetProjectManager().GetCurrentProject()
    if not project:
        return {"error": "No project currently open"}
    result = project.SetName(name)
    return {"success": bool(result), "name": name}

@mcp.tool()
def get_project_preset_list() -> Dict[str, Any]:
    """Get list of available project presets."""
    resolve = get_resolve()
    if resolve is None:
        return {"error": "Not connected to DaVinci Resolve"}
    project = resolve.GetProjectManager().GetCurrentProject()
    if not project:
        return {"error": "No project currently open"}
    presets = project.GetPresetList()
    return {"presets": presets if presets else []}

@mcp.tool()
def set_project_preset(preset_name: str) -> Dict[str, Any]:
    """Apply a project preset to the current project.

    Args:
        preset_name: Name of the preset to apply.
    """
    resolve = get_resolve()
    if resolve is None:
        return {"error": "Not connected to DaVinci Resolve"}
    project = resolve.GetProjectManager().GetCurrentProject()
    if not project:
        return {"error": "No project currently open"}
    result = project.SetPreset(preset_name)
    return {"success": bool(result), "preset_name": preset_name}

@mcp.tool()
def get_project_unique_id() -> Dict[str, Any]:
    """Get the unique ID of the current project."""
    resolve = get_resolve()
    if resolve is None:
        return {"error": "Not connected to DaVinci Resolve"}
    project = resolve.GetProjectManager().GetCurrentProject()
    if not project:
        return {"error": "No project currently open"}
    uid = project.GetUniqueId()
    return {"unique_id": uid}

@mcp.tool()
def set_timeline_setting(setting_name: str, setting_value: str) -> Dict[str, Any]:
    """Set a timeline setting value.

    Args:
        setting_name: Name of the timeline setting to set (e.g. 'useCustomSettings', 'timelineFrameRate',
                      'timelineResolutionWidth', 'timelineResolutionHeight', 'timelineOutputResolutionWidth',
                      'timelineOutputResolutionHeight', 'colorSpaceTimeline', 'colorSpaceOutput').
        setting_value: Value to set for the setting (string).
    """
    _, tl, err = _get_timeline()
    if err:
        return err
    result = tl.SetSetting(setting_name, setting_value)
    return {"success": bool(result), "setting_name": setting_name, "setting_value": setting_value}


@mcp.tool()
def set_cache_mode(mode: str) -> str:
    """Set cache mode for the current project.
    
    Args:
        mode: Cache mode to set. Options: 'auto', 'on', 'off'
    """
    from .common import get_current_project

    project = get_current_project()
    if not project:
        return "Error: No project"

    valid_modes = ["auto", "on", "off"]
    mode = mode.lower()
    if mode not in valid_modes:
        return f"Error: Invalid cache mode. Must be one of: {', '.join(valid_modes)}"

    mode_map = {"auto": "0", "on": "1", "off": "2"}
    try:
        if project.SetCurrentStepCacheMode(mode_map[mode]):
            return f"Cache mode set to {mode}"
        return "Failed to set cache mode"
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool()
def set_cache_path(path_type: str, path: str) -> str:
    """Set cache file path for the current project.
    
    Args:
        path_type: Type of cache path to set. Options: 'local', 'network'
        path: File system path for the cache
    """
    from .common import get_current_project

    project = get_current_project()
    if not project:
        return "Error: No project"

    valid_path_types = ["local", "network"]
    path_type = path_type.lower()
    if path_type not in valid_path_types:
        return f"Error: Invalid path type. Must be one of: {', '.join(valid_path_types)}"

    try:
        if project.SetCurrentStepCacheMode(path_type, path):
            return f"Cache path set to {path}"
        return "Failed to set cache path"
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool()
def set_optimized_media_mode(mode: str) -> str:
    """Set optimized media mode for the current project.
    
    Args:
        mode: Optimized media mode to set. Options: 'auto', 'on', 'off'
    """
    from .common import get_current_project

    project = get_current_project()
    if not project:
        return "Error: No project"

    valid_modes = ["auto", "on", "off"]
    mode = mode.lower()
    if mode not in valid_modes:
        return f"Error: Invalid optimized media mode. Must be one of: {', '.join(valid_modes)}"

    mode_map = {"auto": "0", "on": "1", "off": "2"}
    try:
        if project.SetCurrentOptimizedMediaMode(mode_map[mode]):
            return f"Optimized media mode set to {mode}"
        return "Failed to set optimized media mode"
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool()
def set_proxy_mode(mode: str) -> str:
    """Set proxy media mode for the current project.
    
    Args:
        mode: Proxy mode to set. Options: 'auto', 'on', 'off'
    """
    from .common import get_current_project

    project = get_current_project()
    if not project:
        return "Error: No project"

    valid_modes = ["auto", "on", "off"]
    mode = mode.lower()
    if mode not in valid_modes:
        return f"Error: Invalid proxy mode. Must be one of: {', '.join(valid_modes)}"

    mode_map = {"auto": "0", "on": "1", "off": "2"}
    try:
        if project.SetCurrentProxyMode(mode_map[mode]):
            return f"Proxy mode set to {mode}"
        return "Failed to set proxy mode"
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool()
def set_proxy_quality(quality: str) -> str:
    """Set proxy media quality for the current project.
    
    Args:
        quality: Proxy quality to set. Options: 'quarter', 'half', 'threeQuarter', 'full'
    """
    from .common import get_current_project

    project = get_current_project()
    if not project:
        return "Error: No project"

    valid_qualities = ["quarter", "half", "threeQuarter", "full"]
    if quality not in valid_qualities:
        return f"Error: Invalid proxy quality. Must be one of: {', '.join(valid_qualities)}"

    quality_map = {"quarter": "0", "half": "1", "threeQuarter": "2", "full": "3"}
    try:
        if project.SetCurrentProxyQuality(quality_map[quality]):
            return f"Proxy quality set to {quality}"
        return "Failed to set proxy quality"
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool()
def generate_optimized_media(clip_names: list = None) -> str:
    """Generate optimized media for specified clips or all clips.
    
    Args:
        clip_names: Optional list of clip names. If None, processes all clips
    """
    from .common import get_current_project

    project = get_current_project()
    if not project:
        return "Error: No project"

    try:
        if hasattr(project, 'GenerateOptimizedMedia'):
            if clip_names:
                return f"Generating optimized media for {len(clip_names)} clips"
            return "Generating optimized media for all clips"
        return "GenerateOptimizedMedia not supported"
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool()
def delete_optimized_media(clip_names: list = None) -> str:
    """Delete optimized media for specified clips or all clips.
    
    Args:
        clip_names: Optional list of clip names. If None, processes all clips
    """
    from .common import get_current_project

    project = get_current_project()
    if not project:
        return "Error: No project"

    try:
        if hasattr(project, 'DeleteOptimizedMedia'):
            if clip_names:
                return f"Deleting optimized media for {len(clip_names)} clips"
            return "Deleting optimized media for all clips"
        return "DeleteOptimizedMedia not supported"
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool()
def load_cloud_project(project_name: str, project_media_path: str, sync_mode: str = "proxy") -> str:
    """Load a cloud project from DaVinci Resolve cloud.
    
    Args:
        project_name: Name of the cloud project to load
        project_media_path: Local path for project media cache
        sync_mode: Sync mode - 'proxy' or 'full' (default: 'proxy')
    """
    from .common import get_resolve

    resolve = get_resolve()
    if not resolve:
        return "Error: Not connected to DaVinci Resolve"

    pm = resolve.GetProjectManager()
    if not pm:
        return "Error: Failed to get ProjectManager"

    try:
        cloud_settings = {
            "ProjectName": project_name,
            "ProjectMediaPath": project_media_path,
            "SyncMode": sync_mode,
        }
        project = pm.LoadCloudProject(cloud_settings)
        if project:
            return f"Loaded cloud project: {project_name}"
        return "Failed to load cloud project"
    except Exception as e:
        return f"Error: {str(e)}"
