#!/usr/bin/env python3
"""
DaVinci Resolve MCP Gallery Stills Tools
Manage stills in gallery albums
"""

from typing import Dict, Any, Optional


def _unknown(action, valid):
    """Return error for unknown action."""
    return {"error": f"Unknown action '{action}'. Valid actions: {', '.join(valid)}"}


def register_gallery_stills_tools(mcp, resolve, logger):
    """Register gallery stills MCP tools."""

    @mcp.tool()
    def gallery_stills(
        action: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Manage stills in gallery albums (best results on Color page).

        Actions:
            get_stills(album_index?) -> {count}
            get_label(still_index, album_index?) -> {label}
            set_label(still_index, label, album_index?) -> {success}
            import_stills(paths, album_index?) -> {success}
            export_stills(folder_path, prefix?, format?, album_index?) -> {success}
            delete_stills(still_indices, album_index?) -> {success}

        album_index defaults to current album. still_index is 0-based.

        Args:
            action: The action to perform.
            params: Optional parameters for the action.

        Returns:
            Dict containing the result of the action.
        """
        if resolve is None:
            return {"error": "Not connected to DaVinci Resolve"}

        project_manager = resolve.GetProjectManager()
        if not project_manager:
            return {"error": "Failed to get Project Manager"}

        current_project = project_manager.GetCurrentProject()
        if not current_project:
            return {"error": "No project currently open"}

        gallery = current_project.GetGallery()
        if not gallery:
            return {"error": "Gallery not available"}

        p = params or {}
        album_index = p.get("album_index")

        # Resolve album
        album = _resolve_album(gallery, album_index)
        if not album:
            return {"error": "No still album available"}

        try:
            if action == "get_stills":
                return _get_stills(album)
            elif action == "get_label":
                return _get_label(album, p)
            elif action == "set_label":
                return _set_label(album, p)
            elif action == "import_stills":
                return _import_stills(album, p)
            elif action == "export_stills":
                return _export_stills(album, p)
            elif action == "delete_stills":
                return _delete_stills(album, p)
            else:
                return _unknown(action, ["get_stills", "get_label", "set_label", "import_stills", "export_stills", "delete_stills"])
        except Exception as e:
            return {"error": f"Error executing {action}: {str(e)}"}

    logger.info("Registered gallery stills tools")


def _resolve_album(gallery, album_index):
    """Resolve an album by index or get current album."""
    if album_index is not None:
        albums = gallery.GetGalleryStillAlbums() or []
        if 0 <= album_index < len(albums):
            return albums[album_index]
        return None
    # Default to current album
    album = gallery.GetCurrentStillAlbum()
    if not album:
        albums = gallery.GetGalleryStillAlbums() or []
        album = albums[0] if albums else None
    return album


def _get_stills(album):
    """Get count of stills in album."""
    stills = album.GetStills() or []
    return {"count": len(stills)}


def _get_label(album, params):
    """Get label of a still by index."""
    still_index = params.get("still_index", 0)
    stills = album.GetStills() or []
    if 0 <= still_index < len(stills):
        return {"label": album.GetLabel(stills[still_index])}
    return {"error": f"Still index {still_index} out of range"}


def _set_label(album, params):
    """Set label of a still by index."""
    still_index = params.get("still_index", 0)
    label = params.get("label", "")
    stills = album.GetStills() or []
    if 0 <= still_index < len(stills):
        return {"success": bool(album.SetLabel(stills[still_index], label))}
    return {"error": f"Still index {still_index} out of range"}


def _import_stills(album, params):
    """Import stills into album."""
    paths = params.get("paths")
    if not paths:
        return {"error": "paths parameter is required for import_stills"}
    return {"success": bool(album.ImportStills(paths))}


def _export_stills(album, params):
    """Export stills from album."""
    folder_path = params.get("folder_path")
    if not folder_path:
        return {"error": "folder_path parameter is required for export_stills"}

    stills = album.GetStills() or []
    if not stills:
        return {"error": "No stills to export"}

    prefix = params.get("prefix", "still")
    format = params.get("format", "dpx")
    return {"success": bool(album.ExportStills(stills, folder_path, prefix, format))}


def _delete_stills(album, params):
    """Delete stills from album by indices."""
    still_indices = params.get("still_indices", [])
    if not still_indices:
        return {"error": "still_indices parameter is required for delete_stills"}

    stills = album.GetStills() or []
    to_delete = [stills[i] for i in still_indices if 0 <= i < len(stills)]
    if not to_delete:
        return {"error": "No valid still indices provided"}
    return {"success": bool(album.DeleteStills(to_delete))}
