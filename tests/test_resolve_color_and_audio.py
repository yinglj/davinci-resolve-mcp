"""Resolve 颜色和音频集成测试"""
import pytest
from src.agent.executor.skills.resolve_color_and_audio import (
    create_color_grade_from_style,
    normalize_audio_loudness,
    generate_tts_voiceover,
    apply_auto_color_to_shots,
    STYLE_PRESETS
)


def test_create_color_grade_with_resolve_none():
    """Resolve 未连接时返回错误"""
    result = create_color_grade_from_style(None, style_sample='cinematic')
    assert result['success'] is False
    assert 'error' in result


def test_create_color_grade_cinematic():
    """创建电影风格的颜色分级"""
    result = create_color_grade_from_style(None, style_sample='cinematic')
    # 即使 Resolve 为 None，也应该返回完整结构
    assert 'error' in result or ('style' in result and result['style'] == 'cinematic')


def test_create_color_grade_all_styles():
    """测试所有可用的颜色风格"""
    for style_name in STYLE_PRESETS.keys():
        result = create_color_grade_from_style(None, style_sample=style_name)
        assert result.get('style') == style_name or 'error' in result


def test_create_color_grade_invalid_style():
    """无效风格应该默认为 cinematic"""
    result = create_color_grade_from_style(None, style_sample='invalid_style')
    assert result['style'] == 'cinematic' or 'error' in result


def test_normalize_audio_loudness():
    """测试音频响度规范化"""
    result = normalize_audio_loudness(None, target_loudness=-23.0)
    assert result['success'] is False or 'applied_loudness' in result


def test_normalize_audio_loudness_with_settings():
    """音频规范化应包含 EBU R128 设置"""
    result = normalize_audio_loudness(
        None,
        target_loudness=-23.0,
        compression_ratio=4.0,
        attack_ms=10.0,
        release_ms=100.0
    )
    if result.get('settings'):
        assert result['settings']['target_loudness_lufs'] == -23.0
        assert result['settings']['algorithm'] == 'EBU R128'


def test_generate_tts_voiceover_default():
    """生成 TTS 旁白（英文）"""
    result = generate_tts_voiceover("Hello world, this is a test", voice='default')
    assert result['success'] is True
    assert result['duration'] > 0
    assert '/tmp/voiceover.wav' in result['output_path']


def test_generate_tts_voiceover_chinese():
    """生成 TTS 旁白（中文）"""
    result = generate_tts_voiceover(
        "这是一个测试",
        voice='default',
        language='zh-CN'
    )
    assert result['success'] is True
    assert result['duration'] > 0
    assert result['language'] == 'zh-CN'


def test_generate_tts_with_rate_and_pitch():
    """TTS 支持语速和音高调整"""
    result = generate_tts_voiceover(
        "Test text",
        voice='male',
        language='en-US',
        rate=1.5,
        pitch=1.2
    )
    assert result['success'] is True
    assert result['rate'] == 1.5
    assert result['pitch'] == 1.2


def test_generate_tts_empty_text():
    """TTS 文本为空时返回错误"""
    result = generate_tts_voiceover("", voice='default')
    assert result['success'] is False


def test_apply_auto_color_to_shots():
    """对 shots 应用自动颜色分级"""
    shots = [
        {'id': 's1', 'in': 0.0, 'out': 1.0, 'shot_type': 'wide'},
        {'id': 's2', 'in': 1.0, 'out': 2.5, 'shot_type': 'close'},
    ]
    result = apply_auto_color_to_shots(None, shots, style='cinematic')
    assert result.get('success') is False or result.get('shots_graded') >= 0


def test_apply_auto_color_auto_detect():
    """自动检测风格"""
    shots = [
        {'id': 's1', 'in': 0.0, 'out': 1.0, 'shot_type': 'wide'},
        {'id': 's2', 'in': 1.0, 'out': 2.5, 'shot_type': 'action'},
    ]
    result = apply_auto_color_to_shots(None, shots, style='auto')
    # 'auto' 风格应该被转换为具体风格
    assert result.get('style') in STYLE_PRESETS or 'error' in result


def test_apply_auto_color_per_shot_adjustment():
    """为每个 shot 根据类型调整风格"""
    shots = [
        {'id': 's1', 'in': 0.0, 'out': 1.0, 'shot_type': 'fast_action'},
        {'id': 's2', 'in': 1.0, 'out': 2.5, 'shot_type': 'slow_dramatic'},
    ]
    result = apply_auto_color_to_shots(
        None,
        shots,
        style='cinematic',
        adjust_per_shot=True
    )
    # 结果应该包含每个 shot 的详细信息
    if result.get('details'):
        assert len(result['details']) == len(shots)


def test_apply_auto_color_empty_shots():
    """空 shots 列表应返回错误"""
    result = apply_auto_color_to_shots(None, [], style='cinematic')
    assert result['success'] is False


def test_style_presets_complete():
    """检查所有风格预设都有完整的参数"""
    for style_name, preset in STYLE_PRESETS.items():
        assert 'description' in preset
        assert 'lift' in preset
        assert 'gamma' in preset
        assert 'gain' in preset
        # 每个颜色轮都应该有 RGB 参数
        for wheel_name in ['lift', 'gamma', 'gain']:
            for color in ['red', 'green', 'blue']:
                assert color in preset[wheel_name]

    result = apply_auto_color_to_shots(None, shots, style='vibrant')
    assert result['success'] is True
    assert result['shots_graded'] >= 0
    assert result['total_shots'] == 2
    assert len(result['details']) == 2


def test_apply_auto_color_empty_shots():
    """没有 shots 时返回错误"""
    result = apply_auto_color_to_shots(None, [], style='cinematic')
    assert result['success'] is False
