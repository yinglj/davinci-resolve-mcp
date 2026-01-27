#!/usr/bin/env python3
"""
DaVinci Resolve MCP Prompts - Context-aware prompts
"""


def register_context_prompts(mcp, resolve, logger):
    """Register context-aware prompts."""

    @mcp.prompt()
    def summarize_current_state() -> str:
        """
        Get a summary of the current DaVinci Resolve state for the AI.
        Useful for starting a session with full context.
        """
        if resolve is None:
            return "Note: Not connected to DaVinci Resolve. Please ensure Resolve is running and the scripting API is enabled."

        try:
            pm = resolve.GetProjectManager()
            project = pm.GetCurrentProject()
            if not project:
                return "The user has DaVinci Resolve open but no project is currently loaded. Please ask the user which project they would like to open or create."

            project_name = project.GetName()
            timeline = project.GetCurrentTimeline()
            timeline_name = timeline.GetName() if timeline else "None"

            media_pool = project.GetMediaPool()
            root_folder = media_pool.GetRootFolder()
            clips_count = len(root_folder.GetClipList()) if root_folder else 0

            return f"""You are an advanced DaVinci Resolve Assistant. 
The current environment is:
- Project: '{project_name}'
- Active Timeline: '{timeline_name}'
- Media Pool: Approximately {clips_count} clips in the root folder.

Please analyze the current setup and ask the user how you can assist them today. 
You can help with editing, color grading, audio production in Fairlight, or delivery settings.
If they have a specific goal, suggest the next steps based on this context."""
        except Exception as e:
            return f"Error retrieving context from DaVinci Resolve: {str(e)}. Please guide the user manually."

    logger.info("Context prompts registered")
