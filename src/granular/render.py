#!/usr/bin/env python3
"""DaVinci Resolve MCP - Render Operations (Granular Tools)."""

from typing import Any, Dict, List, Optional, Union, Tuple
from .common import mcp, get_resolve

@mcp.tool()
def add_to_render_queue(preset_name: str, timeline_name: str = None, use_in_out_range: bool = False) -> Dict[str, Any]:
    """Add a timeline to the render queue with the specified preset.
    
    Args:
        preset_name: Name of the render preset to use
        timeline_name: Name of the timeline to render (uses current if None)
        use_in_out_range: Whether to render only the in/out range instead of entire timeline
    """
    from api.delivery_operations import add_to_render_queue as add_queue_func
    return add_queue_func(resolve, preset_name, timeline_name, use_in_out_range)

@mcp.tool()
def start_render() -> Dict[str, Any]:
    """Start rendering the jobs in the render queue."""
    from api.delivery_operations import start_render as start_render_func
    return start_render_func(resolve)

@mcp.resource("resolve://delivery/render-queue/status")
def get_render_queue_status() -> Dict[str, Any]:
    """Get the status of jobs in the render queue."""
    from api.delivery_operations import get_render_queue_status as get_status_func
    return get_status_func(resolve)

@mcp.tool()
def clear_render_queue() -> Dict[str, Any]:
    """Clear all jobs from the render queue."""
    from api.delivery_operations import clear_render_queue as clear_queue_func
    return clear_queue_func(resolve)

@mcp.tool()
def import_render_preset(preset_path: str) -> Dict[str, Any]:
    """Import a render preset from a file.

    Args:
        preset_path: Absolute path to the render preset file.
    """
    resolve = get_resolve()
    if resolve is None:
        return {"error": "Not connected to DaVinci Resolve"}
    result = resolve.ImportRenderPreset(preset_path)
    return {"success": bool(result), "preset_path": preset_path}

@mcp.tool()
def export_render_preset(preset_name: str, export_path: str) -> Dict[str, Any]:
    """Export a render preset to a file.

    Args:
        preset_name: Name of the render preset to export.
        export_path: Absolute path where the preset file will be saved.
    """
    resolve = get_resolve()
    if resolve is None:
        return {"error": "Not connected to DaVinci Resolve"}
    result = resolve.ExportRenderPreset(preset_name, export_path)
    return {"success": bool(result), "preset_name": preset_name, "export_path": export_path}

@mcp.tool()
def delete_render_job(job_id: str) -> Dict[str, Any]:
    """Delete a specific render job by its ID.

    Args:
        job_id: The unique ID of the render job to delete.
    """
    resolve = get_resolve()
    if resolve is None:
        return {"error": "Not connected to DaVinci Resolve"}
    project = resolve.GetProjectManager().GetCurrentProject()
    if not project:
        return {"error": "No project currently open"}
    result = project.DeleteRenderJob(job_id)
    return {"success": bool(result), "job_id": job_id}

@mcp.tool()
def get_render_job_list() -> Dict[str, Any]:
    """Get list of all render jobs in the queue."""
    resolve = get_resolve()
    if resolve is None:
        return {"error": "Not connected to DaVinci Resolve"}
    project = resolve.GetProjectManager().GetCurrentProject()
    if not project:
        return {"error": "No project currently open"}
    jobs = project.GetRenderJobList()
    return {"render_jobs": jobs if jobs else []}

@mcp.tool()
def start_rendering_jobs(job_ids: Optional[List[str]] = None, is_interactive_mode: bool = False) -> Dict[str, Any]:
    """Start rendering jobs. If no job IDs specified, renders all queued jobs.

    Args:
        job_ids: Optional list of job IDs to render. If None, renders all.
        is_interactive_mode: If True, enables interactive rendering mode.
    """
    resolve = get_resolve()
    if resolve is None:
        return {"error": "Not connected to DaVinci Resolve"}
    project = resolve.GetProjectManager().GetCurrentProject()
    if not project:
        return {"error": "No project currently open"}
    if job_ids:
        result = project.StartRendering(job_ids, is_interactive_mode)
    else:
        result = project.StartRendering(is_interactive_mode)
    return {"success": bool(result)}

@mcp.tool()
def stop_rendering() -> Dict[str, Any]:
    """Stop the current rendering process."""
    resolve = get_resolve()
    if resolve is None:
        return {"error": "Not connected to DaVinci Resolve"}
    project = resolve.GetProjectManager().GetCurrentProject()
    if not project:
        return {"error": "No project currently open"}
    project.StopRendering()
    return {"success": True}

@mcp.tool()
def is_rendering_in_progress() -> Dict[str, Any]:
    """Check if rendering is currently in progress."""
    resolve = get_resolve()
    if resolve is None:
        return {"error": "Not connected to DaVinci Resolve"}
    project = resolve.GetProjectManager().GetCurrentProject()
    if not project:
        return {"error": "No project currently open"}
    result = project.IsRenderingInProgress()
    return {"is_rendering": bool(result)}

@mcp.tool()
def load_render_preset(preset_name: str) -> Dict[str, Any]:
    """Load a render preset by name.

    Args:
        preset_name: Name of the render preset to load.
    """
    resolve = get_resolve()
    if resolve is None:
        return {"error": "Not connected to DaVinci Resolve"}
    project = resolve.GetProjectManager().GetCurrentProject()
    if not project:
        return {"error": "No project currently open"}
    result = project.LoadRenderPreset(preset_name)
    return {"success": bool(result), "preset_name": preset_name}

@mcp.tool()
def save_as_new_render_preset(preset_name: str) -> Dict[str, Any]:
    """Save current render settings as a new preset.

    Args:
        preset_name: Name for the new render preset.
    """
    resolve = get_resolve()
    if resolve is None:
        return {"error": "Not connected to DaVinci Resolve"}
    project = resolve.GetProjectManager().GetCurrentProject()
    if not project:
        return {"error": "No project currently open"}
    result = project.SaveAsNewRenderPreset(preset_name)
    return {"success": bool(result), "preset_name": preset_name}

@mcp.tool()
def delete_render_preset(preset_name: str) -> Dict[str, Any]:
    """Delete a render preset.

    Args:
        preset_name: Name of the render preset to delete.
    """
    resolve = get_resolve()
    if resolve is None:
        return {"error": "Not connected to DaVinci Resolve"}
    project = resolve.GetProjectManager().GetCurrentProject()
    if not project:
        return {"error": "No project currently open"}
    result = project.DeleteRenderPreset(preset_name)
    return {"success": bool(result), "preset_name": preset_name}

@mcp.tool()
def set_render_settings(settings: Dict[str, Any]) -> Dict[str, Any]:
    """Set render settings for the current project.

    Args:
        settings: Dict of render settings. Supported keys include:
            SelectAllFrames (bool), MarkIn (int), MarkOut (int),
            TargetDir (str), CustomName (str), UniqueFilenameStyle (0/1),
            ExportVideo (bool), ExportAudio (bool), FormatWidth (int),
            FormatHeight (int), FrameRate (float), VideoQuality (int/str),
            AudioCodec (str), AudioBitDepth (int), AudioSampleRate (int),
            ColorSpaceTag (str), GammaTag (str), ExportAlpha (bool).
    """
    resolve = get_resolve()
    if resolve is None:
        return {"error": "Not connected to DaVinci Resolve"}
    project = resolve.GetProjectManager().GetCurrentProject()
    if not project:
        return {"error": "No project currently open"}
    result = project.SetRenderSettings(settings)
    return {"success": bool(result)}

@mcp.tool()
def get_render_job_status(job_id: str) -> Dict[str, Any]:
    """Get the status of a specific render job.

    Args:
        job_id: The unique ID of the render job.
    """
    resolve = get_resolve()
    if resolve is None:
        return {"error": "Not connected to DaVinci Resolve"}
    project = resolve.GetProjectManager().GetCurrentProject()
    if not project:
        return {"error": "No project currently open"}
    status = project.GetRenderJobStatus(job_id)
    return status if status else {"error": f"No render job with ID {job_id}"}

@mcp.tool()
def get_render_formats() -> Dict[str, Any]:
    """Get all available render formats."""
    resolve = get_resolve()
    if resolve is None:
        return {"error": "Not connected to DaVinci Resolve"}
    project = resolve.GetProjectManager().GetCurrentProject()
    if not project:
        return {"error": "No project currently open"}
    formats = project.GetRenderFormats()
    return {"formats": formats if formats else {}}

@mcp.tool()
def get_render_codecs(format_name: str) -> Dict[str, Any]:
    """Get available codecs for a given render format.

    Args:
        format_name: Render format name (e.g. 'mp4', 'mov', 'avi').
    """
    resolve = get_resolve()
    if resolve is None:
        return {"error": "Not connected to DaVinci Resolve"}
    project = resolve.GetProjectManager().GetCurrentProject()
    if not project:
        return {"error": "No project currently open"}
    codecs = project.GetRenderCodecs(format_name)
    return {"format": format_name, "codecs": codecs if codecs else {}}

@mcp.tool()
def get_current_render_format_and_codec() -> Dict[str, Any]:
    """Get the current render format and codec setting."""
    resolve = get_resolve()
    if resolve is None:
        return {"error": "Not connected to DaVinci Resolve"}
    project = resolve.GetProjectManager().GetCurrentProject()
    if not project:
        return {"error": "No project currently open"}
    result = project.GetCurrentRenderFormatAndCodec()
    return result if result else {"error": "Failed to get render format and codec"}

@mcp.tool()
def set_current_render_format_and_codec(format_name: str, codec_name: str) -> Dict[str, Any]:
    """Set the render format and codec.

    Args:
        format_name: Render format (e.g. 'mp4', 'mov').
        codec_name: Codec name (e.g. 'H264', 'H265', 'ProRes422HQ').
    """
    resolve = get_resolve()
    if resolve is None:
        return {"error": "Not connected to DaVinci Resolve"}
    project = resolve.GetProjectManager().GetCurrentProject()
    if not project:
        return {"error": "No project currently open"}
    result = project.SetCurrentRenderFormatAndCodec(format_name, codec_name)
    return {"success": bool(result), "format": format_name, "codec": codec_name}

@mcp.tool()
def get_current_render_mode() -> Dict[str, Any]:
    """Get the current render mode (0=Individual Clips, 1=Single Clip)."""
    resolve = get_resolve()
    if resolve is None:
        return {"error": "Not connected to DaVinci Resolve"}
    project = resolve.GetProjectManager().GetCurrentProject()
    if not project:
        return {"error": "No project currently open"}
    mode = project.GetCurrentRenderMode()
    return {"render_mode": mode, "mode_name": "Individual Clips" if mode == 0 else "Single Clip"}

@mcp.tool()
def set_current_render_mode(mode: int) -> Dict[str, Any]:
    """Set the render mode.

    Args:
        mode: 0 for Individual Clips, 1 for Single Clip.
    """
    resolve = get_resolve()
    if resolve is None:
        return {"error": "Not connected to DaVinci Resolve"}
    project = resolve.GetProjectManager().GetCurrentProject()
    if not project:
        return {"error": "No project currently open"}
    result = project.SetCurrentRenderMode(mode)
    return {"success": bool(result), "render_mode": mode}

@mcp.tool()
def get_render_resolutions(format_name: str, codec_name: str) -> Dict[str, Any]:
    """Get available render resolutions for a format/codec combination.

    Args:
        format_name: Render format (e.g. 'mp4').
        codec_name: Codec name (e.g. 'H264').
    """
    resolve = get_resolve()
    if resolve is None:
        return {"error": "Not connected to DaVinci Resolve"}
    project = resolve.GetProjectManager().GetCurrentProject()
    if not project:
        return {"error": "No project currently open"}
    resolutions = project.GetRenderResolutions(format_name, codec_name)
    return {"format": format_name, "codec": codec_name, "resolutions": resolutions if resolutions else []}

@mcp.tool()
def insert_audio_to_current_track(file_path: str) -> Dict[str, Any]:
    """Insert audio file to current track at playhead position.

    Args:
        file_path: Absolute path to the audio file.
    """
    resolve = get_resolve()
    if resolve is None:
        return {"error": "Not connected to DaVinci Resolve"}
    project = resolve.GetProjectManager().GetCurrentProject()
    if not project:
        return {"error": "No project currently open"}
    result = project.InsertAudioToCurrentTrackAtPlayhead(file_path)
    return {"success": bool(result), "file_path": file_path}

@mcp.tool()
def load_burn_in_preset(preset_name: str) -> Dict[str, Any]:
    """Load a burn-in preset by name for the project.

    Args:
        preset_name: Name of the burn-in preset to load.
    """
    resolve = get_resolve()
    if resolve is None:
        return {"error": "Not connected to DaVinci Resolve"}
    project = resolve.GetProjectManager().GetCurrentProject()
    if not project:
        return {"error": "No project currently open"}
    result = project.LoadBurnInPreset(preset_name)
    return {"success": bool(result), "preset_name": preset_name}

@mcp.tool()
def export_current_frame_as_still(file_path: str) -> Dict[str, Any]:
    """Export the current frame as a still image.

    Args:
        file_path: Absolute path for the exported still image.
    """
    resolve = get_resolve()
    if resolve is None:
        return {"error": "Not connected to DaVinci Resolve"}
    project = resolve.GetProjectManager().GetCurrentProject()
    if not project:
        return {"error": "No project currently open"}
    result = project.ExportCurrentFrameAsStill(file_path)
    return {"success": bool(result), "file_path": file_path}

@mcp.tool()
def get_quick_export_render_presets() -> Dict[str, Any]:
    """Get list of available quick export render presets."""
    resolve = get_resolve()
    if resolve is None:
        return {"error": "Not connected to DaVinci Resolve"}
    project = resolve.GetProjectManager().GetCurrentProject()
    if not project:
        return {"error": "No project currently open"}
    presets = project.GetQuickExportRenderPresets()
    return {"presets": presets if presets else []}

@mcp.tool()
def render_with_quick_export(preset_name: str) -> Dict[str, Any]:
    """Render the current timeline using a Quick Export preset.

    Args:
        preset_name: Name of the Quick Export preset (e.g. 'H.264', 'YouTube', 'Vimeo').
    """
    resolve = get_resolve()
    if resolve is None:
        return {"error": "Not connected to DaVinci Resolve"}
    project = resolve.GetProjectManager().GetCurrentProject()
    if not project:
        return {"error": "No project currently open"}
    result = project.RenderWithQuickExport(preset_name)
    return {"success": bool(result), "preset_name": preset_name}


# ------------------
# Helper: get project/mediapool
# ------------------
def _get_mp():
    resolve = get_resolve()
    if resolve is None:
        return None, None, {"error": "Not connected to DaVinci Resolve"}
    project = resolve.GetProjectManager().GetCurrentProject()
    if not project:
        return None, None, {"error": "No project currently open"}
    mp = project.GetMediaPool()
    if not mp:
        return project, None, {"error": "Failed to get MediaPool"}
    return project, mp, None

def _find_clip_by_id(folder, target_id):
    for clip in (folder.GetClipList() or []):
        if clip.GetUniqueId() == target_id:
            return clip
    for sub in (folder.GetSubFolderList() or []):
        found = _find_clip_by_id(sub, target_id)
        if found:
            return found
    return None

def _find_clips_by_ids(folder, ids_set):
    found = []
    for clip in (folder.GetClipList() or []):
        if clip.GetUniqueId() in ids_set:
            found.append(clip)
    for sub in (folder.GetSubFolderList() or []):
        found.extend(_find_clips_by_ids(sub, ids_set))
    return found

def _navigate_to_folder(mp, folder_path):
    root = mp.GetRootFolder()
    if not folder_path or folder_path in ("Master", "/", ""):
        return root
    parts = folder_path.strip("/").split("/")
    if parts[0] == "Master":
        parts = parts[1:]
    current = root
    for part in parts:
        found = False
        for sub in (current.GetSubFolderList() or []):
            if sub.GetName() == part:
                current = sub
                found = True
                break
        if not found:
            return None
    return current

def _get_timeline():
    resolve = get_resolve()
    if resolve is None:
        return None, None, {"error": "Not connected to DaVinci Resolve"}
    project = resolve.GetProjectManager().GetCurrentProject()
    if not project:
        return None, None, {"error": "No project currently open"}
    tl = project.GetCurrentTimeline()
    if not tl:
        return project, None, {"error": "No current timeline"}
    return project, tl, None

def _get_timeline_item(track_type="video", track_index=1, item_index=0):
    _, tl, err = _get_timeline()
    if err:
        return None, err
    items = tl.GetItemListInTrack(track_type, track_index)
    if not items or item_index >= len(items):
        return None, {"error": f"No item at index {item_index} on {track_type} track {track_index}"}
    return items[item_index], None


# ------------------
# MediaPool Tools (remaining)
# ------------------

@mcp.tool()
def add_render_job() -> Dict[str, Any]:
    """Add a render job based on current render settings to the render queue.

    Returns the unique job ID string for the new render job.
    Configure render settings first with set_render_settings, set_render_format_and_codec, etc.
    """
    resolve = get_resolve()
    if resolve is None:
        return {"error": "Not connected to DaVinci Resolve"}
    project = resolve.GetProjectManager().GetCurrentProject()
    if not project:
        return {"error": "No project currently open"}
    job_id = project.AddRenderJob()
    if job_id:
        return {"success": True, "job_id": job_id}
    return {"success": False, "error": "Failed to add render job. Check render settings are configured."}

