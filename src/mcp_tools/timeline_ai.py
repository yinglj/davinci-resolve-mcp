#!/usr/bin/env python3
"""
DaVinci Resolve MCP Timeline AI Tools
AI and analysis operations on timelines
"""

from typing import Dict, Any, Optional


def _get_tl(resolve):
    """Get current timeline from resolve object."""
    project_manager = resolve.GetProjectManager()
    if not project_manager:
        return None, {"error": "Failed to get Project Manager"}

    current_project = project_manager.GetCurrentProject()
    if not current_project:
        return None, {"error": "No project open"}

    current_timeline = current_project.GetCurrentTimeline()
    if not current_timeline:
        return None, {"error": "No current timeline"}

    return current_timeline, None


def _unknown(action, valid):
    """Return error for unknown action."""
    return {"error": f"Unknown action '{action}'. Valid actions: {', '.join(valid)}"}


def register_timeline_ai_tools(mcp, resolve, logger):
    """Register timeline AI MCP tools."""

    @mcp.tool()
    def timeline_ai(action: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """AI and analysis operations on the current timeline.

        Actions:
          create_subtitles(settings?) -> {success}  — auto-caption from audio
          detect_scene_cuts() -> {success}
          analyze_dolby_vision(clip_ids?, analysis_type?) -> {success}
          grab_still() -> {success}
          grab_all_stills(source?) -> {count}
        """
        if resolve is None:
            return {"error": "Not connected to DaVinci Resolve"}

        p = params or {}
        tl, err = _get_tl(resolve)
        if err:
            return err

        if action == "create_subtitles":
            return {"success": bool(tl.CreateSubtitlesFromAudio(p.get("settings", {})))}
        elif action == "detect_scene_cuts":
            return {"success": bool(tl.DetectSceneCuts())}
        elif action == "analyze_dolby_vision":
            clip_ids = p.get("clip_ids", [])
            items = []
            if clip_ids:
                for tt in ["video"]:
                    for ti in range(1, tl.GetTrackCount(tt) + 1):
                        for it in (tl.GetItemListInTrack(tt, ti) or []):
                            if it.GetUniqueId() in clip_ids:
                                items.append(it)
            analysis_type = p.get("analysis_type")
            if items:
                return {"success": bool(tl.AnalyzeDolbyVision(items, analysis_type))}
            return {"success": bool(tl.AnalyzeDolbyVision())}
        elif action == "grab_still":
            still = tl.GrabStill()
            return {"success": still is not None}
        elif action == "grab_all_stills":
            stills = tl.GrabAllStills(p.get("source", 1))
            return {"count": len(stills) if stills else 0}
        return _unknown(action, ["create_subtitles", "detect_scene_cuts", "analyze_dolby_vision", "grab_still", "grab_all_stills"])

    logger.info("Registered timeline AI tools")