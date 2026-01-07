"""
DaVinci Resolve MCP - Advanced Timeline Tools
Ported from robgrappler/claude branch
"""

from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger("davinci-resolve-mcp.api.extra.timeline_advanced")

try:
    from ...resolve_mcp_server import (
        get_resolve,
        get_project_manager,
        get_current_project,
        get_current_timeline,
    )
except ImportError:
    # Fallback
    def get_resolve():
        return None

    def get_project_manager():
        return None

    def get_current_project():
        return None

    def get_current_timeline():
        return None


def export_timeline(
    file_path: str, export_type: str, export_subtype: Optional[str] = None
) -> Dict[str, Any]:
    """Export timeline to various formats (AAF, EDL, XML, FCP XML, etc.)."""
    timeline = get_current_timeline()
    if not timeline:
        return {"success": False, "error": "No timeline active"}

    try:
        # map export type string to Resolve constant if needed
        # For simplicity, pass directly as Resolve API supports strings for these
        result = timeline.Export(file_path, export_type, export_subtype or "")
        return {
            "success": bool(result),
            "file_path": file_path,
            "export_type": export_type,
            "message": f"Timeline {'exported' if result else 'export failed'}",
        }
    except Exception as e:
        logger.error(f"Error exporting timeline: {e}")
        return {"success": False, "error": str(e)}


def duplicate_timeline(timeline_name: str) -> Dict[str, Any]:
    """Duplicate the current timeline with a new name."""
    timeline = get_current_timeline()
    project = get_current_project()
    if not timeline or not project:
        return {"success": False, "error": "No timeline/project active"}

    try:
        result = project.DuplicateTimeline(timeline, timeline_name)
        return {
            "success": bool(result),
            "new_timeline_name": timeline_name,
            "message": f"Timeline {'duplicated' if result else 'duplication failed'}",
        }
    except Exception as e:
        logger.error(f"Error duplicating timeline: {e}")
        return {"success": False, "error": str(e)}


def insert_fusion_title(title_name: str) -> Dict[str, Any]:
    """Insert a Fusion title into the timeline."""
    timeline = get_current_timeline()
    if not timeline:
        return {"success": False, "error": "No timeline active"}

    try:
        result = timeline.InsertFusionTitleIntoTimeline(title_name)
        return {"success": bool(result), "title_name": title_name}
    except Exception as e:
        logger.error(f"Error inserting Fusion title: {e}")
        return {"success": False, "error": str(e)}


def register_tools(proxy):
    """Register tools with the proxy."""
    proxy.register_tool(
        "export_timeline",
        export_timeline,
        "timeline",
        "Export timeline to various formats (AAF, EDL, XML, FCP XML, DRT)",
        {
            "file_path": {"type": "string", "description": "Destination file path"},
            "export_type": {
                "type": "string",
                "description": "Export format (AAF, EDL, FCPXML_1_10, etc.)",
            },
        },
    )
    proxy.register_tool(
        "duplicate_timeline",
        duplicate_timeline,
        "timeline",
        "Duplicate the current timeline with a new name",
        {"timeline_name": {"type": "string", "description": "New timeline name"}},
    )
    proxy.register_tool(
        "insert_fusion_title",
        insert_fusion_title,
        "fusion",
        "Insert a Fusion title into the timeline",
        {"title_name": {"type": "string", "description": "Fusion title name"}},
    )
    return 3
