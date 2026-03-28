#!/usr/bin/env python3
"""
DaVinci Resolve MCP Resources - Preset related resources
"""

from typing import Any

from fastmcp.resources import ResourceContent, ResourceResult


def register_preset_resources(mcp, resolve, logger):
    """Register preset-related (LUTs, Color Presets) resources."""

    def to_resource_result(payload: Any) -> ResourceResult:
        return ResourceResult([ResourceContent(payload)])

    @mcp.resource("resolve://color/lut-formats")
    def get_lut_formats() -> ResourceResult:
        """Get available LUT export formats and sizes."""
        return to_resource_result(
            {
                "formats": [
                    {
                        "name": "Cube",
                        "extension": ".cube",
                        "description": "Industry standard LUT format",
                    },
                    {
                        "name": "Davinci",
                        "extension": ".ilut",
                        "description": "DaVinci Resolve native format",
                    },
                    {
                        "name": "3dl",
                        "extension": ".3dl",
                        "description": "ASSIMILATE SCRATCH format",
                    },
                    {
                        "name": "Panasonic",
                        "extension": ".vlut",
                        "description": "Panasonic VariCam format",
                    },
                ],
                "sizes": [
                    {"name": "17Point", "description": "Smaller file size (17x17x17)"},
                    {"name": "33Point", "description": "Standard size (33x33x33)"},
                    {"name": "65Point", "description": "Highest precision (65x65x65)"},
                ],
            }
        )

    @mcp.resource("resolve://color/presets")
    def get_color_presets() -> ResourceResult:
        """Get all available color presets in the current project."""
        if resolve is None:
            return to_resource_result([{"error": "Not connected to DaVinci Resolve"}])

        project_manager = resolve.GetProjectManager()
        if not project_manager:
            return to_resource_result([{"error": "Failed to get Project Manager"}])

        current_project = project_manager.GetCurrentProject()
        if not current_project:
            return to_resource_result([{"error": "No project currently open"}])

        current_page = resolve.GetCurrentPage()
        if current_page != "color":
            resolve.OpenPage("color")

        try:
            gallery = current_project.GetGallery()
            if not gallery:
                return to_resource_result([{"error": "Failed to get gallery"}])

            albums = gallery.GetAlbums()
            if not albums:
                return to_resource_result([{"info": "No albums found in gallery"}])

            result = []
            for album in albums:
                stills = album.GetStills()
                album_info = {"name": album.GetName(), "stills": []}

                if stills:
                    for still in stills:
                        still_info = {
                            "id": still.GetUniqueId(),
                            "label": still.GetLabel(),
                            "timecode": still.GetTimecode(),
                            "isGrabbed": still.IsGrabbed(),
                        }
                        album_info["stills"].append(still_info)

                result.append(album_info)

            if current_page != "color":
                resolve.OpenPage(current_page)

            return to_resource_result(result)
        except Exception as e:
            if current_page != "color":
                resolve.OpenPage(current_page)
            return to_resource_result(
                [{"error": f"Error retrieving color presets: {str(e)}"}]
            )

    logger.info("Preset resources registered")
