"""AutoCut planning utilities

Beat-aware shot timing with style/pacing heuristics, beat snapping, and constraints.
"""
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


def beat_to_time(beat_index: float, bpm: float) -> float:
    """Convert beat index to time in seconds using BPM."""
    if bpm is None or bpm <= 0:
        raise ValueError("BPM must be a positive number")
    return float(beat_index) * (60.0 / float(bpm))


def snap_to_beat(value: float, bpm: float, round_mode: str = 'nearest') -> float:
    """Snap a value (in seconds) to the nearest beat.
    
    Args:
        value: time in seconds
        bpm: tempo
        round_mode: 'nearest', 'up', 'down'
    
    Returns:
        snapped time in seconds
    """
    beat_interval = 60.0 / float(bpm)
    beat_count = value / beat_interval
    
    if round_mode == 'nearest':
        snapped_beats = round(beat_count)
    elif round_mode == 'up':
        import math
        snapped_beats = math.ceil(beat_count)
    elif round_mode == 'down':
        import math
        snapped_beats = math.floor(beat_count)
    else:
        snapped_beats = round(beat_count)
    
    return beat_to_time(snapped_beats, bpm)


def detect_beat_density(shots: List[Dict[str, Any]], bpm: float) -> str:
    """Heuristic to detect pacing style: 'tight', 'normal', or 'loose'.
    
    Analyzes average shot duration relative to beat intervals.
    """
    if not shots or bpm is None or bpm <= 0:
        return 'normal'
    
    beat_interval = 60.0 / float(bpm)
    durations = [float(s.get('duration', beat_interval * 2)) for s in shots]
    avg_duration = sum(durations) / len(durations) if durations else beat_interval * 2
    beats_per_shot = avg_duration / beat_interval
    
    if beats_per_shot < 1.5:
        return 'tight'
    elif beats_per_shot > 3.5:
        return 'loose'
    else:
        return 'normal'


def auto_cut_shots(
    shots: List[Dict[str, Any]],
    bpm: Optional[float] = None,
    default_beats_per_shot: int = 2,
    style: str = 'auto',
    min_duration: float = 0.5,
    max_duration: Optional[float] = None,
    snap_to_beats: bool = True
) -> List[Dict[str, Any]]:
    """Assign 'in' and 'out' times to shots based on BPM and pacing style.

    Args:
        shots: List of shot dicts (each with optional 'duration', 'id', etc.)
        bpm: Optional tempo (beats per minute)
        default_beats_per_shot: fallback beats when shot has no duration
        style: 'auto' (detect), 'tight', 'normal', or 'loose' for beat density
        min_duration: minimum shot duration in seconds
        max_duration: maximum shot duration in seconds (None = no limit)
        snap_to_beats: if True and bpm provided, align shot boundaries to beats

    Returns:
        New list of shots with added 'in', 'out', 'in_beat', 'out_beat' keys
    """
    updated = []

    if not shots:
        return []

    if bpm is not None and bpm > 0:
        # Beat-aligned logic
        beat_interval = 60.0 / float(bpm)

        # Detect pacing if style is 'auto'
        if style == 'auto':
            style = detect_beat_density(shots, bpm)

        # Adjust default beats based on style
        style_multiplier = {'tight': 1.0, 'normal': 1.0, 'loose': 1.5}
        effective_default_beats = default_beats_per_shot * style_multiplier.get(style, 1.0)

        cumulative_beats = 0.0

        for s in shots:
            raw_duration = s.get('duration')
            if raw_duration is None:
                # Use style-adjusted default
                beats = effective_default_beats
            else:
                # Convert duration seconds to beat count
                beats = max(1, float(raw_duration) / beat_interval)

            # Clamp duration to min/max constraints
            duration_sec = beat_to_time(beats, bpm)
            if duration_sec < min_duration:
                beats = beat_to_time(min_duration, bpm)
            if max_duration and duration_sec > max_duration:
                beats = beat_to_time(max_duration, bpm)

            in_beat = cumulative_beats
            out_beat = in_beat + beats

            # Optionally snap to beat boundaries
            if snap_to_beats:
                in_beat_snapped = round(in_beat)
                out_beat_snapped = round(max(in_beat_snapped + 1, out_beat))  # at least 1 beat
                in_sec = beat_to_time(in_beat_snapped, bpm)
                out_sec = beat_to_time(out_beat_snapped, bpm)
            else:
                in_sec = beat_to_time(in_beat, bpm)
                out_sec = beat_to_time(out_beat, bpm)

            new_shot = dict(s)
            new_shot.update({
                'in': in_sec,
                'out': out_sec,
                'in_beat': in_beat_snapped if snap_to_beats else in_beat,
                'out_beat': out_beat_snapped if snap_to_beats else out_beat,
                'style': style
            })
            updated.append(new_shot)

            cumulative_beats = out_beat_snapped if snap_to_beats else out_beat

    else:
        # Fallback: use durations if present, otherwise use a default of 2.0 seconds
        cumulative = 0.0
        for s in shots:
            raw_duration = float(s.get('duration', 2.0))
            
            # Clamp to min/max
            duration_sec = max(min_duration, raw_duration)
            if max_duration:
                duration_sec = min(duration_sec, max_duration)

            in_sec = cumulative
            out_sec = in_sec + duration_sec
            new_shot = dict(s)
            new_shot.update({'in': in_sec, 'out': out_sec})
            updated.append(new_shot)
            cumulative = out_sec

    logger.info("AutoCut assigned in/out for %d shots (bpm=%s, style=%s)", len(updated), str(bpm), style)
    return updated
