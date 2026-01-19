"""P1-03 AutoColor & Audio Executor Tools

Color grading, audio normalization, and TTS generation integrated with Resolve.
"""
from typing import List, Dict, Any, Optional
from .resolve_color_and_audio import (
    create_color_grade_from_style,
    normalize_audio_loudness,
    generate_tts_voiceover,
    apply_auto_color_to_shots,
    STYLE_PRESETS
)
import logging

logger = logging.getLogger(__name__)


def auto_color_grade(
    shots: List[Dict[str, Any]],
    style: str = 'auto',
    apply_to_all_clips: bool = False,
    adjust_per_shot: bool = False
) -> Dict[str, Any]:
    """Executor tool: Apply automatic color grading to shots.
    
    Args:
        shots: List of shots (each with 'id', 'in', 'out', 'shot_type')
        style: Style code or 'auto' for auto-detection
        apply_to_all_clips: Apply to all clips in timeline
        adjust_per_shot: Adjust style per shot based on shot_type
    
    Returns:
        Execution result with success status, graded shots count, details
    """
    try:
        from src.resolve_mcp_server import get_resolve
        resolve = get_resolve()
    except Exception:
        resolve = None
    
    try:
        # If apply_to_all_clips, apply to all clips; otherwise apply to provided shots
        if apply_to_all_clips:
            result = create_color_grade_from_style(resolve, style_sample=style, apply_to_all_clips=True)
        else:
            result = apply_auto_color_to_shots(resolve, shots, style=style, adjust_per_shot=adjust_per_shot)
        
        return result
    except Exception as e:
        logger.exception("AutoColor execution failed: %s", str(e))
        return {'success': False, 'error': str(e)}


def audio_normalize(
    target_loudness: float = -23.0,
    timeline_name: Optional[str] = None,
    compression_ratio: float = 4.0,
    attack_ms: float = 10.0,
    release_ms: float = 100.0
) -> Dict[str, Any]:
    """Executor tool: Normalize timeline audio loudness.
    
    Audio normalization following EBU R128 broadcast standard.
    
    Args:
        target_loudness: Target loudness in LUFS (recommended -23.0)
        timeline_name: Timeline name (None = current)
        compression_ratio: Compression ratio (e.g., 4.0)
        attack_ms: Compressor attack time in milliseconds
        release_ms: Compressor release time in milliseconds
    
    Returns:
        Normalization result
    """
    try:
        from src.resolve_mcp_server import get_resolve
        resolve = get_resolve()
    except Exception:
        resolve = None
    
    try:
        return normalize_audio_loudness(
            resolve,
            target_loudness=target_loudness,
            timeline_name=timeline_name,
            compression_ratio=compression_ratio,
            attack_ms=attack_ms,
            release_ms=release_ms
        )
    except Exception as e:
        logger.exception("Audio normalization failed: %s", str(e))
        return {'success': False, 'error': str(e)}


def text_to_speech(
    text: str,
    voice: str = 'default',
    output_path: str = '/tmp/voiceover.wav',
    language: str = 'en-US',
    rate: float = 1.0,
    pitch: float = 1.0
) -> Dict[str, Any]:
    """Executor tool: Generate TTS voiceover.
    
    Support for multiple languages and voice parameters.
    
    Args:
        text: Voiceover text
        voice: Voice choice ('default'|'male'|'female'|'neutral'|'child')
        output_path: Output file path
        language: Language code ('en-US'|'zh-CN'|'ja-JP')
        rate: Speech rate multiplier (0.5 = half speed, 2.0 = double speed)
        pitch: Pitch multiplier
    
    Returns:
        TTS result
    """
    try:
        return generate_tts_voiceover(
            text,
            voice=voice,
            output_path=output_path,
            language=language,
            rate=rate,
            pitch=pitch
        )
    except Exception as e:
        logger.exception("TTS generation failed: %s", str(e))
        return {'success': False, 'error': str(e)}


def get_available_styles() -> Dict[str, Dict[str, Any]]:
    """Get all available color grading styles.
    
    Returns:
        Style presets dictionary with descriptions and parameters
    """
    return STYLE_PRESETS
