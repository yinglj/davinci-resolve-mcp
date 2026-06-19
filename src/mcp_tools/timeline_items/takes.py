#!/usr/bin/env python3
"""
DaVinci Resolve MCP Timeline Item Takes Tools
Take management on timeline items
"""

from typing import Dict, Any, Optional

from .properties import find_timeline_item


def _get_item_params(params):
    """Extract timeline item identification parameters from params dict."""
    return {
        "track_type": params.get("track_type", "video"),
        "track_index": params.get("track_index", 1),
        "item_index": params.get("item_index", 0),
        "timeline_item_id": params.get("timeline_item_id"),
    }


def _unknown(action, valid):
    """Return error for unknown action."""
    return {"error": f"Unknown action '{action}'. Valid actions: {', '.join(valid)}"}


def register_timeline_item_takes_tools(mcp, resolve, logger):
    """Register timeline item takes MCP tools."""

    @mcp.tool()
    def timeline_item_takes(
        action: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Take management on timeline items.

        Identify by track_type, track_index, item_index.
        Default: track_type="video", track_index=1, item_index=0

        Actions:
            add(clip_id, start_frame?, end_frame?, ...) -> {success}
            get_count(...) -> {count}
            get_selected_index(...) -> {index}
            get_by_index(index, ...) -> {take}
            select(index, ...) -> {success}
            delete(index, ...) -> {success}
            finalize(...) -> {success}

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

        p = params or {}
        item_params = _get_item_params(p)

        # Resolve timeline item
        timeline_item = None
        if item_params["timeline_item_id"]:
            timeline_item, _ = find_timeline_item(
                current_timeline,
                item_params["timeline_item_id"],
                search_video=True,
                search_audio=True,
            )
        else:
            track_type = item_params["track_type"]
            track_index = item_params["track_index"]
            item_index = item_params["item_index"]
            items = current_timeline.GetItemListInTrack(track_type, track_index) or []
            if 0 <= item_index < len(items):
                timeline_item = items[item_index]

        if not timeline_item:
            return {"error": f"Timeline item not found at track={item_params['track_index']}, index={item_params['item_index']}"}

        try:
            if action == "add":
                return _takes_add(resolve, timeline_item, p)
            elif action == "get_count":
                return {"count": timeline_item.GetTakesCount()}
            elif action == "get_selected_index":
                return {"index": timeline_item.GetSelectedTakeIndex()}
            elif action == "get_by_index":
                index = p.get("index")
                if index is None:
                    return {"error": "index parameter is required for get_by_index"}
                take = timeline_item.GetTakeByIndex(index)
                return {"take": take} if take else {"take": None}
            elif action == "select":
                index = p.get("index")
                if index is None:
                    return {"error": "index parameter is required for select"}
                return {"success": bool(timeline_item.SelectTakeByIndex(index))}
            elif action == "delete":
                index = p.get("index")
                if index is None:
                    return {"error": "index parameter is required for delete"}
                return {"success": bool(timeline_item.DeleteTakeByIndex(index))}
            elif action == "finalize":
                return {"success": bool(timeline_item.FinalizeTake())}
            else:
                return _unknown(action, ["add", "get_count", "get_selected_index", "get_by_index", "select", "delete", "finalize"])
        except Exception as e:
            return {"error": f"Error executing {action}: {str(e)}"}

    def _takes_add(resolve, timeline_item, params):
        """Add a take to the timeline item."""
        clip_id = params.get("clip_id")
        if not clip_id:
            return {"error": "clip_id parameter is required for add"}

        project_manager = resolve.GetProjectManager()
        current_project = project_manager.GetCurrentProject()
        mp = current_project.GetMediaPool()
        if not mp:
            return {"error": "Failed to get MediaPool"}

        root = mp.GetRootFolder()
        clip = _find_clip_in_folder(root, clip_id)
        if not clip:
            return {"error": f"Clip not found: {clip_id}"}

        start_frame = params.get("start_frame", 0)
        end_frame = params.get("end_frame", 0)
        return {"success": bool(timeline_item.AddTake(clip, start_frame, end_frame))}

    logger.info("Registered timeline item takes tools")


def _find_clip_in_folder(folder, clip_id):
    """Recursively find a clip by ID in a folder and its subfolders."""
    for clip in (folder.GetClipList() or []):
        if clip.GetUniqueId() == clip_id:
            return clip
    for sub in (folder.GetSubFolderList() or []):
        found = _find_clip_in_folder(sub, clip_id)
        if found:
            return found
    return None
