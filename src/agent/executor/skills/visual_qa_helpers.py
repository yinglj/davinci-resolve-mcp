"""Visual QA helpers for AutoCut rough cuts

Provides utilities to generate visual summaries, shot timing charts, and thumbnail references
for rough-cut review and validation.
"""
from typing import List, Dict, Any, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


def generate_shot_timing_chart(shots: List[Dict[str, Any]], width: int = 120) -> str:
    """Generate a text-based timing chart for shots.

    Returns an ASCII visualization of shot timings for quick visual inspection.
    """
    if not shots:
        return "(no shots)"

    # Determine total duration
    total_duration = 0.0
    for s in shots:
        if 'out' in s:
            total_duration = max(total_duration, s['out'])
    
    if total_duration <= 0:
        return "(invalid shot times)"

    # Compute pixel width per second
    px_per_sec = width / total_duration

    lines = []
    lines.append(f"Shot Timing Chart (total: {total_duration:.2f}s)")
    lines.append("=" * (width + 20))

    for s in shots:
        shot_id = s.get('id', 'unknown')
        summary = s.get('summary', '')[:20]
        in_time = s.get('in', 0.0)
        out_time = s.get('out', in_time + 1.0)

        # Compute bar positions
        start_px = int(in_time * px_per_sec)
        end_px = int(out_time * px_per_sec)
        duration = out_time - in_time

        bar = ' ' * start_px + '█' * max(1, end_px - start_px)
        line = f"{shot_id:8} | {bar:{width}s} | {duration:.2f}s {summary}"
        lines.append(line)

    lines.append("=" * (width + 20))
    return '\n'.join(lines)


def generate_rough_cut_summary(shots: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Generate summary statistics for rough cut timeline.

    Returns dict with total duration, shot count, average duration, pacing, and recommendations.
    """
    if not shots:
        return {'error': 'no shots'}

    total_duration = 0.0
    min_duration = float('inf')
    max_duration = 0.0
    durations = []

    for s in shots:
        if 'out' in s and 'in' in s:
            duration = s['out'] - s['in']
            durations.append(duration)
            total_duration = s['out']
            min_duration = min(min_duration, duration)
            max_duration = max(max_duration, duration)

    if not durations:
        return {'error': 'no valid shot times'}

    avg_duration = sum(durations) / len(durations) if durations else 0.0

    # Detect pacing
    if avg_duration < 0.7:
        pacing = 'very_fast'
        recommendation = 'Extremely rapid cuts; consider slowing down for viewer comprehension'
    elif avg_duration < 1.2:
        pacing = 'fast'
        recommendation = 'Quick pacing; good for action or music videos'
    elif avg_duration < 2.5:
        pacing = 'moderate'
        recommendation = 'Balanced pacing; suitable for most content'
    elif avg_duration < 4.0:
        pacing = 'slow'
        recommendation = 'Deliberate pacing; good for dramatic or contemplative content'
    else:
        pacing = 'very_slow'
        recommendation = 'Very slow cuts; ensure content supports long-form presentation'

    return {
        'shot_count': len(shots),
        'total_duration': total_duration,
        'average_duration': avg_duration,
        'min_duration': min_duration if min_duration != float('inf') else 0.0,
        'max_duration': max_duration,
        'pacing': pacing,
        'recommendation': recommendation,
        'style': shots[0].get('style', 'unknown') if shots else 'unknown'
    }


def generate_thumbnail_reference(shots: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Generate a reference list for thumbnail generation.

    Each entry includes shot metadata and suggested thumbnail frame time.
    Can be used to guide external thumbnail/poster frame selection.
    """
    refs = []

    for s in shots:
        in_time = s.get('in', 0.0)
        out_time = s.get('out', in_time + 1.0)
        duration = out_time - in_time

        # Suggest thumbnail at middle of shot (or custom if user provided marker_offset_frames)
        thumbnail_offset = duration / 2.0
        thumbnail_time = in_time + thumbnail_offset

        ref = {
            'shot_id': s.get('id', 'unknown'),
            'summary': s.get('summary', ''),
            'in': in_time,
            'out': out_time,
            'duration': duration,
            'thumbnail_time': thumbnail_time,
            'thumbnail_frame': int(thumbnail_time * 30),  # assuming 30fps base
            'shot_type': s.get('shot_type', 'generic')
        }
        refs.append(ref)

    logger.info("Generated %d thumbnail references", len(refs))
    return refs


def generate_beat_visualization(shots: List[Dict[str, Any]], bpm: Optional[float] = None) -> str:
    """Generate a beat-grid visualization for rhythm matching.

    Shows shots aligned to beat grid (if bpm available).
    """
    if not shots or not bpm or bpm <= 0:
        return "(beat visualization requires bpm > 0)"

    beat_interval = 60.0 / bpm
    total_duration = 0.0
    for s in shots:
        if 'out' in s:
            total_duration = max(total_duration, s['out'])

    total_beats = total_duration / beat_interval
    
    lines = []
    lines.append(f"Beat Grid (BPM: {bpm}, {beat_interval:.2f}s/beat)")
    lines.append("=" * 80)

    # Draw beat grid
    beat_marks = []
    for i in range(int(total_beats) + 1):
        beat_time = i * beat_interval
        beat_marks.append((i, beat_time))

    # Overlay shots on beat grid
    for s in shots:
        shot_id = s.get('id', '?')
        in_time = s.get('in', 0.0)
        out_time = s.get('out', in_time + 1.0)
        in_beat = in_time / beat_interval
        out_beat = out_time / beat_interval

        # Simple text rep: show which beats this shot spans
        beats_spanned = f"[{in_beat:.1f} -> {out_beat:.1f} beats]"
        lines.append(f"  {shot_id:8} {beats_spanned}")

    lines.append("=" * 80)
    return '\n'.join(lines)
