#!/usr/bin/env python3
"""
DaVinci Resolve MCP Resources - Cloud Project related resources
"""

from typing import Any

from fastmcp.resources import ResourceContent, ResourceResult
from src.utils.cloud_operations import get_cloud_project_list


def register_cloud_resources(mcp, resolve, logger):
    """Register cloud project-related resources."""

    def to_resource_result(payload: Any) -> ResourceResult:
        return ResourceResult([ResourceContent(payload)])

    @mcp.resource("resolve://cloud/projects")
    def get_cloud_projects() -> ResourceResult:
        """Get list of available cloud projects.

        Returns:
            Dict[str, Any]: A dictionary containing the list of cloud projects.
        """
        if resolve is None:
            return to_resource_result(
                {"error": "Not connected to DaVinci Resolve", "success": False}
            )

        return to_resource_result(get_cloud_project_list(resolve))

    logger.info("Cloud resources registered")
