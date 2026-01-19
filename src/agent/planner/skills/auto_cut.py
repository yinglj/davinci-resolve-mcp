"""AutoCut planning utilities

Simple POC functions to map beats -> time and assign in/out times to shots based on BPM.
"""
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


def beat_to_time(beat_index: int, bpm: float) -> float:
    """Convert beat index to time in seconds using BPM."""
    if bpm is None or bpm <= 0:
        raise ValueError("BPM must be a positive number")
    return beat_index * (60.0 / float(bpm))


def auto_cut_shots(shots: List[Dict[str, Any]], bpm: Optional[float] = None, default_beats_per_shot: int = 2) -> List[Dict[str, Any]]:
    """Assign 'in' and 'out' times (seconds) to shots based on BPM or durations.

    Strategy (POC):
    - If BPM is provided: compute beat interval and round shot durations to whole beats.
    - If a shot provides 'duration', use it as guidance; otherwise use default beats.
    - Return a new list with same metadata and added keys: 'in', 'out', 'in_beat', 'out_beat'.
    """
    updated = []

    if not shots:
        return []

    if bpm is not None:
        # Use beat-aligned durations
        beat_interval = 60.0 / float(bpm)
        cumulative_beats = 0

        # Estimate average duration if missing
        durations = [s.get('duration') for s in shots if s.get('duration')]
        avg_duration = float(sum(durations) / len(durations)) if durations else (beat_interval * default_beats_per_shot)

        for s in shots:
            raw_duration = s.get('duration')
            if raw_duration is None:
                # assign default duration in beats
                beats = default_beats_per_shot
            else:
                # convert duration seconds to nearest beat count
                beats = max(1, int(round(float(raw_duration) / beat_interval)))

            in_beat = cumulative_beats
            out_beat = in_beat + beats
            in_sec = beat_to_time(in_beat, bpm)
            out_sec = beat_to_time(out_beat, bpm)

            new_shot = dict(s)
            new_shot.update({'in': in_sec, 'out': out_sec, 'in_beat': in_beat, 'out_beat': out_beat})
            updated.append(new_shot)

            cumulative_beats = out_beat

    else:
        # Fallback: use durations if present, otherwise use a default of 2 seconds
        cumulative = 0.0
        for s in shots:
            duration = float(s.get('duration', 2.0))
            in_sec = cumulative
            out_sec = cumulative + duration
            new_shot = dict(s)
            new_shot.update({'in': in_sec, 'out': out_sec})
            updated.append(new_shot)
            cumulative = out_sec

    logger.info("AutoCut assigned in/out for %d shots (bpm=%s)", len(updated), str(bpm))
    return updated
