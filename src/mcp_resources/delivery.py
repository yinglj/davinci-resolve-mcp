#!/usr/bin/env python3
"""
DaVinci Resolve MCP Resources - Delivery related resources
"""

from typing import Any

from fastmcp.resources import ResourceContent, ResourceResult


def register_delivery_resources(mcp, resolve, logger):
    """Register delivery-related resources."""

    def to_resource_result(payload: Any) -> ResourceResult:
        return ResourceResult([ResourceContent(payload)])

    @mcp.resource("resolve://delivery/render-presets")
    def get_render_presets() -> ResourceResult:
        """Get all available render presets in the current project."""
        try:
            from src.api.delivery import (
                get_render_presets as get_presets_func,
            )
        except ImportError:
            return to_resource_result(
                [{"error": "Could not import delivery operations"}]
            )

        return to_resource_result(get_presets_func(resolve))

    @mcp.resource("resolve://delivery/render-queue/status")
    def get_render_queue_status() -> ResourceResult:
        """Get the status of jobs in the render queue."""
        try:
            from src.api.delivery import (
                get_render_queue_status as get_status_func,
            )
        except ImportError:
            return to_resource_result({"error": "Could not import delivery operations"})

        return to_resource_result(get_status_func(resolve))

    logger.info("Delivery resources registered")
