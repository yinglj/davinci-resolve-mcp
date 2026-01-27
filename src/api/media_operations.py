#!/usr/bin/env python3
"""
DaVinci Resolve Media Operations
Re-exports from split submodules for backward compatibility.
"""

# Re-export all functions from submodules
from src.api.media.pool import (
    list_media_pool_clips,
    import_media,
    create_bin,
    list_bins,
    get_bin_contents,
    format_clip_list,
    get_all_media_pool_clips,
)

from src.api.media.clips import (
    list_timeline_clips,
    add_clip_to_timeline,
    delete_media,
    move_media_to_bin,
    create_sub_clip,
)

from src.api.media.sync import (
    auto_sync_audio,
    unlink_clips,
    relink_clips,
)

__all__ = [
    # Pool operations
    "list_media_pool_clips",
    "import_media",
    "create_bin",
    "list_bins",
    "get_bin_contents",
    "format_clip_list",
    "get_all_media_pool_clips",
    # Clip operations
    "list_timeline_clips",
    "add_clip_to_timeline",
    "delete_media",
    "move_media_to_bin",
    "create_sub_clip",
    # Sync operations
    "auto_sync_audio",
    "unlink_clips",
    "relink_clips",
]
