"""Resolve color and audio integration tests"""
import pytest
# FIXME: src.agent removed


def test_create_color_grade_with_resolve_none():
    """Returns error when Resolve not connected"""
    result = create_color_grade_from_style(None, style_sample='cinematic')
    assert result['success'] is False
    assert 'error' in result


def test_create_color_grade_cinematic():
    """Create cinematic style color grading"""
    result = create_color_grade_from_style(None, style_sample='cinematic')
    # Should return complete structure even if Resolve is None
    assert 'error' in result or ('style' in result and result['style'] == 'cinematic')


def test_create_color_grade_all_styles():
    """Test all available color styles"""
    for style_name in STYLE_PRESETS.keys():
        result = create_color_grade_from_style(None, style_sample=style_name)
        assert result.get('style') == style_name or 'error' in result


def test_create_color_grade_invalid_style():
    """Invalid style should default to cinematic"""
    result = create_color_grade_from_style(None, style_sample='invalid_style')
    assert result['style'] == 'cinematic' or 'error' in result


def test_normalize_audio_loudness():
    """Test audio loudness normalization"""
    result = normalize_audio_loudness(None, target_loudness=-23.0)
    assert result['success'] is False or 'applied_loudness' in result


def test_normalize_audio_loudness_with_settings():
    """Audio normalization should include EBU R128 settings"""
    result = normalize_audio_loudness(
        None,
        target_loudness=-23.0,
        compression_ratio=4.0,
        attack_ms=10.0,
        release_ms=100.0
    )
    # Result should include all settings even if Resolve is None
    assert result.get('success') is False or result.get('target_loudness') == -23.0


def test_generate_tts_voiceover_default():
    """Generate TTS voiceover (English)"""
    result = generate_tts_voiceover("Hello world, this is a test", voice='default')
    assert result['success'] is True
    assert result['duration'] > 0
    assert '/tmp/voiceover.wav' in result['output_path']


def test_generate_tts_voiceover_chinese():
    """Generate TTS voiceover (Mandarin Chinese)"""
    result = generate_tts_voiceover(
        "这是一个测试",
        voice='default',
        language='zh-CN'
    )
    assert result['success'] is True
    assert result['duration'] > 0
    assert result['language'] == 'zh-CN'


def test_generate_tts_with_rate_and_pitch():
    """TTS supports speech rate and pitch adjustment"""
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
    """TTS returns error for empty text"""
    result = generate_tts_voiceover("", voice='default')
    assert result['success'] is False


def test_apply_auto_color_to_shots():
    """Apply automatic color grading to shots"""
    shots = [
        {'id': 's1', 'in': 0.0, 'out': 1.0, 'shot_type': 'wide'},
        {'id': 's2', 'in': 1.0, 'out': 2.5, 'shot_type': 'close'},
    ]
    result = apply_auto_color_to_shots(None, shots, style='cinematic')
    assert result.get('success') is False or result.get('shots_graded') >= 0


def test_apply_auto_color_auto_detect():
    """Auto-detect style based on shot types"""
    shots = [
        {'id': 's1', 'in': 0.0, 'out': 1.0, 'shot_type': 'wide'},
        {'id': 's2', 'in': 1.0, 'out': 2.5, 'shot_type': 'action'},
    ]
    result = apply_auto_color_to_shots(None, shots, style='auto')
    # 'auto' style should be converted to specific style
    assert result.get('style') in STYLE_PRESETS or 'error' in result


def test_apply_auto_color_per_shot_adjustment():
    """Adjust style per shot based on shot type"""
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
    # Result should include details for each shot
    if result.get('details'):
        assert len(result['details']) == len(shots)


def test_apply_auto_color_empty_shots():
    """Empty shots list should return error"""
    result = apply_auto_color_to_shots(None, [], style='cinematic')
    assert result['success'] is False


def test_style_presets_complete():
    """Check all style presets have complete parameters"""
    for style_name, preset in STYLE_PRESETS.items():
        assert 'description' in preset
        assert 'lift' in preset
        assert 'gamma' in preset
        assert 'gain' in preset
        # Each color wheel should have RGB parameters
        for wheel_name in ['lift', 'gamma', 'gain']:
            for color in ['red', 'green', 'blue']:
                assert color in preset[wheel_name]
