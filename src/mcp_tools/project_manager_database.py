#!/usr/bin/env python3
"""
DaVinci Resolve MCP Project Manager Database Tools
Database management operations
"""

from typing import Dict, Any, Optional


def register_project_manager_database_tools(mcp, resolve, logger):
    """Register project manager database MCP tools."""

    @mcp.tool()
    def project_manager_database(action: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Manage DaVinci Resolve project databases.

        Actions:
          get_current() -> {db_type, db_name}
          list() -> {databases}
          set_current(db_info) -> {success}  — db_info: {DbType, DbName}

        Args:
            action: The action to perform (get_current, list, set_current)
            params: Optional parameters for the action

        Returns:
            dict: Result of the action
        """
        from src.api.database_operations import (
            get_current_database,
            get_database_list,
            set_current_database,
        )

        if resolve is None:
            return {"error": "Not connected to DaVinci Resolve"}

        p = params or {}
        action_lower = action.lower()

        if action_lower == "get_current":
            return get_current_database(resolve)
        elif action_lower == "list":
            databases = get_database_list(resolve)
            return {"databases": databases}
        elif action_lower == "set_current":
            db_type = p.get("db_type")
            db_name = p.get("db_name")
            ip_address = p.get("ip_address", "127.0.0.1")

            if not db_type or not db_name:
                return {"success": False, "error": "db_type and db_name are required"}

            result = set_current_database(resolve, db_type, db_name, ip_address)
            if result.startswith("Successfully"):
                return {"success": True, "message": result}
            else:
                return {"success": False, "error": result}
        else:
            valid = ["get_current", "list", "set_current"]
            return {"error": f"Unknown action '{action}'. Valid actions: {', '.join(valid)}"}

    logger.info("Registered project manager database tools")