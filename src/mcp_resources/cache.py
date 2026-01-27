#!/usr/bin/env python3
"""
DaVinci Resolve MCP Resources - Cache related resources
"""

from typing import Dict, Any


def register_cache_resources(mcp, resolve, logger):
    """Register cache-related resources."""

    @mcp.resource("resolve://cache/settings")
    def get_cache_settings() -> Dict[str, Any]:
        """Get current cache settings from the project.

        Returns:
            Dict[str, Any]: A dictionary containing cache settings.
        """
        if resolve is None:
            return {"error": "Not connected to DaVinci Resolve"}

        project_manager = resolve.GetProjectManager()
        if not project_manager:
            return {"error": "Failed to get Project Manager"}

        current_project = project_manager.GetCurrentProject()
        if not current_project:
            return {"error": "No project currently open"}

        try:
            settings = {}
            cache_keys = [
                "CacheMode",
                "CacheClipMode",
                "OptimizedMediaMode",
                "ProxyMode",
                "ProxyQuality",
                "TimelineCacheMode",
                "LocalCachePath",
                "NetworkCachePath",
            ]

            for key in cache_keys:
                value = current_project.GetSetting(key)
                settings[key] = value

            return settings
        except Exception as e:
            return {"error": f"Failed to get cache settings: {str(e)}"}

    logger.info("Cache resources registered")
