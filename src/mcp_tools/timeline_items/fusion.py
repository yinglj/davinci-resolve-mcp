#!/usr/bin/env python3
"""
DaVinci Resolve MCP Timeline Item Fusion Tools
Fusion composition operations on timeline items
"""

from typing import Dict, Any, Optional

from .properties import find_timeline_item


def resolve_item_from_params(timeline, track_type, track_index, item_index):
    """Resolve a timeline item from track/item indices.

    Args:
        timeline: The timeline object.
        track_type: Type of track ("video", "audio").
        track_index: 1-based track index.
        item_index: 0-based item index within the track.

    Returns:
        Timeline item or None if not found.
    """
    if item_index is None:
        return None

    effective_track = track_index or 1
    items = timeline.GetItemListInTrack(track_type, effective_track) or []
    if 0 <= item_index < len(items):
        return items[item_index]
    return None


def register_timeline_item_fusion_tools(mcp, resolve, logger):
    """Register timeline item fusion MCP tools."""

    @mcp.tool()
    def timeline_item_fusion(
        action: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Fusion composition operations on timeline items.

        Identify by track_type, track_index, item_index.
        Default: track_type="video", track_index=1, item_index=0

        Actions:
            add_comp(...) -> {success}
            get_comp_count(...) -> {count}
            get_comp_names(...) -> {names}
            get_comp_by_name(name, ...) -> {available}
            get_comp_by_index(index, ...) -> {available}
            export_comp(path, index, ...) -> {success}
            import_comp(path, ...) -> {success}
            delete_comp(name, ...) -> {success}
            load_comp(name, ...) -> {success}
            rename_comp(old_name, new_name, ...) -> {success}

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

        current_timeline = current_project.GetCurrentTimeline()
        if not current_timeline:
            return {"error": "No timeline currently active"}

        params = params or {}

        track_type = params.get("track_type", "video")
        track_index = params.get("track_index", 1)
        item_index = params.get("item_index", 0)

        # Resolve timeline item
        timeline_item = resolve_item_from_params(
            current_timeline, track_type, track_index, item_index
        )

        if not timeline_item:
            return {
                "error": f"Timeline item not found at track={track_index}, index={item_index}"
            }

        try:
            if action == "add_comp":
                return _fusion_add_comp(timeline_item)
            elif action == "get_comp_count":
                return _fusion_get_comp_count(timeline_item)
            elif action == "get_comp_names":
                return _fusion_get_comp_names(timeline_item)
            elif action == "get_comp_by_name":
                name = params.get("name")
                if not name:
                    return {"error": "name parameter is required for get_comp_by_name"}
                return _fusion_get_comp_by_name(timeline_item, name)
            elif action == "get_comp_by_index":
                index = params.get("index")
                if index is None:
                    return {"error": "index parameter is required for get_comp_by_index"}
                return _fusion_get_comp_by_index(timeline_item, index)
            elif action == "export_comp":
                path = params.get("path")
                index = params.get("index", 0)
                if not path:
                    return {"error": "path parameter is required for export_comp"}
                return _fusion_export_comp(timeline_item, path, index)
            elif action == "import_comp":
                path = params.get("path")
                if not path:
                    return {"error": "path parameter is required for import_comp"}
                return _fusion_import_comp(timeline_item, path)
            elif action == "delete_comp":
                name = params.get("name")
                if not name:
                    return {"error": "name parameter is required for delete_comp"}
                return _fusion_delete_comp(timeline_item, name)
            elif action == "load_comp":
                name = params.get("name")
                if not name:
                    return {"error": "name parameter is required for load_comp"}
                return _fusion_load_comp(timeline_item, name)
            elif action == "rename_comp":
                old_name = params.get("old_name")
                new_name = params.get("new_name")
                if not old_name or not new_name:
                    return {
                        "error": "old_name and new_name parameters are required for rename_comp"
                    }
                return _fusion_rename_comp(timeline_item, old_name, new_name)
            else:
                return {
                    "error": f"Unknown action: {action}. Valid actions: add_comp, get_comp_count, get_comp_names, get_comp_by_name, get_comp_by_index, export_comp, import_comp, delete_comp, load_comp, rename_comp"
                }
        except Exception as e:
            return {"error": f"Error executing {action}: {str(e)}"}

    def _fusion_add_comp(timeline_item):
        """Add a new Fusion composition."""
        try:
            comp = timeline_item.AddFusionComp()
            if comp:
                return {"success": True, "comp": str(comp)}
            return {"success": False, "error": "Failed to add Fusion composition"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _fusion_get_comp_count(timeline_item):
        """Get the number of Fusion compositions."""
        try:
            count = timeline_item.GetCompCount()
            return {"count": count}
        except Exception as e:
            return {"error": str(e)}

    def _fusion_get_comp_names(timeline_item):
        """Get names of all Fusion compositions."""
        try:
            count = timeline_item.GetCompCount()
            names = []
            for i in range(count):
                try:
                    comp = timeline_item.GetCompByIndex(i)
                    if comp:
                        names.append(comp.GetName())
                except Exception:
                    pass
            return {"names": names}
        except Exception as e:
            return {"error": str(e)}

    def _fusion_get_comp_by_name(timeline_item, name):
        """Get a Fusion composition by name."""
        try:
            comp = timeline_item.GetCompByName(name)
            if comp:
                return {"available": True, "name": name}
            return {"available": False}
        except Exception as e:
            return {"error": str(e)}

    def _fusion_get_comp_by_index(timeline_item, index):
        """Get a Fusion composition by index."""
        try:
            comp = timeline_item.GetCompByIndex(index)
            if comp:
                return {"available": True, "index": index, "name": comp.GetName()}
            return {"available": False}
        except Exception as e:
            return {"error": str(e)}

    def _fusion_export_comp(timeline_item, path, index):
        """Export a Fusion composition to a file."""
        try:
            result = timeline_item.ExportFusionComp(path, index)
            return {"success": result}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _fusion_import_comp(timeline_item, path):
        """Import a Fusion composition from a file."""
        try:
            result = timeline_item.ImportFusionComp(path)
            return {"success": result}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _fusion_delete_comp(timeline_item, name):
        """Delete a Fusion composition by name."""
        try:
            result = timeline_item.DeleteFusionComp(name)
            return {"success": result}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _fusion_load_comp(timeline_item, name):
        """Load a Fusion composition by name."""
        try:
            result = timeline_item.LoadFusionComp(name)
            return {"success": result}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _fusion_rename_comp(timeline_item, old_name, new_name):
        """Rename a Fusion composition."""
        try:
            result = timeline_item.RenameFusionComp(old_name, new_name)
            return {"success": result}
        except Exception as e:
            return {"success": False, "error": str(e)}

    logger.info("Registered timeline item fusion tools")