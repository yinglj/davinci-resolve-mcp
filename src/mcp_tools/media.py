#!/usr/bin/env python3
"""
DaVinci Resolve MCP Media Tools
Media pool and clip operations
"""

from typing import List, Dict, Any, Optional


def register_media_tools(mcp, resolve, logger):
    """Register media pool MCP tools."""

    # @mcp.tool() - SKIPPED: import_media is in granular (prefer upstream)
    def import_media(file_path: str) -> str:
        """Import a media file from the local filesystem into the current project's media pool.

        Args:
            file_path: Absolute path to the media file to import.

        Returns:
            str: Success message with clip name or failure description.
        """
        from src.api.media import import_media as import_media_func

        return import_media_func(resolve, file_path)

    # @mcp.tool() - SKIPPED: delete_media is in granular (prefer upstream)
    def delete_media(clip_name: str) -> str:
        """Delete a media clip from the media pool by its name.

        Args:
            clip_name: The name of the clip to remove.

        Returns:
            str: A message indicating whether the clip was successfully deleted.
        """
        from src.api.media import delete_media as delete_media_func

        return delete_media_func(resolve, clip_name)

    # @mcp.tool() - SKIPPED: move_media_to_bin is in granular (prefer upstream)
    def move_media_to_bin(clip_name: str, bin_name: str) -> str:
        """Move a media clip to a specific bin (folder) in the media pool.

        Args:
            clip_name: The name of the clip to move.
            bin_name: The target bin/folder name.

        Returns:
            str: Result of the move operation.
        """
        from src.api.media import move_media_to_bin as move_media_func

        return move_media_func(resolve, clip_name, bin_name)

    # @mcp.tool() - SKIPPED: auto_sync_audio is in granular (prefer upstream)
    def auto_sync_audio(
        clip_names: List[str],
        sync_method: str = "waveform",
        append_mode: bool = False,
        target_bin: Optional[str] = None,
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
        from src.api.media import auto_sync_audio as auto_sync_audio_func

        return auto_sync_audio_func(
            resolve, clip_names, sync_method, append_mode, target_bin
        )

    # @mcp.tool() - SKIPPED: unlink_clips is in granular (prefer upstream)
    def unlink_clips(clip_names: List[str]) -> str:
        """Unlink specified clips, disconnecting them from their media files.

        Args:
            clip_names: List of clip names to unlink.

        Returns:
            str: A message indicating the success or failure of the operation.
        """
        from src.api.media import unlink_clips as unlink_clips_func

        return unlink_clips_func(resolve, clip_names)

    # @mcp.tool() - SKIPPED: relink_clips is in granular (prefer upstream)
    def relink_clips(
        clip_names: List[str],
        media_paths: Optional[List[str]] = None,
        folder_path: Optional[str] = None,
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
        from src.api.media import relink_clips as relink_clips_func

        return relink_clips_func(
            resolve, clip_names, media_paths, folder_path, recursive
        )

    # @mcp.tool() - SKIPPED: create_sub_clip is in granular (prefer upstream)
    def create_sub_clip(
        clip_name: str,
        start_frame: int,
        end_frame: int,
        sub_clip_name: Optional[str] = None,
        bin_name: Optional[str] = None,
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
        from src.api.media import create_sub_clip as create_sub_clip_func

        return create_sub_clip_func(
            resolve, clip_name, start_frame, end_frame, sub_clip_name, bin_name
        )

    # @mcp.tool() - SKIPPED: create_bin is in granular (prefer upstream)
    def create_bin(name: str) -> str:
        """Create a new bin (folder) in the media pool root folder.

        Args:
            name: The name for the new bin.

        Returns:
            str: Result message.
        """
        from src.api.media import create_bin as create_bin_func

        return create_bin_func(resolve, name)

    # @mcp.tool() - SKIPPED: add_clip_to_timeline is in granular (prefer upstream)
    def add_clip_to_timeline(
        clip_name: str, timeline_name: Optional[str] = None
    ) -> str:
        """Add a media pool clip to the timeline.

        Args:
            clip_name: Name of the clip to add to the timeline.
            timeline_name: Name of the timeline to add the clip to.

        Returns:
            str: A message indicating the success or failure of the operation.
        """
        from src.api.media import add_clip_to_timeline as add_clip_func

        return add_clip_func(resolve, clip_name, timeline_name)

    @mcp.tool()
    def append_to_timeline(
        clip_name: str,
        start_frame: Optional[int] = None,
        end_frame: Optional[int] = None,
        track_index: int = 1,
        record_frame: Optional[int] = None,
        timeline_name: Optional[str] = None,
    ) -> str:
        """Append a media pool clip (or a frame range of it) to the current timeline.

        This is the recommended way to add clips to a timeline. It uses Resolve's
        native AppendToTimeline API which supports startFrame/endFrame for
        "virtual subclip" semantics — no need to create subclips first.

        Args:
            clip_name: Name of the clip in the media pool (e.g. "video.mp4").
            start_frame: Optional start frame for subclip range. Omit for full clip.
            end_frame: Optional end frame for subclip range. Omit for full clip.
            track_index: Target video track index (default 1).
            record_frame: Optional position on the timeline to place the clip.
            timeline_name: Optional timeline name (uses current if not specified).

        Returns:
            str: A message indicating the success or failure of the operation.
        """
        from src.api.media import append_to_timeline as append_func

        return append_func(
            resolve,
            clip_name,
            start_frame,
            end_frame,
            track_index,
            record_frame,
            timeline_name,
        )

    # @mcp.tool() - SKIPPED: get_clip_metadata is in granular (prefer upstream)
    def get_clip_metadata(clip_name: str) -> Dict[str, Any]:
        """Get detailed metadata for a media pool clip (FPS, duration, resolution, etc.).

        Args:
            clip_name: Name of the clip to inspect.

        Returns:
            dict: Metadata properties or error message.
        """
        from src.api.media import get_clip_metadata as get_meta_func

        return get_meta_func(resolve, clip_name)

    logger.info("Registered media tools")
