#!/usr/bin/env python3
"""
DaVinci Resolve MCP Timeline Item Markers Tools
Markers, flags, and clip color on timeline items
"""

from typing import Dict, Any, Optional


def _get_timeline_item(resolve, track_type: str = "video", track_index: int = 1, item_index: int = 0):
    """Get a timeline item by track_type, track_index, and item_index.

    Args:
        resolve: DaVinci Resolve connection
        track_type: "video", "audio", or "subtitle"
        track_index: 1-based track index
        item_index: 0-based item index within the track

    Returns:
        Tuple of (timeline_item, timeline) or (None, error_dict)
    """
    if resolve is None:
        return None, {"error": "Not connected to DaVinci Resolve"}

    project_manager = resolve.GetProjectManager()
    if not project_manager:
        return None, {"error": "Failed to get Project Manager"}

    current_project = project_manager.GetCurrentProject()
    if not current_project:
        return None, {"error": "No project currently open"}

    timeline = current_project.GetCurrentTimeline()
    if not timeline:
        return None, {"error": "No timeline currently active"}

    items = timeline.GetItemListInTrack(track_type, track_index) or []
    if item_index < 0 or item_index >= len(items):
        return None, {"error": f"Item index {item_index} out of range for track {track_type}:{track_index}"}

    item = items[item_index]
    return item, timeline


def register_timeline_item_markers_tools(mcp, resolve, logger):
    """Register timeline item markers MCP tools."""

    @mcp.tool()
    def timeline_item_markers(action: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Markers, flags, and clip color on timeline items. Identify by track_type, track_index, item_index.

        Actions:
          add(frame, color, name, note, duration, custom_data?, ...) -> {success}
          get_all(...) -> {markers}
          get_by_custom_data(custom_data, ...) -> {markers}
          update_custom_data(frame, custom_data, ...) -> {success}
          get_custom_data(frame, ...) -> {data}
          delete_by_color(color, ...) -> {success}
          delete_at_frame(frame, ...) -> {success}
          delete_by_custom_data(custom_data, ...) -> {success}
          add_flag(color, ...) -> {success}
          get_flags(...) -> {flags}
          clear_flags(color, ...) -> {success}
          get_clip_color(...) -> {color}
          set_clip_color(color, ...) -> {success}
          clear_clip_color(...) -> {success}

        Default: track_type="video", track_index=1, item_index=0

        Args:
            action: The action to perform
            params: Optional parameters for the action

        Returns:
            dict: Result of the action
        """
        if resolve is None:
            return {"error": "Not connected to DaVinci Resolve"}

        p = params or {}
        action_lower = action.lower()

        # Extract common parameters with defaults
        track_type = p.get("track_type", "video")
        track_index = p.get("track_index", 1)
        item_index = p.get("item_index", 0)

        if action_lower == "add":
            frame = p.get("frame")
            color = p.get("color", "Blue")
            name = p.get("name", "")
            note = p.get("note", "")
            duration = p.get("duration", 1)
            custom_data = p.get("custom_data", "")

            if frame is None:
                return {"success": False, "error": "frame is required"}

            item, result = _get_timeline_item(resolve, track_type, track_index, item_index)
            if item is None:
                return result

            try:
                result_val = item.AddMarker(frame, color, name, note, duration, custom_data)
                if result_val:
                    return {"success": True, "message": f"Added {color} marker at frame {frame}"}
                else:
                    return {"success": False, "error": f"Failed to add marker at frame {frame}"}
            except Exception as e:
                return {"success": False, "error": f"Error: {str(e)}"}

        elif action_lower == "get_all":
            item, result = _get_timeline_item(resolve, track_type, track_index, item_index)
            if item is None:
                return result

            try:
                markers = item.GetMarkers()
                if markers:
                    return {"markers": markers, "count": len(markers)}
                return {"markers": {}, "count": 0}
            except Exception as e:
                return {"error": f"Error: {str(e)}"}

        elif action_lower == "get_by_custom_data":
            custom_data = p.get("custom_data")
            if not custom_data:
                return {"error": "custom_data is required"}

            item, result = _get_timeline_item(resolve, track_type, track_index, item_index)
            if item is None:
                return result

            try:
                marker = item.GetMarkerByCustomData(custom_data)
                if marker:
                    return {"marker": marker}
                return {"error": "No marker found with specified custom data"}
            except Exception as e:
                return {"error": f"Error: {str(e)}"}

        elif action_lower == "update_custom_data":
            frame = p.get("frame")
            custom_data = p.get("custom_data")
            if frame is None or custom_data is None:
                return {"success": False, "error": "frame and custom_data are required"}

            item, result = _get_timeline_item(resolve, track_type, track_index, item_index)
            if item is None:
                return result

            try:
                result_val = item.UpdateMarkerCustomData(frame, custom_data)
                if result_val:
                    return {"success": True, "message": f"Updated custom data for marker at frame {frame}"}
                else:
                    return {"success": False, "error": f"Failed to update marker at frame {frame}"}
            except Exception as e:
                return {"success": False, "error": f"Error: {str(e)}"}

        elif action_lower == "get_custom_data":
            frame = p.get("frame")
            if frame is None:
                return {"error": "frame is required"}

            item, result = _get_timeline_item(resolve, track_type, track_index, item_index)
            if item is None:
                return result

            try:
                data = item.GetMarkerCustomData(frame)
                return {"data": data if data else ""}
            except Exception as e:
                return {"error": f"Error: {str(e)}"}

        elif action_lower == "delete_by_color":
            color = p.get("color")
            if not color:
                return {"success": False, "error": "color is required"}

            item, result = _get_timeline_item(resolve, track_type, track_index, item_index)
            if item is None:
                return result

            try:
                result_val = item.DeleteMarkersByColor(color)
                if result_val:
                    return {"success": True, "message": f"Deleted all {color} markers"}
                else:
                    return {"success": False, "error": f"No {color} markers found"}
            except Exception as e:
                return {"success": False, "error": f"Error: {str(e)}"}

        elif action_lower == "delete_at_frame":
            frame = p.get("frame")
            if frame is None:
                return {"success": False, "error": "frame is required"}

            item, result = _get_timeline_item(resolve, track_type, track_index, item_index)
            if item is None:
                return result

            try:
                result_val = item.DeleteMarkerAtFrame(frame)
                if result_val:
                    return {"success": True, "message": f"Deleted marker at frame {frame}"}
                else:
                    return {"success": False, "error": f"No marker found at frame {frame}"}
            except Exception as e:
                return {"success": False, "error": f"Error: {str(e)}"}

        elif action_lower == "delete_by_custom_data":
            custom_data = p.get("custom_data")
            if not custom_data:
                return {"success": False, "error": "custom_data is required"}

            item, result = _get_timeline_item(resolve, track_type, track_index, item_index)
            if item is None:
                return result

            try:
                result_val = item.DeleteMarkerByCustomData(custom_data)
                if result_val:
                    return {"success": True, "message": "Deleted marker with specified custom data"}
                else:
                    return {"success": False, "error": "No marker found with specified custom data"}
            except Exception as e:
                return {"success": False, "error": f"Error: {str(e)}"}

        elif action_lower == "add_flag":
            color = p.get("color")
            if not color:
                return {"success": False, "error": "color is required"}

            item, result = _get_timeline_item(resolve, track_type, track_index, item_index)
            if item is None:
                return result

            try:
                result_val = item.AddFlag(color)
                if result_val:
                    return {"success": True, "message": f"Added {color} flag"}
                else:
                    return {"success": False, "error": "Failed to add flag"}
            except Exception as e:
                return {"success": False, "error": f"Error: {str(e)}"}

        elif action_lower == "get_flags":
            item, result = _get_timeline_item(resolve, track_type, track_index, item_index)
            if item is None:
                return result

            try:
                flags = item.GetFlags()
                return {"flags": flags if flags else {}}
            except Exception as e:
                return {"error": f"Error: {str(e)}"}

        elif action_lower == "clear_flags":
            color = p.get("color")  # Optional

            item, result = _get_timeline_item(resolve, track_type, track_index, item_index)
            if item is None:
                return result

            try:
                if color:
                    result_val = item.ClearFlags(color)
                else:
                    result_val = item.ClearFlags()
                if result_val:
                    return {"success": True, "message": "Cleared flags"}
                else:
                    return {"success": False, "error": "Failed to clear flags"}
            except Exception as e:
                return {"success": False, "error": f"Error: {str(e)}"}

        elif action_lower == "get_clip_color":
            item, result = _get_timeline_item(resolve, track_type, track_index, item_index)
            if item is None:
                return result

            try:
                color = item.GetClipColor()
                return {"color": color if color else ""}
            except Exception as e:
                return {"error": f"Error: {str(e)}"}

        elif action_lower == "set_clip_color":
            color = p.get("color")
            if not color:
                return {"success": False, "error": "color is required"}

            item, result = _get_timeline_item(resolve, track_type, track_index, item_index)
            if item is None:
                return result

            try:
                result_val = item.SetClipColor(color)
                if result_val:
                    return {"success": True, "message": f"Set clip color to {color}"}
                else:
                    return {"success": False, "error": "Failed to set clip color"}
            except Exception as e:
                return {"success": False, "error": f"Error: {str(e)}"}

        elif action_lower == "clear_clip_color":
            item, result = _get_timeline_item(resolve, track_type, track_index, item_index)
            if item is None:
                return result

            try:
                result_val = item.ClearClipColor()
                if result_val:
                    return {"success": True, "message": "Cleared clip color"}
                else:
                    return {"success": False, "error": "Failed to clear clip color"}
            except Exception as e:
                return {"success": False, "error": f"Error: {str(e)}"}

        else:
            valid = [
                "add", "get_all", "get_by_custom_data", "update_custom_data",
                "get_custom_data", "delete_by_color", "delete_at_frame",
                "delete_by_custom_data", "add_flag", "get_flags", "clear_flags",
                "get_clip_color", "set_clip_color", "clear_clip_color"
            ]
            return {"error": f"Unknown action '{action}'. Valid actions: {', '.join(valid)}"}

    logger.info("Registered timeline item markers tools")