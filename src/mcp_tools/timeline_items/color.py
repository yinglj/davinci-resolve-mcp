#!/usr/bin/env python3
"""
DaVinci Resolve MCP Timeline Item Color Tools
Color grading, versions, LUTs, cache, and AI tools on timeline items
"""

from typing import Dict, Any, Optional

from .properties import find_timeline_item


def resolve_item_from_params(
    timeline, track_type, track_index, item_index, timeline_item_id=None
):
    """Resolve a timeline item from track/item indices or timeline_item_id.

    Args:
        timeline: The timeline object.
        track_type: Type of track ("video", "audio").
        track_index: 1-based track index.
        item_index: 0-based item index within the track.
        timeline_item_id: Optional unique ID of the item.

    Returns:
        Timeline item or None if not found.
    """
    if timeline_item_id:
        item, _ = find_timeline_item(
            timeline,
            timeline_item_id,
            search_video=True,
            search_audio=True,
        )
        return item

    if item_index is None:
        return None

    effective_track = track_index or 1
    items = timeline.GetItemListInTrack(track_type, effective_track) or []
    if 0 <= item_index < len(items):
        return items[item_index]
    return None


def register_timeline_item_color_tools(mcp, resolve, logger):
    """Register timeline item color MCP tools."""

    @mcp.tool()
    def timeline_item_color(
        action: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Color grading, versions, LUTs, cache, and AI tools on timeline items.

        Identify by track_type, track_index, item_index.
        Default: track_type="video", track_index=1, item_index=0

        Actions:
            set_cdl(cdl, ...) -> {success} — cdl: {NodeIndex, Slope, Offset, Power, Saturation}
            copy_grades(target_ids, ...) -> {success}
            add_version(name, type?, ...) -> {success} — type: 0=local, 1=remote
            get_current_version(...) -> {version}
            get_version_names(type?, ...) -> {names}
            load_version(name, type?, ...) -> {success}
            rename_version(old_name, new_name, type?, ...) -> {success}
            delete_version(name, type?, ...) -> {success}
            get_node_graph(layer_index?, ...) -> {available}
            get_color_group(...) -> {name}
            assign_color_group(group_name, ...) -> {success}
            remove_from_color_group(...) -> {success}
            export_lut(type, path, ...) -> {success}
            get_color_cache(...) -> {enabled}
            set_color_cache(enabled, ...) -> {success}
            get_fusion_cache(...) -> {enabled}
            set_fusion_cache(enabled, ...) -> {success}
            stabilize(...) -> {success}
            smart_reframe(...) -> {success}
            create_magic_mask(mode, ...) -> {success} — mode: "F" forward, "B" backward, "BI" bidirectional
            regenerate_magic_mask(...) -> {success}

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
        timeline_item_id = params.get("timeline_item_id")

        # Resolve timeline item
        timeline_item = resolve_item_from_params(
            current_timeline,
            track_type,
            track_index,
            item_index,
            timeline_item_id,
        )

        if not timeline_item and action not in ["get_color_group", "get_node_graph"]:
            return {
                "error": f"Timeline item not found at track={track_index}, index={item_index}"
            }

        try:
            if action == "set_cdl":
                cdl = params.get("cdl", {})
                node_index = params.get("node_index")
                return _color_set_cdl(timeline_item, cdl, node_index)
            elif action == "copy_grades":
                target_ids = params.get("target_ids", [])
                return _color_copy_grades(current_project, timeline_item, target_ids)
            elif action == "add_version":
                name = params.get("name")
                version_type = params.get("type", 0)
                return _color_add_version(timeline_item, name, version_type)
            elif action == "get_current_version":
                return _color_get_current_version(timeline_item)
            elif action == "get_version_names":
                version_type = params.get("type")
                return _color_get_version_names(timeline_item, version_type)
            elif action == "load_version":
                name = params.get("name")
                version_type = params.get("type", 0)
                return _color_load_version(timeline_item, name, version_type)
            elif action == "rename_version":
                old_name = params.get("old_name")
                new_name = params.get("new_name")
                version_type = params.get("type", 0)
                return _color_rename_version(timeline_item, old_name, new_name, version_type)
            elif action == "delete_version":
                name = params.get("name")
                version_type = params.get("type", 0)
                return _color_delete_version(timeline_item, name, version_type)
            elif action == "get_node_graph":
                layer_index = params.get("layer_index")
                return _color_get_node_graph(timeline_item, layer_index)
            elif action == "get_color_group":
                return _color_get_color_group(current_project, timeline_item)
            elif action == "assign_color_group":
                group_name = params.get("group_name")
                if not group_name:
                    return {"error": "group_name parameter is required for assign_color_group"}
                return _color_assign_color_group(current_project, timeline_item, group_name)
            elif action == "remove_from_color_group":
                return _color_remove_from_color_group(current_project, timeline_item)
            elif action == "export_lut":
                lut_type = params.get("type")
                path = params.get("path")
                if not lut_type or not path:
                    return {"error": "type and path parameters are required for export_lut"}
                return _color_export_lut(timeline_item, lut_type, path)
            elif action == "get_color_cache":
                return _color_get_color_cache(timeline_item)
            elif action == "set_color_cache":
                enabled = params.get("enabled")
                if enabled is None:
                    return {"error": "enabled parameter is required for set_color_cache"}
                return _color_set_color_cache(timeline_item, enabled)
            elif action == "get_fusion_cache":
                return _color_get_fusion_cache(timeline_item)
            elif action == "set_fusion_cache":
                enabled = params.get("enabled")
                if enabled is None:
                    return {"error": "enabled parameter is required for set_fusion_cache"}
                return _color_set_fusion_cache(timeline_item, enabled)
            elif action == "stabilize":
                return _color_stabilize(timeline_item, params)
            elif action == "smart_reframe":
                return _color_smart_reframe(timeline_item, params)
            elif action == "create_magic_mask":
                mode = params.get("mode", "F")
                return _color_create_magic_mask(timeline_item, mode)
            elif action == "regenerate_magic_mask":
                return _color_regenerate_magic_mask(timeline_item)
            else:
                return {
                    "error": f"Unknown action: {action}. Valid actions: set_cdl, copy_grades, add_version, get_current_version, get_version_names, load_version, rename_version, delete_version, get_node_graph, get_color_group, assign_color_group, remove_from_color_group, export_lut, get_color_cache, set_color_cache, get_fusion_cache, set_fusion_cache, stabilize, smart_reframe, create_magic_mask, regenerate_magic_mask"
                }
        except Exception as e:
            return {"error": f"Error executing {action}: {str(e)}"}

    def _color_set_cdl(timeline_item, cdl, node_index):
        """Set CDL (Color Decision List) values."""
        try:
            if node_index is not None:
                result = timeline_item.SetCDL(
                    nodeIndex=node_index,
                    slope=cdl.get("Slope"),
                    offset=cdl.get("Offset"),
                    power=cdl.get("Power"),
                    saturation=cdl.get("Saturation"),
                )
            else:
                result = timeline_item.SetCDL(
                    slope=cdl.get("Slope"),
                    offset=cdl.get("Offset"),
                    power=cdl.get("Power"),
                    saturation=cdl.get("Saturation"),
                )
            return {"success": result}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _color_copy_grades(current_project, timeline_item, target_ids):
        """Copy grades to target timeline items."""
        try:
            current_timeline = current_project.GetCurrentTimeline()
            targets = []
            for tid in target_ids:
                item, _ = find_timeline_item(
                    current_timeline,
                    tid,
                    search_video=True,
                    search_audio=True,
                )
                if item:
                    targets.append(item)

            if not targets:
                return {"success": False, "error": "No valid target items found"}

            grade = timeline_item.GetCurrentGrade()
            if not grade:
                return {"success": False, "error": "Failed to get current grade"}

            result = True
            for target in targets:
                if not target.CopyGrade(grade):
                    result = False

            return {"success": result, "copied_count": len(targets)}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _color_add_version(timeline_item, name, version_type=0):
        """Add a new color version."""
        if not name:
            return {"success": False, "error": "name parameter is required"}
        try:
            version_type_map = {0: "Local", 1: "Remote"}
            vtype = version_type_map.get(version_type, "Local")
            result = timeline_item.AddVersion(name, vtype)
            return {"success": result, "name": name, "type": version_type}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _color_get_current_version(timeline_item):
        """Get the current color version."""
        try:
            version = timeline_item.GetCurrentVersion()
            if version:
                return {"version": version}
            return {"version": None}
        except Exception as e:
            return {"error": str(e)}

    def _color_get_version_names(timeline_item, version_type=None):
        """Get names of all color versions."""
        try:
            version_type_map = {0: "Local", 1: "Remote"}
            if version_type is not None:
                vtype = version_type_map.get(version_type, "Local")
                names = timeline_item.GetVersionNames(vtype)
            else:
                local_names = timeline_item.GetVersionNames("Local") or []
                remote_names = timeline_item.GetVersionNames("Remote") or []
                names = local_names + remote_names
            return {"names": list(names) if names else []}
        except Exception as e:
            return {"error": str(e)}

    def _color_load_version(timeline_item, name, version_type=0):
        """Load a color version by name."""
        if not name:
            return {"success": False, "error": "name parameter is required"}
        try:
            version_type_map = {0: "Local", 1: "Remote"}
            vtype = version_type_map.get(version_type, "Local")
            result = timeline_item.LoadVersion(name, vtype)
            return {"success": result}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _color_rename_version(timeline_item, old_name, new_name, version_type=0):
        """Rename a color version."""
        if not old_name or not new_name:
            return {"success": False, "error": "old_name and new_name parameters are required"}
        try:
            version_type_map = {0: "Local", 1: "Remote"}
            vtype = version_type_map.get(version_type, "Local")
            result = timeline_item.RenameVersion(old_name, new_name, vtype)
            return {"success": result, "old_name": old_name, "new_name": new_name}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _color_delete_version(timeline_item, name, version_type=0):
        """Delete a color version."""
        if not name:
            return {"success": False, "error": "name parameter is required"}
        try:
            version_type_map = {0: "Local", 1: "Remote"}
            vtype = version_type_map.get(version_type, "Local")
            result = timeline_item.DeleteVersion(name, vtype)
            return {"success": result}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _color_get_node_graph(timeline_item, layer_index=None):
        """Get the node graph for the timeline item."""
        try:
            if layer_index is not None:
                available = timeline_item.GetNodeGraph(layer_index)
            else:
                available = timeline_item.GetNodeGraph()
            return {"available": available}
        except Exception as e:
            return {"error": str(e)}

    def _color_get_color_group(current_project, timeline_item):
        """Get the color group name for the timeline item."""
        try:
            group_name = timeline_item.GetColorGroup()
            return {"name": group_name if group_name else None}
        except Exception as e:
            return {"error": str(e)}

    def _color_assign_color_group(current_project, timeline_item, group_name):
        """Assign the timeline item to a color group."""
        try:
            current_project = current_project
            result = timeline_item.AssignColorGroup(group_name)
            return {"success": result, "group_name": group_name}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _color_remove_from_color_group(current_project, timeline_item):
        """Remove the timeline item from its color group."""
        try:
            result = timeline_item.RemoveFromColorGroup()
            return {"success": result}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _color_export_lut(timeline_item, lut_type, path):
        """Export a LUT from the timeline item."""
        try:
            result = timeline_item.ExportLUT(lut_type, path)
            return {"success": result, "path": path, "type": lut_type}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _color_get_color_cache(timeline_item):
        """Get the color cache setting."""
        try:
            enabled = timeline_item.GetColorCache()
            return {"enabled": enabled}
        except Exception as e:
            return {"error": str(e)}

    def _color_set_color_cache(timeline_item, enabled):
        """Set the color cache setting."""
        try:
            result = timeline_item.SetColorCache(enabled)
            return {"success": result, "enabled": enabled}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _color_get_fusion_cache(timeline_item):
        """Get the Fusion cache setting."""
        try:
            enabled = timeline_item.GetFusionCache()
            return {"enabled": enabled}
        except Exception as e:
            return {"error": str(e)}

    def _color_set_fusion_cache(timeline_item, enabled):
        """Set the Fusion cache setting."""
        try:
            result = timeline_item.SetFusionCache(enabled)
            return {"success": result, "enabled": enabled}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _color_stabilize(timeline_item, params):
        """Apply stabilization to the timeline item."""
        try:
            mode = params.get("mode")
            result = timeline_item.Stabilize(mode) if mode else timeline_item.Stabilize()
            return {"success": result}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _color_smart_reframe(timeline_item, params):
        """Apply smart reframing to the timeline item."""
        try:
            result = timeline_item.SmartReframe()
            return {"success": result}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _color_create_magic_mask(timeline_item, mode="F"):
        """Create a magic mask on the timeline item."""
        try:
            result = timeline_item.CreateMagicMask(mode)
            return {"success": result, "mode": mode}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _color_regenerate_magic_mask(timeline_item):
        """Regenerate the magic mask on the timeline item."""
        try:
            result = timeline_item.RegenerateMagicMask()
            return {"success": result}
        except Exception as e:
            return {"success": False, "error": str(e)}

    logger.info("Registered timeline item color tools")