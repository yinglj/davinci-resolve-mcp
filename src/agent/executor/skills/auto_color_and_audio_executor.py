"""P1-03 AutoColor & Audio 的执行器工具

与 Resolve 集成的颜色分级、音频规范化和 TTS 生成。
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
    """执行器工具：对 shots 应用自动颜色分级。
    
    Args:
        shots: shot 列表 (each with 'id', 'in', 'out', 'shot_type')
        style: 风格代码或 'auto' (自动检测)
        apply_to_all_clips: 是否应用到时间线中的所有 clips
        adjust_per_shot: 是否为每个 shot 根据其 shot_type 微调风格
    
    Returns:
        执行结果包含成功状态、应用的 shots 数、详细信息
    """
    try:
        from src.resolve_mcp_server import get_resolve
        resolve = get_resolve()
    except Exception:
        resolve = None
    
    try:
        # 如果 apply_to_all_clips，对所有 clips 应用，否则只对提供的 shots 应用
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
    """执行器工具：规范化时间线音频响度。
    
    遵循 EBU R128 广播标准的音频规范化。
    
    Args:
        target_loudness: 目标响度（LUFS，推荐 -23.0）
        timeline_name: 时间线名称（None = 当前）
        compression_ratio: 压缩比（e.g., 4.0）
        attack_ms: 压缩器 attack 时间
        release_ms: 压缩器 release 时间
    
    Returns:
        规范化结果
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
    """执行器工具：生成 TTS 旁白。
    
    支持多种语言和语音参数。
    
    Args:
        text: 旁白文本
        voice: 语音选择 ('default'|'male'|'female'|'neutral'|'child')
        output_path: 输出文件路径
        language: 语言代码 ('en-US'|'zh-CN'|'ja-JP')
        rate: 语速倍数 (0.5 = 一半速度，2.0 = 两倍速度)
        pitch: 音高倍数
    
    Returns:
        TTS 结果
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
    """获取所有可用的颜色风格。
    
    Returns:
        风格预设字典，包含描述和参数
    """
    return STYLE_PRESETS
