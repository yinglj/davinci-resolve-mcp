#!/usr/bin/env python3
"""
DaVinci Resolve MCP Delivery Tools
Rendering and delivery operations
"""

import os
from typing import Any, Dict, Optional, Protocol, TypedDict, cast


class _MediaPoolItem(Protocol):
    def GetName(self) -> str:  # noqa: N802
        ...

    def LinkProxyMedia(self, proxy_media_file_path: str) -> bool:  # noqa: N802
        ...

    def UnlinkProxyMedia(self) -> bool:  # noqa: N802
        ...

    def ReplaceClip(self, replacement_path: str) -> bool:  # noqa: N802
        ...

    def TranscribeAudio(self, language: Optional[str] = None) -> bool:  # noqa: N802
        ...

    def ClearTranscription(self) -> bool:  # noqa: N802
        ...


class _MediaPoolClipsResult(TypedDict):
    clips: list[_MediaPoolItem]


def register_delivery_tools(mcp, resolve, logger):
    """Register delivery page MCP tools."""

    @mcp.tool()
    def add_to_render_queue(
        preset_name: str,
        timeline_name: Optional[str] = None,
        use_in_out_range: bool = False,
        target_dir: Optional[str] = None,
        custom_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Add a timeline to the render queue with the specified preset.

        Args:
            preset_name: Name of the render preset (e.g., 'H.264 Master', 'YouTube - 1080p')
            timeline_name: Optional timeline name (uses current if not specified)
            use_in_out_range: If True, only render the in/out range
            target_dir: Optional output directory path (e.g., 'C:/output' or '/home/user/output')
            custom_name: Optional custom filename for the output (without extension)

        Returns:
            Dict[str, Any]: A dictionary containing the result of the operation.
        """
        from src.api.delivery import add_to_render_queue as add_queue_func

        # Build render_settings dict if custom options provided
        render_settings = {}
        if target_dir:
            render_settings["TargetDir"] = target_dir
        if custom_name:
            render_settings["CustomName"] = custom_name

        return add_queue_func(
            resolve,
            preset_name,
            timeline_name,
            use_in_out_range,
            render_settings if render_settings else None,
        )

    @mcp.tool()
    def start_render() -> Dict[str, Any]:
        """Start rendering the jobs in the render queue.

        Returns:
            Dict[str, Any]: A dictionary containing the result of the operation.
        """
        from src.api.delivery import start_render as start_render_func

        return start_render_func(resolve)

    @mcp.tool()
    def clear_render_queue() -> Dict[str, Any]:
        """Clear all jobs from the render queue.

        Returns:
            Dict[str, Any]: A dictionary containing the result of the operation.
        """
        from src.api.delivery import clear_render_queue as clear_queue_func

        return clear_queue_func(resolve)

    @mcp.tool()
    def link_proxy_media(clip_name: str, proxy_file_path: str) -> str:
        """Link a proxy media file to a clip.

        Args:
            clip_name: Name of the clip to link the proxy media to.
            proxy_file_path: Path to the proxy media file.

        Returns:
            str: A message indicating the success or failure of the operation.
        """
        if not resolve:
            return "Error: Not connected to DaVinci Resolve"

        project_manager = resolve.GetProjectManager()
        if not project_manager:
            return "Error: Failed to get Project Manager"

        current_project = project_manager.GetCurrentProject()
        if not current_project:
            return "Error: No project currently open"

        media_pool = current_project.GetMediaPool()
        if not media_pool:
            return "Error: Failed to get Media Pool"

        from src.api.media import get_all_media_pool_clips

        pool_result = get_all_media_pool_clips(resolve)
        if isinstance(pool_result, dict) and "error" in pool_result:
            return f"Error: {pool_result['error']}"
        if not isinstance(pool_result, dict) or "clips" not in pool_result:
            return "Error: Failed to fetch media pool clips"

        clips = cast(_MediaPoolClipsResult, cast(object, pool_result))["clips"]
        target_clip = None

        for clip in clips:
            if not clip:
                continue
            if clip.GetName() == clip_name:
                target_clip = clip
                break

        if not target_clip:
            return f"Error: Clip '{clip_name}' not found in Media Pool"

        if not os.path.exists(proxy_file_path):
            return f"Error: Proxy file '{proxy_file_path}' does not exist"

        try:
            result = target_clip.LinkProxyMedia(proxy_file_path)
            if result:
                return f"Successfully linked proxy media '{proxy_file_path}' to clip '{clip_name}'"
            else:
                return f"Failed to link proxy media to clip '{clip_name}'"
        except Exception as e:
            return f"Error linking proxy media: {str(e)}"

    @mcp.tool()
    def unlink_proxy_media(clip_name: str) -> str:
        """Unlink proxy media from a clip.

        Args:
            clip_name: Name of the clip to unlink the proxy media from.

        Returns:
            str: A message indicating the success or failure of the operation.
        """
        if not resolve:
            return "Error: Not connected to DaVinci Resolve"

        project_manager = resolve.GetProjectManager()
        if not project_manager:
            return "Error: Failed to get Project Manager"

        current_project = project_manager.GetCurrentProject()
        if not current_project:
            return "Error: No project currently open"

        media_pool = current_project.GetMediaPool()
        if not media_pool:
            return "Error: Failed to get Media Pool"

        from src.api.media import get_all_media_pool_clips

        pool_result = get_all_media_pool_clips(resolve)
        if isinstance(pool_result, dict) and "error" in pool_result:
            return f"Error: {pool_result['error']}"
        if not isinstance(pool_result, dict) or "clips" not in pool_result:
            return "Error: Failed to fetch media pool clips"

        clips = cast(_MediaPoolClipsResult, cast(object, pool_result))["clips"]
        target_clip = None

        for clip in clips:
            if not clip:
                continue
            if clip.GetName() == clip_name:
                target_clip = clip
                break

        if not target_clip:
            return f"Error: Clip '{clip_name}' not found in Media Pool"

        try:
            result = target_clip.UnlinkProxyMedia()
            if result:
                return f"Successfully unlinked proxy media from clip '{clip_name}'"
            else:
                return f"Failed to unlink proxy media from clip '{clip_name}'"
        except Exception as e:
            return f"Error unlinking proxy media: {str(e)}"

    @mcp.tool()
    def replace_clip(clip_name: str, replacement_path: str) -> str:
        """Replace a clip with another media file.

        Args:
            clip_name: Name of the clip to replace.
            replacement_path: Path to the replacement media file.

        Returns:
            str: A message indicating the success or failure of the operation.
        """
        if not resolve:
            return "Error: Not connected to DaVinci Resolve"

        project_manager = resolve.GetProjectManager()
        if not project_manager:
            return "Error: Failed to get Project Manager"

        current_project = project_manager.GetCurrentProject()
        if not current_project:
            return "Error: No project currently open"

        media_pool = current_project.GetMediaPool()
        if not media_pool:
            return "Error: Failed to get Media Pool"

        from src.api.media import get_all_media_pool_clips

        pool_result = get_all_media_pool_clips(resolve)
        if isinstance(pool_result, dict) and "error" in pool_result:
            return f"Error: {pool_result['error']}"
        if not isinstance(pool_result, dict) or "clips" not in pool_result:
            return "Error: Failed to fetch media pool clips"

        clips = cast(_MediaPoolClipsResult, cast(object, pool_result))["clips"]
        target_clip = None

        for clip in clips:
            if not clip:
                continue
            if clip.GetName() == clip_name:
                target_clip = clip
                break

        if not target_clip:
            return f"Error: Clip '{clip_name}' not found in Media Pool"

        if not os.path.exists(replacement_path):
            return f"Error: Replacement file '{replacement_path}' does not exist"

        try:
            result = target_clip.ReplaceClip(replacement_path)
            if result:
                return f"Successfully replaced clip '{clip_name}' with '{replacement_path}'"
            else:
                return f"Failed to replace clip '{clip_name}'"
        except Exception as e:
            return f"Error replacing clip: {str(e)}"

    @mcp.tool()
    def transcribe_audio(clip_name: str, language: str = "en-US") -> str:
        """Transcribe audio for a clip.

        Args:
            clip_name: Name of the clip to transcribe.
            language: Language code for the transcription (e.g., 'en-US', 'ja-JP', 'zh-CN', 'zh-TW', 'ko-KR', 'fr-FR', 'de-DE', 'it-IT', 'es-ES', 'pt-BR', 'pt-PT', 'ru-RU', 'ar-SA', 'hi-IN', 'bn-BD', 'bn-IN', 'ta-IN', 'te-IN', 'ur-PK', 'ur-IN', 'th-TH', 'vi-VN', 'zh-HK', 'zh-TW').

        Returns:
            str: A message indicating the success or failure of the operation.
        """
        if not resolve:
            return "Error: Not connected to DaVinci Resolve"

        project_manager = resolve.GetProjectManager()
        if not project_manager:
            return "Error: Failed to get Project Manager"

        current_project = project_manager.GetCurrentProject()
        if not current_project:
            return "Error: No project currently open"

        media_pool = current_project.GetMediaPool()
        if not media_pool:
            return "Error: Failed to get Media Pool"

        from src.api.media import get_all_media_pool_clips

        pool_result = get_all_media_pool_clips(resolve)
        if isinstance(pool_result, dict) and "error" in pool_result:
            return f"Error: {pool_result['error']}"
        if not isinstance(pool_result, dict) or "clips" not in pool_result:
            return "Error: Failed to fetch media pool clips"

        clips = cast(_MediaPoolClipsResult, cast(object, pool_result))["clips"]
        target_clip = None

        for clip in clips:
            if not clip:
                continue
            if clip.GetName() == clip_name:
                target_clip = clip
                break

        if not target_clip:
            return f"Error: Clip '{clip_name}' not found in Media Pool"

        try:
            try:
                result = target_clip.TranscribeAudio(language)
            except TypeError:
                result = target_clip.TranscribeAudio()
            if result:
                return f"Successfully started audio transcription for clip '{clip_name}' in language '{language}'"
            else:
                return f"Failed to start audio transcription for clip '{clip_name}'"
        except Exception as e:
            return f"Error during audio transcription: {str(e)}"

    @mcp.tool()
    def clear_transcription(clip_name: str) -> str:
        """Clear audio transcription for a clip.

        Args:
            clip_name: Name of the clip to clear the transcription for.

        Returns:
            str: A message indicating the success or failure of the operation.
        """
        if not resolve:
            return "Error: Not connected to DaVinci Resolve"

        project_manager = resolve.GetProjectManager()
        if not project_manager:
            return "Error: Failed to get Project Manager"

        current_project = project_manager.GetCurrentProject()
        if not current_project:
            return "Error: No project currently open"

        media_pool = current_project.GetMediaPool()
        if not media_pool:
            return "Error: Failed to get Media Pool"

        from src.api.media import get_all_media_pool_clips

        pool_result = get_all_media_pool_clips(resolve)
        if isinstance(pool_result, dict) and "error" in pool_result:
            return f"Error: {pool_result['error']}"
        if not isinstance(pool_result, dict) or "clips" not in pool_result:
            return "Error: Failed to fetch media pool clips"

        clips = cast(_MediaPoolClipsResult, cast(object, pool_result))["clips"]
        target_clip = None

        for clip in clips:
            if not clip:
                continue
            if clip.GetName() == clip_name:
                target_clip = clip
                break

        if not target_clip:
            return f"Error: Clip '{clip_name}' not found in Media Pool"

        try:
            result = target_clip.ClearTranscription()
            if result:
                return (
                    f"Successfully cleared audio transcription for clip '{clip_name}'"
                )
            else:
                return f"Failed to clear audio transcription for clip '{clip_name}'"
        except Exception as e:
            return f"Error clearing audio transcription: {str(e)}"

    logger.info("Registered delivery tools")
