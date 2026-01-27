#!/usr/bin/env python3
"""
DaVinci Resolve MCP Object Inspection Tools
Inspect API objects and get help on their methods
"""

from typing import Dict, Any

from src.utils.object_inspection import (
    inspect_object,
    print_object_help,
)


def register_inspection_tools(mcp, resolve, logger):
    """Register object inspection MCP tools."""

    @mcp.tool()
    def object_help(object_type: str) -> str:
        """Get human-readable help for a DaVinci Resolve API object.

        Args:
            object_type: Type of object to get help for ('resolve', 'project_manager',
                         'project', 'media_pool', 'timeline', 'media_storage').

        Returns:
            str: A string containing the help text for the specified object.
        """
        if resolve is None:
            return "Error: Not connected to DaVinci Resolve"

        obj = None

        if object_type == "resolve":
            obj = resolve
        elif object_type == "project_manager":
            obj = resolve.GetProjectManager()
        elif object_type == "project":
            pm = resolve.GetProjectManager()
            if pm:
                obj = pm.GetCurrentProject()
        elif object_type == "media_pool":
            pm = resolve.GetProjectManager()
            if pm:
                project = pm.GetCurrentProject()
                if project:
                    obj = project.GetMediaPool()
        elif object_type == "timeline":
            pm = resolve.GetProjectManager()
            if pm:
                project = pm.GetCurrentProject()
                if project:
                    obj = project.GetCurrentTimeline()
        elif object_type == "media_storage":
            obj = resolve.GetMediaStorage()
        else:
            return f"Error: Unknown object type '{object_type}'"

        if obj is None:
            return f"Error: Failed to get {object_type} object"

        return print_object_help(obj)

    @mcp.tool()
    def inspect_custom_object(object_path: str) -> Dict[str, Any]:
        """Inspect a custom DaVinci Resolve API object by path.

        Args:
            object_path: Path to the object using dot notation
                         (e.g., 'resolve.GetMediaStorage()').

        Returns:
            Dict[str, Any]: A dictionary containing the methods and properties of the custom object.
        """
        if resolve is None:
            return {"error": "Not connected to DaVinci Resolve"}

        try:
            obj = resolve

            parts = object_path.split(".")

            start_index = 1 if parts[0].lower() == "resolve" else 0

            for i in range(start_index, len(parts)):
                part = parts[i]

                if part.endswith("()"):
                    method_name = part[:-2]
                    if hasattr(obj, method_name) and callable(
                        getattr(obj, method_name)
                    ):
                        obj = getattr(obj, method_name)()
                    else:
                        return {
                            "error": f"Method '{method_name}' not found or not callable"
                        }
                else:
                    if hasattr(obj, part):
                        obj = getattr(obj, part)
                    else:
                        return {"error": f"Attribute '{part}' not found"}

            return inspect_object(obj)
        except Exception as e:
            return {"error": f"Error inspecting object: {str(e)}"}

    logger.info("Registered inspection tools")
