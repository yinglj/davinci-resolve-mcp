#!/usr/bin/env python3
"""
DaVinci Resolve MCP Resources - Delivery related resources
"""

from typing import List, Dict, Any


def register_delivery_resources(mcp, resolve, logger):
    """Register delivery-related resources."""

    @mcp.resource("resolve://delivery/render-presets")
    def get_render_presets() -> List[Dict[str, Any]]:
        """Get all available render presets in the current project."""
        try:
            from src.api.delivery_operations import (
                get_render_presets as get_presets_func,
            )
        except ImportError:
            return [{"error": "Could not import delivery operations"}]

        return get_presets_func(resolve)

    @mcp.resource("resolve://delivery/render-queue/status")
    def get_render_queue_status() -> Dict[str, Any]:
        """Get the status of jobs in the render queue."""
        try:
            from src.api.delivery_operations import (
                get_render_queue_status as get_status_func,
            )
        except ImportError:
            return {"error": "Could not import delivery operations"}

        return get_status_func(resolve)

    logger.info("Delivery resources registered")
