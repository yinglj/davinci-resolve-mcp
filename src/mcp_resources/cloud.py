#!/usr/bin/env python3
"""
DaVinci Resolve MCP Resources - Cloud Project related resources
"""

from typing import Dict, Any
from src.utils.cloud_operations import get_cloud_project_list


def register_cloud_resources(mcp, resolve, logger):
    """Register cloud project-related resources."""

    @mcp.resource("resolve://cloud/projects")
    def get_cloud_projects() -> Dict[str, Any]:
        """Get list of available cloud projects.

        Returns:
            Dict[str, Any]: A dictionary containing the list of cloud projects.
        """
        if resolve is None:
            return {"error": "Not connected to DaVinci Resolve", "success": False}

        return get_cloud_project_list(resolve)

    logger.info("Cloud resources registered")
