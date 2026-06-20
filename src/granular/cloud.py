#!/usr/bin/env python3
"""DaVinci Resolve MCP - Cloud Operations (Granular Tools)."""

from typing import Any, Dict, List, Optional, Union, Tuple
from .common import mcp, get_resolve

@mcp.tool()
def create_cloud_project_tool(project_name: str, folder_path: str = None) -> Dict[str, Any]:
    """Create a new cloud project.
    
    Args:
        project_name: Name for the new cloud project
        folder_path: Optional path for the cloud project folder
    """
    resolve = get_resolve()
    if resolve is None:
        return {"error": "Not connected to DaVinci Resolve", "success": False}
    
    return create_cloud_project(resolve, project_name, folder_path)

@mcp.tool()
def import_cloud_project_tool(cloud_id: str, project_name: str = None) -> Dict[str, Any]:
    """Import a project from DaVinci Resolve cloud.
    
    Args:
        cloud_id: Cloud ID or reference of the project to import
        project_name: Optional custom name for the imported project (uses original name if None)
    """
    resolve = get_resolve()
    if resolve is None:
        return {"error": "Not connected to DaVinci Resolve", "success": False}
    
    return import_cloud_project(resolve, cloud_id, project_name)

@mcp.tool()
def restore_cloud_project_tool(cloud_id: str, project_name: str = None) -> Dict[str, Any]:
    """Restore a project from DaVinci Resolve cloud.
    
    Args:
        cloud_id: Cloud ID or reference of the project to restore
        project_name: Optional custom name for the restored project (uses original name if None)
    """
    resolve = get_resolve()
    if resolve is None:
        return {"error": "Not connected to DaVinci Resolve", "success": False}
    
    return restore_cloud_project(resolve, cloud_id, project_name)

@mcp.tool()
def export_project_to_cloud_tool(project_name: str = None) -> Dict[str, Any]:
    """Export current or specified project to DaVinci Resolve cloud.
    
    Args:
        project_name: Optional name of project to export (uses current project if None)
    """
    resolve = get_resolve()
    if resolve is None:
        return {"error": "Not connected to DaVinci Resolve", "success": False}
    
    return export_project_to_cloud(resolve, project_name)

@mcp.tool()
def add_user_to_cloud_project_tool(cloud_id: str, user_email: str, permissions: str = "viewer") -> Dict[str, Any]:
    """Add a user to a cloud project with specified permissions.
    
    Args:
        cloud_id: Cloud ID of the project
        user_email: Email of the user to add
        permissions: Permission level (viewer, editor, admin)
    """
    resolve = get_resolve()
    if resolve is None:
        return {"error": "Not connected to DaVinci Resolve", "success": False}
    
    return add_user_to_cloud_project(resolve, cloud_id, user_email, permissions)

@mcp.tool()
def remove_user_from_cloud_project_tool(cloud_id: str, user_email: str) -> Dict[str, Any]:
    """Remove a user from a cloud project.
    
    Args:
        cloud_id: Cloud ID of the project
        user_email: Email of the user to remove
    """
    resolve = get_resolve()
    if resolve is None:
        return {"error": "Not connected to DaVinci Resolve", "success": False}
    
    return remove_user_from_cloud_project(resolve, cloud_id, user_email)

# ------------------
# Project Properties
# ------------------

@mcp.resource("resolve://project/properties")
def get_project_properties_endpoint() -> Dict[str, Any]:
    """Get all project properties for the current project."""
    pm, current_project = get_current_project()
    if not current_project:
        return {"error": "No project currently open"}
    
    return get_all_project_properties(current_project)

@mcp.resource("resolve://project/property/{property_name}")
def get_project_property_endpoint(property_name: str) -> Dict[str, Any]:
    """Get a specific project property value.
    
    Args:
        property_name: Name of the property to get
    """
    pm, current_project = get_current_project()
    if not current_project:
        return {"error": "No project currently open"}
    
    value = get_project_property(current_project, property_name)
    return {property_name: value}

