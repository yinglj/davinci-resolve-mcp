#!/usr/bin/env python3
"""
DaVinci Resolve MCP Prompts - Registration Module
"""

from .workflows import register_workflow_prompts
from .assistant import register_assistant_prompts
from .context import register_context_prompts


def register_all_prompts(mcp, resolve, logger):
    """Register all MCP prompts."""
    register_workflow_prompts(mcp, resolve, logger)
    register_assistant_prompts(mcp, resolve, logger)
    register_context_prompts(mcp, resolve, logger)


__all__ = ["register_all_prompts"]
