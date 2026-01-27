#!/usr/bin/env python3
"""
DaVinci Resolve MCP Tasks - Registration Module
"""

from .workflows import register_workflow_tasks
from .maintenance import register_maintenance_tasks


def register_all_tasks(mcp, resolve, logger):
    """Register all MCP tasks."""
    register_workflow_tasks(mcp, resolve, logger)
    register_maintenance_tasks(mcp, resolve, logger)


__all__ = ["register_all_tasks"]
