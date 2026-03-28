#!/usr/bin/env python3
"""
DaVinci Resolve MCP Resources - Project related resources
"""

from typing import Any

from fastmcp.resources import ResourceContent, ResourceResult


def register_project_resources(mcp, resolve, logger):
    """Register project-related resources."""

    def to_resource_result(payload: Any) -> ResourceResult:
        return ResourceResult([ResourceContent(payload)])

    @mcp.resource("resolve://projects")
    def list_projects() -> ResourceResult:
        """List all available projects in the current database."""
        if resolve is None:
            return to_resource_result("Error: Not connected to DaVinci Resolve")

        project_manager = resolve.GetProjectManager()
        if not project_manager:
            return to_resource_result("Error: Failed to get Project Manager")

        projects = project_manager.GetProjectListInCurrentFolder()
        return to_resource_result([p for p in projects if p])

    @mcp.resource("resolve://current-project")
    def get_current_project_name() -> ResourceResult:
        """Get the name of the currently open project."""
        if resolve is None:
            return to_resource_result("Error: Not connected to DaVinci Resolve")

        project_manager = resolve.GetProjectManager()
        if not project_manager:
            return to_resource_result("Error: Failed to get Project Manager")

        current_project = project_manager.GetCurrentProject()
        if not current_project:
            return to_resource_result("No project currently open")

        return to_resource_result(current_project.GetName())

    @mcp.resource("resolve://project-settings")
    def get_project_settings() -> ResourceResult:
        """Get all project settings from the current project."""
        if resolve is None:
            return to_resource_result({"error": "Not connected to DaVinci Resolve"})

        project_manager = resolve.GetProjectManager()
        if not project_manager:
            return to_resource_result({"error": "Failed to get Project Manager"})

        current_project = project_manager.GetCurrentProject()
        if not current_project:
            return to_resource_result({"error": "No project currently open"})

        try:
            return to_resource_result(current_project.GetSetting(""))
        except Exception as e:
            return to_resource_result(
                {"error": f"Failed to get project settings: {str(e)}"}
            )

    @mcp.resource("resolve://project-setting/{setting_name}")
    def get_project_setting(setting_name: str) -> ResourceResult:
        """Get a specific project setting by name."""
        if resolve is None:
            return to_resource_result({"error": "Not connected to DaVinci Resolve"})

        project_manager = resolve.GetProjectManager()
        if not project_manager:
            return to_resource_result({"error": "Failed to get Project Manager"})

        current_project = project_manager.GetCurrentProject()
        if not current_project:
            return to_resource_result({"error": "No project currently open"})

        try:
            value = current_project.GetSetting(setting_name)
            return to_resource_result({setting_name: value})
        except Exception as e:
            return to_resource_result(
                {"error": (f"Failed to get project setting '{setting_name}': {str(e)}")}
            )

    logger.info("Project resources registered")
