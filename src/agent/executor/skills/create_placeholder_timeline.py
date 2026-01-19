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

    # Marker placement options
    marker_position = options.get('marker_position') if options and 'marker_position' in options else 'start'
    # marker_position: 'start' | 'middle' | 'end' - where to place the marker within the shot
    default_track = options.get('marker_track') if options and 'marker_track' in options else None
    default_offset_frames = int(options.get('marker_offset_frames', 0)) if options and 'marker_offset_frames' in options else 0

    # Build the created shots structure (keep shot metadata intact so we can consider in/out per shot)
    created = []
    for s in shots:
        created.append({
            'id': s.get('id'),
            'summary': s.get('summary'),
            'duration': s.get('duration'),
            'shot_type': s.get('shot_type'),
            'in': s.get('in'),
            'out': s.get('out'),
            'offset': s.get('offset', 0),
            'marker_track': s.get('marker_track', None)
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

            # Add markers at positions determined by marker_position and per-shot metadata
            cumulative = 0.0
            markers_added = []
            for s in created:
                # Determine shot duration (prefer 'in'/'out' if present)
                duration = None
                try:
                    if s.get('in') is not None and s.get('out') is not None:
                        # in/out are seconds relative to shot; duration is out - in
                        duration = float(s['out']) - float(s['in'])
                    else:
                        duration = float(s.get('duration', 3))
                except Exception:
                    duration = float(s.get('duration', 3))

                # Base start time is cumulative + per-shot offset (seconds)
                shot_offset_seconds = float(s.get('offset', 0))
                shot_start = cumulative + shot_offset_seconds

                if marker_position == 'start':
                    marker_seconds = shot_start
                elif marker_position == 'middle':
                    marker_seconds = shot_start + max(0.0, duration / 2.0)
                elif marker_position == 'end':
                    marker_seconds = shot_start + max(0.0, duration)
                else:
                    # unknown option - default to start
                    marker_seconds = shot_start

                # If shot specified explicit 'marker_offset_frames', apply
                marker_offset_frames = default_offset_frames
                marker_track = s.get('marker_track') if s.get('marker_track') is not None else default_track

                frame = _seconds_to_frame(marker_seconds, frame_rate) + marker_offset_frames
                note = s.get('summary', '')

                # Use timeline_operations.add_marker wrapper, but catch and log failures per-shot
                try:
                    add_marker(resolve, frame=frame, color='Blue', note=note, track=marker_track)
                    markers_added.append({'frame': frame, 'note': note, 'track': marker_track})
                except TypeError:
                    # older Resolve mock or API might not accept track param; try without it
                    try:
                        add_marker(resolve, frame=frame, color='Blue', note=note)
                        markers_added.append({'frame': frame, 'note': note, 'track': None})
                    except Exception as e:
                        logger.warning("Failed to add marker in fallback attempt for shot %s: %s", s.get('id'), str(e))
                except Exception as e:
                    logger.warning("Failed to add marker for shot %s: %s", s.get('id'), str(e))

                cumulative += duration

            result = {
                'timeline_name': timeline_name,
                'project': project or None,
                'created_shots_count': len(created),
                'shots': created,
                'markers': markers_added,
                'resolve_result': res
            }

            logger.info("Created timeline '%s' in Resolve, markers: %d", timeline_name, len(markers_added))
            return result
        except Exception as e:
            # Log exception details and fallback
            logger.exception("Error creating timeline in Resolve (will fallback to local representation): %s", str(e))

    # Fallback deterministic result (POC)
    result = {
        'timeline_name': timeline_name,
        'project': project,
        'created_shots_count': len(created),
        'shots': created
    }

    logger.info(f"Created placeholder timeline (local): {timeline_name}, shots: {len(created)}")
    return result