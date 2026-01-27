#!/usr/bin/env python3
"""
DaVinci Resolve MCP Resources - Project related resources
"""

from typing import List, Dict, Any


def register_project_resources(mcp, resolve, logger):
    """Register project-related resources."""

    @mcp.resource("resolve://projects")
    def list_projects() -> List[str]:
        """List all available projects in the current database."""
        if resolve is None:
            return ["Error: Not connected to DaVinci Resolve"]

        project_manager = resolve.GetProjectManager()
        if not project_manager:
            return ["Error: Failed to get Project Manager"]

        projects = project_manager.GetProjectListInCurrentFolder()
        return [p for p in projects if p]

    @mcp.resource("resolve://current-project")
    def get_current_project_name() -> str:
        """Get the name of the currently open project."""
        if resolve is None:
            return "Error: Not connected to DaVinci Resolve"

        project_manager = resolve.GetProjectManager()
        if not project_manager:
            return "Error: Failed to get Project Manager"

        current_project = project_manager.GetCurrentProject()
        if not current_project:
            return "No project currently open"

        return current_project.GetName()

    @mcp.resource("resolve://project-settings")
    def get_project_settings() -> Dict[str, Any]:
        """Get all project settings from the current project."""
        if resolve is None:
            return {"error": "Not connected to DaVinci Resolve"}

        project_manager = resolve.GetProjectManager()
        if not project_manager:
            return {"error": "Failed to get Project Manager"}

        current_project = project_manager.GetCurrentProject()
        if not current_project:
            return {"error": "No project currently open"}

        try:
            return current_project.GetSetting("")
        except Exception as e:
            return {"error": f"Failed to get project settings: {str(e)}"}

    @mcp.resource("resolve://project-setting/{setting_name}")
    def get_project_setting(setting_name: str) -> Dict[str, Any]:
        """Get a specific project setting by name."""
        if resolve is None:
            return {"error": "Not connected to DaVinci Resolve"}

        project_manager = resolve.GetProjectManager()
        if not project_manager:
            return {"error": "Failed to get Project Manager"}

        current_project = project_manager.GetCurrentProject()
        if not current_project:
            return {"error": "No project currently open"}

        try:
            value = current_project.GetSetting(setting_name)
            return {setting_name: value}
        except Exception as e:
            return {
                "error": f"Failed to get project setting '{setting_name}': {str(e)}"
            }

    logger.info("Project resources registered")
