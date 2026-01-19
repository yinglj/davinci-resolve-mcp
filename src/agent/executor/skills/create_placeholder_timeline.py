"""CreatePlaceholderTimeline POC

Creates a lightweight placeholder timeline representation from a shot list.
This is a POC: it returns a dict describing the created timeline and supports
integration with a real Resolve instance via `src.resolve_mcp_server.get_resolve()`
if available.
"""
from typing import List, Dict, Any, Optional
import logging

# Import Resolve API functions lazily inside function to avoid circular imports at module import time

logger = logging.getLogger(__name__)


def _seconds_to_frame(seconds: float, frame_rate: float) -> int:
    return int(seconds * frame_rate)


def create_placeholder_timeline(shots: List[Dict[str, Any]], project: Optional[str] = None, options: Optional[Dict] = None) -> Dict[str, Any]:
    """Create a placeholder timeline representation from shots.

    If DaVinci Resolve is available, create a real empty timeline and add markers
    for each shot at cumulative time positions using frame numbers derived from
    frame_rate (options or timeline settings). Otherwise, return a deterministic
    in-memory representation (POC behavior).
    """
    timeline_name = options.get('timeline_name') if options and 'timeline_name' in options else 'AutoTimeline'
    frame_rate = options.get('frame_rate') if options and 'frame_rate' in options else None

    # Build the created shots structure
    created = []
    for s in shots:
        created.append({
            'id': s.get('id'),
            'summary': s.get('summary'),
            'duration': s.get('duration'),
            'shot_type': s.get('shot_type')
        })

    # Lazy imports to avoid import-time circular dependencies
    resolve = None
    try:
        from src.resolve_mcp_server import get_resolve
        from src.api.timeline_operations import create_empty_timeline, add_marker, get_current_timeline_info

        resolve = get_resolve()
    except Exception:
        resolve = None

    if resolve:
        # Try to create a real timeline via timeline_operations helper
        try:
            # Use provided frame_rate or fallback to project/timeline default
            res = create_empty_timeline(resolve, timeline_name, frame_rate=frame_rate)

            # If frame_rate not provided, try to read it from timeline info
            if frame_rate is None:
                info = get_current_timeline_info(resolve)
                try:
                    fr = float(info.get('framerate'))
                    frame_rate = fr if fr and fr > 0 else 30.0
                except Exception:
                    frame_rate = 30.0

            # Add markers at cumulative positions
            cumulative = 0.0
            markers_added = []
            for s in created:
                frame = _seconds_to_frame(cumulative, frame_rate)
                note = s.get('summary', '')
                # Use timeline_operations.add_marker wrapper
                try:
                    add_marker(resolve, frame=frame, color='Blue', note=note)
                    markers_added.append({'frame': frame, 'note': note})
                except Exception as e:
                    logger.warning(f"Failed to add marker for shot {s.get('id')}: {e}")
                cumulative += float(s.get('duration', 3))

            result = {
                'timeline_name': timeline_name,
                'project': project or None,
                'created_shots_count': len(created),
                'shots': created,
                'markers': markers_added,
                'resolve_result': res
            }

            logger.info(f"Created timeline '{timeline_name}' in Resolve, markers: {len(markers_added)}")
            return result
        except Exception as e:
            logger.exception("Error creating timeline in Resolve, falling back to local representation")

    # Fallback deterministic result (POC)
    result = {
        'timeline_name': timeline_name,
        'project': project,
        'created_shots_count': len(created),
        'shots': created
    }

    logger.info(f"Created placeholder timeline (local): {timeline_name}, shots: {len(created)}")
    return result