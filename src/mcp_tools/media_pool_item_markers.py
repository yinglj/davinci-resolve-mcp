#!/usr/bin/env python3
"""
DaVinci Resolve MCP Media Pool Item Markers Tools
Markers and flags on media pool clips
"""

from typing import Dict, Any, Optional


def register_media_pool_item_markers_tools(mcp, resolve, logger):
    """Register media pool item markers MCP tools."""

    @mcp.tool()
    def media_pool_item_markers(action: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Markers and flags on media pool clips. Identify clip by clip_id.

        Actions:
          add(clip_id, frame, color, name, note, duration, custom_data?) -> {success}
          get_all(clip_id) -> {markers}
          get_by_custom_data(clip_id, custom_data) -> {markers}
          update_custom_data(clip_id, frame, custom_data) -> {success}
          get_custom_data(clip_id, frame) -> {data}
          delete_by_color(clip_id, color) -> {success}
          delete_at_frame(clip_id, frame) -> {success}
          delete_by_custom_data(clip_id, custom_data) -> {success}
          add_flag(clip_id, color) -> {success}
          get_flags(clip_id) -> {flags}
          clear_flags(clip_id, color) -> {success}

        Args:
            action: The action to perform
            params: Optional parameters for the action

        Returns:
            dict: Result of the action
        """
        from src.api.marker_operations import (
            get_clip_markers,
            add_clip_marker,
        )

        if resolve is None:
            return {"error": "Not connected to DaVinci Resolve"}

        p = params or {}
        action_lower = action.lower()

        if action_lower == "add":
            clip_id = p.get("clip_id")
            frame = p.get("frame")
            color = p.get("color", "Blue")
            name = p.get("name", "")
            note = p.get("note", "")
            duration = p.get("duration", 1)
            custom_data = p.get("custom_data", "")

            if not clip_id or frame is None:
                return {"success": False, "error": "clip_id and frame are required"}

            # clip_id is used as clip_name in the existing API
            result = add_clip_marker(resolve, str(clip_id), frame, color, name, note, duration, custom_data)
            if result.startswith("Added"):
                return {"success": True, "message": result}
            else:
                return {"success": False, "error": result}

        elif action_lower == "get_all":
            clip_id = p.get("clip_id")
            if not clip_id:
                return {"error": "clip_id is required"}

            # clip_id is used as clip_name in the existing API
            return get_clip_markers(resolve, str(clip_id))

        elif action_lower == "get_by_custom_data":
            clip_id = p.get("clip_id")
            custom_data = p.get("custom_data")
            if not clip_id or not custom_data:
                return {"error": "clip_id and custom_data are required"}

            # Use get_clip_markers and filter by custom_data
            result = get_clip_markers(resolve, str(clip_id))
            if "markers" in result:
                markers = result.get("markers", {})
                matching = {}
                for frame, marker in markers.items():
                    if marker.get("customData") == custom_data:
                        matching[frame] = marker
                return {"markers": matching, "count": len(matching)}
            return result

        elif action_lower == "update_custom_data":
            clip_id = p.get("clip_id")
            frame = p.get("frame")
            custom_data = p.get("custom_data")
            if not clip_id or frame is None or custom_data is None:
                return {"success": False, "error": "clip_id, frame, and custom_data are required"}

            # Find the clip and update marker custom data
            project_manager = resolve.GetProjectManager()
            if not project_manager:
                return {"success": False, "error": "Failed to get Project Manager"}

            current_project = project_manager.GetCurrentProject()
            if not current_project:
                return {"success": False, "error": "No project currently open"}

            media_pool = current_project.GetMediaPool()
            if not media_pool:
                return {"success": False, "error": "Failed to get Media Pool"}

            # Find the clip by clip_id (which should be the clip's unique ID or name)
            target_clip = None
            root_folder = media_pool.GetRootFolder()

            def find_clip_by_id(folder, clip_id):
                clips = folder.GetClipList()
                if clips:
                    for clip in clips:
                        if str(clip.GetUniqueId()) == str(clip_id) or clip.GetName() == str(clip_id):
                            return clip
                subfolders = folder.GetSubFolderList()
                for subfolder in subfolders:
                    result = find_clip_by_id(subfolder, clip_id)
                    if result:
                        return result
                return None

            target_clip = find_clip_by_id(root_folder, clip_id)
            if not target_clip:
                return {"success": False, "error": f"Clip '{clip_id}' not found"}

            try:
                result = target_clip.UpdateMarkerCustomData(frame, custom_data)
                if result:
                    return {"success": True, "message": f"Updated custom data for marker at frame {frame}"}
                else:
                    return {"success": False, "error": f"Failed to update marker at frame {frame}"}
            except Exception as e:
                return {"success": False, "error": f"Error: {str(e)}"}

        elif action_lower == "get_custom_data":
            clip_id = p.get("clip_id")
            frame = p.get("frame")
            if not clip_id or frame is None:
                return {"error": "clip_id and frame are required"}

            # Find the clip
            project_manager = resolve.GetProjectManager()
            if not project_manager:
                return {"error": "Failed to get Project Manager"}

            current_project = project_manager.GetCurrentProject()
            if not current_project:
                return {"error": "No project currently open"}

            media_pool = current_project.GetMediaPool()
            if not media_pool:
                return {"error": "Failed to get Media Pool"}

            target_clip = None
            root_folder = media_pool.GetRootFolder()

            def find_clip_by_id(folder, clip_id):
                clips = folder.GetClipList()
                if clips:
                    for clip in clips:
                        if str(clip.GetUniqueId()) == str(clip_id) or clip.GetName() == str(clip_id):
                            return clip
                subfolders = folder.GetSubFolderList()
                for subfolder in subfolders:
                    result = find_clip_by_id(subfolder, clip_id)
                    if result:
                        return result
                return None

            target_clip = find_clip_by_id(root_folder, clip_id)
            if not target_clip:
                return {"error": f"Clip '{clip_id}' not found"}

            try:
                data = target_clip.GetMarkerCustomData(frame)
                return {"data": data if data else ""}
            except Exception as e:
                return {"error": f"Error: {str(e)}"}

        elif action_lower == "delete_by_color":
            clip_id = p.get("clip_id")
            color = p.get("color")
            if not clip_id or not color:
                return {"success": False, "error": "clip_id and color are required"}

            # Find the clip
            project_manager = resolve.GetProjectManager()
            if not project_manager:
                return {"success": False, "error": "Failed to get Project Manager"}

            current_project = project_manager.GetCurrentProject()
            if not current_project:
                return {"success": False, "error": "No project currently open"}

            media_pool = current_project.GetMediaPool()
            if not media_pool:
                return {"success": False, "error": "Failed to get Media Pool"}

            target_clip = None
            root_folder = media_pool.GetRootFolder()

            def find_clip_by_id(folder, clip_id):
                clips = folder.GetClipList()
                if clips:
                    for clip in clips:
                        if str(clip.GetUniqueId()) == str(clip_id) or clip.GetName() == str(clip_id):
                            return clip
                subfolders = folder.GetSubFolderList()
                for subfolder in subfolders:
                    result = find_clip_by_id(subfolder, clip_id)
                    if result:
                        return result
                return None

            target_clip = find_clip_by_id(root_folder, clip_id)
            if not target_clip:
                return {"success": False, "error": f"Clip '{clip_id}' not found"}

            try:
                # Delete markers by color - need to iterate and delete
                markers = target_clip.GetMarkers()
                deleted_count = 0
                if markers:
                    for frame, marker in markers.items():
                        if marker.get("color") == color:
                            try:
                                target_clip.DeleteMarkerAtFrame(frame)
                                deleted_count += 1
                            except:
                                pass
                return {"success": True, "deleted_count": deleted_count}
            except Exception as e:
                return {"success": False, "error": f"Error: {str(e)}"}

        elif action_lower == "delete_at_frame":
            clip_id = p.get("clip_id")
            frame = p.get("frame")
            if not clip_id or frame is None:
                return {"success": False, "error": "clip_id and frame are required"}

            # Find the clip
            project_manager = resolve.GetProjectManager()
            if not project_manager:
                return {"success": False, "error": "Failed to get Project Manager"}

            current_project = project_manager.GetCurrentProject()
            if not current_project:
                return {"success": False, "error": "No project currently open"}

            media_pool = current_project.GetMediaPool()
            if not media_pool:
                return {"success": False, "error": "Failed to get Media Pool"}

            target_clip = None
            root_folder = media_pool.GetRootFolder()

            def find_clip_by_id(folder, clip_id):
                clips = folder.GetClipList()
                if clips:
                    for clip in clips:
                        if str(clip.GetUniqueId()) == str(clip_id) or clip.GetName() == str(clip_id):
                            return clip
                subfolders = folder.GetSubFolderList()
                for subfolder in subfolders:
                    result = find_clip_by_id(subfolder, clip_id)
                    if result:
                        return result
                return None

            target_clip = find_clip_by_id(root_folder, clip_id)
            if not target_clip:
                return {"success": False, "error": f"Clip '{clip_id}' not found"}

            try:
                result = target_clip.DeleteMarkerAtFrame(frame)
                if result:
                    return {"success": True, "message": f"Deleted marker at frame {frame}"}
                else:
                    return {"success": False, "error": f"No marker found at frame {frame}"}
            except Exception as e:
                return {"success": False, "error": f"Error: {str(e)}"}

        elif action_lower == "delete_by_custom_data":
            clip_id = p.get("clip_id")
            custom_data = p.get("custom_data")
            if not clip_id or not custom_data:
                return {"success": False, "error": "clip_id and custom_data are required"}

            # Find the clip
            project_manager = resolve.GetProjectManager()
            if not project_manager:
                return {"success": False, "error": "Failed to get Project Manager"}

            current_project = project_manager.GetCurrentProject()
            if not current_project:
                return {"success": False, "error": "No project currently open"}

            media_pool = current_project.GetMediaPool()
            if not media_pool:
                return {"success": False, "error": "Failed to get Media Pool"}

            target_clip = None
            root_folder = media_pool.GetRootFolder()

            def find_clip_by_id(folder, clip_id):
                clips = folder.GetClipList()
                if clips:
                    for clip in clips:
                        if str(clip.GetUniqueId()) == str(clip_id) or clip.GetName() == str(clip_id):
                            return clip
                subfolders = folder.GetSubFolderList()
                for subfolder in subfolders:
                    result = find_clip_by_id(subfolder, clip_id)
                    if result:
                        return result
                return None

            target_clip = find_clip_by_id(root_folder, clip_id)
            if not target_clip:
                return {"success": False, "error": f"Clip '{clip_id}' not found"}

            try:
                result = target_clip.DeleteMarkerByCustomData(custom_data)
                if result:
                    return {"success": True, "message": "Deleted marker with specified custom data"}
                else:
                    return {"success": False, "error": "No marker found with specified custom data"}
            except Exception as e:
                return {"success": False, "error": f"Error: {str(e)}"}

        elif action_lower == "add_flag":
            clip_id = p.get("clip_id")
            color = p.get("color")
            if not clip_id or not color:
                return {"success": False, "error": "clip_id and color are required"}

            # Find the clip
            project_manager = resolve.GetProjectManager()
            if not project_manager:
                return {"success": False, "error": "Failed to get Project Manager"}

            current_project = project_manager.GetCurrentProject()
            if not current_project:
                return {"success": False, "error": "No project currently open"}

            media_pool = current_project.GetMediaPool()
            if not media_pool:
                return {"success": False, "error": "Failed to get Media Pool"}

            target_clip = None
            root_folder = media_pool.GetRootFolder()

            def find_clip_by_id(folder, clip_id):
                clips = folder.GetClipList()
                if clips:
                    for clip in clips:
                        if str(clip.GetUniqueId()) == str(clip_id) or clip.GetName() == str(clip_id):
                            return clip
                subfolders = folder.GetSubFolderList()
                for subfolder in subfolders:
                    result = find_clip_by_id(subfolder, clip_id)
                    if result:
                        return result
                return None

            target_clip = find_clip_by_id(root_folder, clip_id)
            if not target_clip:
                return {"success": False, "error": f"Clip '{clip_id}' not found"}

            try:
                result = target_clip.AddFlag(color)
                if result:
                    return {"success": True, "message": f"Added {color} flag"}
                else:
                    return {"success": False, "error": "Failed to add flag"}
            except Exception as e:
                return {"success": False, "error": f"Error: {str(e)}"}

        elif action_lower == "get_flags":
            clip_id = p.get("clip_id")
            if not clip_id:
                return {"error": "clip_id is required"}

            # Find the clip
            project_manager = resolve.GetProjectManager()
            if not project_manager:
                return {"error": "Failed to get Project Manager"}

            current_project = project_manager.GetCurrentProject()
            if not current_project:
                return {"error": "No project currently open"}

            media_pool = current_project.GetMediaPool()
            if not media_pool:
                return {"error": "Failed to get Media Pool"}

            target_clip = None
            root_folder = media_pool.GetRootFolder()

            def find_clip_by_id(folder, clip_id):
                clips = folder.GetClipList()
                if clips:
                    for clip in clips:
                        if str(clip.GetUniqueId()) == str(clip_id) or clip.GetName() == str(clip_id):
                            return clip
                subfolders = folder.GetSubFolderList()
                for subfolder in subfolders:
                    result = find_clip_by_id(subfolder, clip_id)
                    if result:
                        return result
                return None

            target_clip = find_clip_by_id(root_folder, clip_id)
            if not target_clip:
                return {"error": f"Clip '{clip_id}' not found"}

            try:
                flags = target_clip.GetFlags()
                return {"flags": flags if flags else {}}
            except Exception as e:
                return {"error": f"Error: {str(e)}"}

        elif action_lower == "clear_flags":
            clip_id = p.get("clip_id")
            color = p.get("color")  # Optional - if not provided, clear all flags
            if not clip_id:
                return {"success": False, "error": "clip_id is required"}

            # Find the clip
            project_manager = resolve.GetProjectManager()
            if not project_manager:
                return {"success": False, "error": "Failed to get Project Manager"}

            current_project = project_manager.GetCurrentProject()
            if not current_project:
                return {"success": False, "error": "No project currently open"}

            media_pool = current_project.GetMediaPool()
            if not media_pool:
                return {"success": False, "error": "Failed to get Media Pool"}

            target_clip = None
            root_folder = media_pool.GetRootFolder()

            def find_clip_by_id(folder, clip_id):
                clips = folder.GetClipList()
                if clips:
                    for clip in clips:
                        if str(clip.GetUniqueId()) == str(clip_id) or clip.GetName() == str(clip_id):
                            return clip
                subfolders = folder.GetSubFolderList()
                for subfolder in subfolders:
                    result = find_clip_by_id(subfolder, clip_id)
                    if result:
                        return result
                return None

            target_clip = find_clip_by_id(root_folder, clip_id)
            if not target_clip:
                return {"success": False, "error": f"Clip '{clip_id}' not found"}

            try:
                if color:
                    result = target_clip.ClearFlags(color)
                else:
                    result = target_clip.ClearFlags()
                if result:
                    return {"success": True, "message": "Cleared flags"}
                else:
                    return {"success": False, "error": "Failed to clear flags"}
            except Exception as e:
                return {"success": False, "error": f"Error: {str(e)}"}

        else:
            valid = [
                "add", "get_all", "get_by_custom_data", "update_custom_data",
                "get_custom_data", "delete_by_color", "delete_at_frame",
                "delete_by_custom_data", "add_flag", "get_flags", "clear_flags"
            ]
            return {"error": f"Unknown action '{action}'. Valid actions: {', '.join(valid)}"}

    logger.info("Registered media pool item markers tools")