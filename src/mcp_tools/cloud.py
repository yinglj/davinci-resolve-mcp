#!/usr/bin/env python3
"""
DaVinci Resolve MCP Cloud Project Tools
Cloud project operations including create, load, import, and restore
"""

from typing import Any, Dict, Optional

from src.utils.cloud_operations import (
    create_cloud_project,
    load_cloud_project,
    import_cloud_project,
    restore_cloud_project,
)


def register_cloud_tools(mcp, resolve, logger):
    """Register cloud project MCP tools."""

    @mcp.tool()
    def create_cloud_project_tool(
        project_name: str,
        project_media_path: Optional[str] = None,
        is_collab: Optional[bool] = None,
        sync_mode: Optional[str] = None,
        is_camera_access: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """Create a new cloud project.

        Args:
            project_name: Name for the new cloud project
            project_media_path: Optional media path for the project
            is_collab: Whether the project is a collaboration project
            sync_mode: Sync mode ('none', 'proxy_only', 'proxy_and_orig')
            is_camera_access: Whether to enable camera access

        Returns:
            Dict[str, Any]: A dictionary containing the result of the operation.
        """
        if resolve is None:
            return {"error": "Not connected to DaVinci Resolve", "success": False}

        return create_cloud_project(
            resolve,
            project_name=project_name,
            project_media_path=project_media_path,
            is_collab=is_collab,
            sync_mode=sync_mode,
            is_camera_access=is_camera_access,
        )

    @mcp.tool()
    def load_cloud_project_tool(
        project_name: str,
        project_media_path: Optional[str] = None,
        sync_mode: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Load an existing cloud project.

        Args:
            project_name: Name of the cloud project to load
            project_media_path: Optional media path
            sync_mode: Sync mode ('none', 'proxy_only', 'proxy_and_orig')

        Returns:
            Dict[str, Any]: A dictionary containing the result of the operation.
        """
        if resolve is None:
            return {"error": "Not connected to DaVinci Resolve", "success": False}

        return load_cloud_project(
            resolve,
            project_name=project_name,
            project_media_path=project_media_path,
            sync_mode=sync_mode,
        )

    @mcp.tool()
    def import_cloud_project_tool(
        file_path: str,
        project_name: Optional[str] = None,
        project_media_path: Optional[str] = None,
        is_collab: Optional[bool] = None,
        sync_mode: Optional[str] = None,
        is_camera_access: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """Import a cloud project from a file.

        Args:
            file_path: Path to the cloud project file
            project_name: Optional custom name for the imported project
            project_media_path: Optional media path
            is_collab: Whether the project is a collaboration project
            sync_mode: Sync mode ('none', 'proxy_only', 'proxy_and_orig')
            is_camera_access: Whether to enable camera access

        Returns:
            Dict[str, Any]: A dictionary containing the result of the operation.
        """
        if resolve is None:
            return {"error": "Not connected to DaVinci Resolve", "success": False}

        return import_cloud_project(
            resolve,
            file_path=file_path,
            project_name=project_name,
            project_media_path=project_media_path,
            is_collab=is_collab,
            sync_mode=sync_mode,
            is_camera_access=is_camera_access,
        )

    @mcp.tool()
    def restore_cloud_project_tool(
        folder_path: str,
        project_name: Optional[str] = None,
        project_media_path: Optional[str] = None,
        is_collab: Optional[bool] = None,
        sync_mode: Optional[str] = None,
        is_camera_access: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """Restore a cloud project from a folder.

        Args:
            folder_path: Path to the cloud project folder
            project_name: Optional custom name for the restored project
            project_media_path: Optional media path
            is_collab: Whether the project is a collaboration project
            sync_mode: Sync mode ('none', 'proxy_only', 'proxy_and_orig')
            is_camera_access: Whether to enable camera access

        Returns:
            Dict[str, Any]: A dictionary containing the result of the operation.
        """
        if resolve is None:
            return {"error": "Not connected to DaVinci Resolve", "success": False}

        return restore_cloud_project(
            resolve,
            folder_path=folder_path,
            project_name=project_name,
            project_media_path=project_media_path,
            is_collab=is_collab,
            sync_mode=sync_mode,
            is_camera_access=is_camera_access,
        )

    logger.info("Registered cloud tools")
