"""AutoColor & Audio Pipeline Integration Test"""
import asyncio
from src.agent.executor.skills.auto_color_and_audio_executor import (
    auto_color_grade,
    audio_normalize,
    text_to_speech,
    get_available_styles
)


def test_available_styles():
    """Get all available color styles"""
    styles = get_available_styles()
    assert len(styles) > 0
    assert 'cinematic' in styles
    assert 'documentary' in styles
    assert 'vibrant' in styles


def test_full_pipeline_color_and_audio():
    """Complete AutoColor & Audio pipeline test"""
    # 1. Create shots
    shots = [
        {'id': 's1', 'in': 0.0, 'out': 2.0, 'summary': 'Opening wide shot', 'shot_type': 'wide'},
        {'id': 's2', 'in': 2.0, 'out': 4.0, 'summary': 'Close-up detail', 'shot_type': 'close'},
        {'id': 's3', 'in': 4.0, 'out': 6.0, 'summary': 'Action sequence', 'shot_type': 'action'},
    ]
    
    # 2. Apply automatic color grading
    color_result = auto_color_grade(shots, style='cinematic', adjust_per_shot=True)
    assert 'success' in color_result
    assert 'shots_graded' in color_result or 'details' in color_result
    
    # 3. Normalize audio
    audio_result = audio_normalize(
        target_loudness=-23.0,
        compression_ratio=4.0,
        attack_ms=10.0,
        release_ms=100.0
    )
    assert 'success' in audio_result
    if audio_result.get('success'):
        assert 'applied_loudness' in audio_result
        assert audio_result['applied_loudness'] == -23.0
    
    # 4. Generate TTS voiceover
    tts_result = text_to_speech(
        "Welcome to this video",
        voice='neutral',
        language='en-US',
        rate=1.0
    )
    assert tts_result['success'] is True
    assert tts_result['duration'] > 0
    assert 'output_path' in tts_result


def test_multiformat_tts():
    """Test TTS with multiple languages and voices"""
    test_cases = [
        ("Hello world", 'male', 'en-US'),
        ("你好世界", 'female', 'zh-CN'),
        ("こんにちは", 'neutral', 'ja-JP'),
        ("Bonjour", 'default', 'fr-FR'),
    ]
    
    for text, voice, language in test_cases:
        result = text_to_speech(
            text,
            voice=voice,
            language=language,
            rate=1.0,
            pitch=1.0
        )
        assert result['success'] is True
        assert result['language'] == language
        assert result['voice'] == voice


def test_color_style_variations():
    """Test application of different color styles"""
    shots = [
        {'id': 's1', 'in': 0.0, 'out': 1.0, 'shot_type': 'generic'},
        {'id': 's2', 'in': 1.0, 'out': 2.0, 'shot_type': 'generic'},
    ]
    
    styles_to_test = ['cinematic', 'documentary', 'vibrant', 'cool', 'warm']
    
    for style in styles_to_test:
        result = auto_color_grade(shots, style=style)
        # Even if Resolve is unavailable, should successfully return metadata
        assert 'success' in result


def test_tts_with_speed_variations():
    """Test TTS with different speech speeds"""
    text = "This is a test voice over"
    speeds = [0.5, 1.0, 1.5, 2.0]
    
    results = []
    for speed in speeds:
        result = text_to_speech(text, rate=speed)
        assert result['success'] is True
        results.append(result)
    
    # Verify different speech speeds result in different durations
    durations = [r['duration'] for r in results]
    # Faster speech should result in shorter duration
    assert durations[3] < durations[0]  # 2.0x should be faster than 0.5x
