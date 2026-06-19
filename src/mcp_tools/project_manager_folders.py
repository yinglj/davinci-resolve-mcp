#!/usr/bin/env python3
"""
DaVinci Resolve MCP Project Manager Folders Tools
Navigate and manage project folders in the Project Manager
"""

from typing import Dict, Any, Optional


def _unknown(action, valid):
    """Return error for unknown action."""
    return {"error": f"Unknown action '{action}'. Valid actions: {', '.join(valid)}"}


def register_project_manager_folders_tools(mcp, resolve, logger):
    """Register project manager folders MCP tools."""

    @mcp.tool()
    def project_manager_folders(
        action: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Navigate and manage project folders in the Project Manager.

        Actions:
            list() -> {folders}
            get_current() -> {folder}
            create(name) -> {success}
            delete(name) -> {success}
            open(name) -> {success}
            goto_root() -> {success}
            goto_parent() -> {success}

        Args:
            action: The action to perform.
            params: Optional parameters for the action.

        Returns:
            Dict containing the result of the action.
        """
        if resolve is None:
            return {"error": "Not connected to DaVinci Resolve"}

        project_manager = resolve.GetProjectManager()
        if not project_manager:
            return {"error": "Failed to get Project Manager"}

        try:
            if action == "list":
                return _list_folders(project_manager)
            elif action == "get_current":
                return _get_current_folder(project_manager)
            elif action == "create":
                return _create_folder(project_manager, params)
            elif action == "delete":
                return _delete_folder(project_manager, params)
            elif action == "open":
                return _open_folder(project_manager, params)
            elif action == "goto_root":
                return {"success": bool(project_manager.GotoRootFolder())}
            elif action == "goto_parent":
                return {"success": bool(project_manager.GotoParentFolder())}
            else:
                return _unknown(action, ["list", "get_current", "create", "delete", "open", "goto_root", "goto_parent"])
        except Exception as e:
            return {"error": f"Error executing {action}: {str(e)}"}

    logger.info("Registered project manager folders tools")


def _list_folders(project_manager):
    """List folders in current folder."""
    folders = project_manager.GetFolderListInCurrentFolder()
    return {"folders": folders if folders else []}


def _get_current_folder(project_manager):
    """Get current folder name."""
    folder = project_manager.GetCurrentFolder()
    return {"folder": folder if folder else "Root"}


def _create_folder(project_manager, params):
    """Create a new folder."""
    name = params.get("name") if params else None
    if not name:
        return {"error": "name parameter is required for create"}
    return {"success": bool(project_manager.CreateFolder(name))}


def _delete_folder(project_manager, params):
    """Delete a folder by name."""
    name = params.get("name") if params else None
    if not name:
        return {"error": "name parameter is required for delete"}
    return {"success": bool(project_manager.DeleteFolder(name))}


def _open_folder(project_manager, params):
    """Open a folder by name."""
    name = params.get("name") if params else None
    if not name:
        return {"error": "name parameter is required for open"}
    return {"success": bool(project_manager.OpenFolder(name))}
