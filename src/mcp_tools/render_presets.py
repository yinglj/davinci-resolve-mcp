#!/usr/bin/env python3
"""
DaVinci Resolve MCP Render Presets Tools
Import/export render and burn-in presets
"""

import os
from typing import Dict, Any, Optional


def register_render_presets_tools(mcp, resolve, logger):
    """Register render presets MCP tools."""

    @mcp.tool()
    def render_presets(action: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Import/export render and burn-in presets.

        Actions:
          import_render(path) -> {success}
          export_render(name, path) -> {success}
          import_burnin(path) -> {success}
          export_burnin(name, path) -> {success}
        """
        if resolve is None:
            return {"success": False, "error": "Not connected to DaVinci Resolve"}

        p = params or {}
        action_lower = action.lower()

        if action_lower == "import_render":
            path = p.get("path")
            if not path:
                return {"success": False, "error": "path is required"}
            if not os.path.exists(path):
                return {"success": False, "error": f"File '{path}' does not exist"}
            try:
                result = resolve.ImportRenderPreset(path)
                return {"success": bool(result)}
            except Exception as e:
                return {"success": False, "error": f"Error importing render preset: {str(e)}"}

        elif action_lower == "export_render":
            name = p.get("name")
            path = p.get("path")
            if not name:
                return {"success": False, "error": "name is required"}
            if not path:
                return {"success": False, "error": "path is required"}
            try:
                result = resolve.ExportRenderPreset(name, path)
                return {"success": bool(result)}
            except Exception as e:
                return {"success": False, "error": f"Error exporting render preset: {str(e)}"}

        elif action_lower == "import_burnin":
            path = p.get("path")
            if not path:
                return {"success": False, "error": "path is required"}
            if not os.path.exists(path):
                return {"success": False, "error": f"File '{path}' does not exist"}
            try:
                result = resolve.ImportBurnInPreset(path)
                return {"success": bool(result)}
            except Exception as e:
                return {"success": False, "error": f"Error importing burn-in preset: {str(e)}"}

        elif action_lower == "export_burnin":
            name = p.get("name")
            path = p.get("path")
            if not name:
                return {"success": False, "error": "name is required"}
            if not path:
                return {"success": False, "error": "path is required"}
            try:
                result = resolve.ExportBurnInPreset(name, path)
                return {"success": bool(result)}
            except Exception as e:
                return {"success": False, "error": f"Error exporting burn-in preset: {str(e)}"}

        else:
            valid = ["import_render", "export_render", "import_burnin", "export_burnin"]
            return {"success": False, "error": f"Unknown action '{action}'. Valid actions: {', '.join(valid)}"}

    logger.info("Registered render presets tools")