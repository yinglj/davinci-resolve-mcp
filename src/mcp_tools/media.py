#!/usr/bin/env python3
"""
DaVinci Resolve MCP Media Tools
Media pool and clip operations
"""

from typing import List, Dict, Any


def register_media_tools(mcp, resolve, logger):
    """Register media pool MCP tools."""

    @mcp.tool()
    def import_media(file_path: str) -> str:
        """Import a media file from the local filesystem into the current project's media pool.

        Args:
            file_path: Absolute path to the media file to import.

        Returns:
            str: Success message with clip name or failure description.
        """
        from src.api.media_operations import import_media as import_media_func

        return import_media_func(resolve, file_path)

    @mcp.tool()
    def delete_media(clip_name: str) -> str:
        """Delete a media clip from the media pool by its name.

        Args:
            clip_name: The name of the clip to remove.

        Returns:
            str: A message indicating whether the clip was successfully deleted.
        """
        from src.api.media_operations import delete_media as delete_media_func

        return delete_media_func(resolve, clip_name)

    @mcp.tool()
    def move_media_to_bin(clip_name: str, bin_name: str) -> str:
        """Move a media clip to a specific bin (folder) in the media pool.

        Args:
            clip_name: The name of the clip to move.
            bin_name: The target bin/folder name.

        Returns:
            str: Result of the move operation.
        """
        from src.api.media_operations import move_media_to_bin as move_media_func

        return move_media_func(resolve, clip_name, bin_name)

    @mcp.tool()
    def auto_sync_audio(
        clip_names: List[str],
        sync_method: str = "waveform",
        append_mode: bool = False,
        target_bin: str = None,
    ) -> str:
        """Sync audio between clips with customizable settings.

        Args:
            clip_names: List of clip names to sync audio for.
            sync_method: Method to sync audio ("waveform", "phase", "pitch").
            append_mode: Whether to append the synced audio to the existing audio.
            target_bin: Target bin to move the synced clips to.

        Returns:
            str: A message indicating the success or failure of the operation.
        """
        from src.api.media_operations import auto_sync_audio as auto_sync_audio_func

        return auto_sync_audio_func(
            resolve, clip_names, sync_method, append_mode, target_bin
        )

    @mcp.tool()
    def unlink_clips(clip_names: List[str]) -> str:
        """Unlink specified clips, disconnecting them from their media files.

        Args:
            clip_names: List of clip names to unlink.

        Returns:
            str: A message indicating the success or failure of the operation.
        """
        from src.api.media_operations import unlink_clips as unlink_clips_func

        return unlink_clips_func(resolve, clip_names)

    @mcp.tool()
    def relink_clips(
        clip_names: List[str],
        media_paths: List[str] = None,
        folder_path: str = None,
        recursive: bool = False,
    ) -> str:
        """Relink specified clips to their media files.

        Args:
            clip_names: List of clip names to relink.
            media_paths: List of media paths to relink to.
            folder_path: Path to the folder containing the media files.
            recursive: Whether to recursively search for media files.

        Returns:
            str: A message indicating the success or failure of the operation.
        """
        from src.api.media_operations import relink_clips as relink_clips_func

        return relink_clips_func(
            resolve, clip_names, media_paths, folder_path, recursive
        )

    @mcp.tool()
    def create_sub_clip(
        clip_name: str,
        start_frame: int,
        end_frame: int,
        sub_clip_name: str = None,
        bin_name: str = None,
    ) -> str:
        """Create a subclip from the specified clip using in and out points.

        Args:
            clip_name: Name of the clip to create a subclip from.
            start_frame: Start frame of the subclip.
            end_frame: End frame of the subclip.
            sub_clip_name: Name for the new subclip.
            bin_name: Name of the bin to move the subclip to.

        Returns:
            str: A message indicating the success or failure of the operation.
        """
        from src.api.media_operations import create_sub_clip as create_sub_clip_func

        return create_sub_clip_func(
            resolve, clip_name, start_frame, end_frame, sub_clip_name, bin_name
        )

    @mcp.tool()
    def create_bin(name: str) -> str:
        """Create a new bin (folder) in the media pool root folder.

        Args:
            name: The name for the new bin.

        Returns:
            str: Result message.
        """
        from src.api.media_operations import create_bin as create_bin_func

        return create_bin_func(resolve, name)

    @mcp.tool()
    def add_clip_to_timeline(clip_name: str, timeline_name: str = None) -> str:
        """Add a media pool clip to the timeline.

        Args:
            clip_name: Name of the clip to add to the timeline.
            timeline_name: Name of the timeline to add the clip to.

        Returns:
            str: A message indicating the success or failure of the operation.
        """
        from src.api.media_operations import add_clip_to_timeline as add_clip_func

        return add_clip_func(resolve, clip_name, timeline_name)

    logger.info("Registered media tools")
