#!/usr/bin/env python3
"""
DaVinci Resolve MCP Prompts - Workflow related prompts
"""

from typing import Optional


def register_workflow_prompts(mcp, resolve, logger):
    """Register workflow-related prompts."""

    @mcp.prompt()
    def optimize_workflow(project_type: str = "commercial") -> str:
        """
        Suggest an optimized workflow for a specific project type.

        Args:
            project_type: The type of project (commercial, documentary, feature, social_media)
        """
        return f"""You are an expert DaVinci Resolve Workflow Consultant. 
The user is working on a {project_type} project. 

Please analyze their current project structure and suggest:
1. Best organizational practices for their Media Pool.
2. Recommended timeline settings for this project type.
3. An efficient round-trip or internal workflow (e.g., from Edit to Color to Fairlight).
4. Export settings tailored for the final delivery of a {project_type} project.

Ask the user for specific details about their footage if needed."""

    @mcp.prompt()
    def social_media_strategy(platform: str = "instagram_reels") -> str:
        """
        Get a strategy for social media delivery.

        Args:
            platform: Targeted platform (instagram_reels, tiktok, youtube_shorts, youtube_main)
        """
        return f"""You are a Social Media Content Specialist. 
The goal is to optimize the current DaVinci Resolve project for {platform}.

Please provide:
1. Ideal resolution and aspect ratio settings.
2. Recommendations for safe zones and overlays.
3. Tips for using 'Smart Reframe' if applicable.
4. Optimal render settings for {platform} to ensure the highest quality after upload compression.
5. Suggestions for 'Social Media' specific transitions and effects."""

    logger.info("Workflow prompts registered")
