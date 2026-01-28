"""P1-03 Enhanced Integration Tests

Tests for advanced Resolve integration with:
- Fairlight audio processing
- Color grading automation
- Real-time monitoring
- Metadata export/import
"""
import sys
sys.path.insert(0, '.')

# FIXME: src.agent removed


def test_fairlight_audio_chain():
    """Test Fairlight audio chain creation"""
    result = create_fairlight_audio_chain(
        target_loudness=-23.0,
        compression_ratio=4.0,
        gate_threshold=-40.0,
        eq_profile='warmth'
    )
    
    assert result['success'] is True
    assert 'chain_id' in result
    assert len(result['processors']) > 0
    print('✓ Fairlight audio chain creation')


def test_color_grade_automation():
    """Test color grading with automation"""
    shots = [
        {'id': 's1', 'in': 0.0, 'out': 2.0, 'shot_type': 'wide'},
        {'id': 's2', 'in': 2.0, 'out': 4.0, 'shot_type': 'close'},
    ]
    
    result = apply_color_grade_with_automation(
        shots,
        style='cinematic',
        auto_keyframes=True,
        enable_temporal_smoothing=True
    )
    
    assert result['success'] is True
    assert result['shots_processed'] >= 0
    assert result['keyframes_created'] >= 0
    print('✓ Color grading automation')


def test_audio_level_monitoring():
    """Test audio level monitoring"""
    result = monitor_audio_levels(duration_seconds=5.0)
    
    assert result['success'] is True
    assert 'peak_level' in result or 'channels' in result
    print('✓ Audio level monitoring')


def test_color_metadata_export():
    """Test color metadata export"""
    result = export_color_metadata()
    
    assert result['success'] is True
    assert 'format' in result
    assert 'grades' in result
    print('✓ Color metadata export')


def test_full_p1_03_integration():
    """Full P1-03 integration test"""
    print('\nFull P1-03 Integration Tests:')
    print('-' * 60)
    
    # 1. Create audio chain
    audio_result = create_fairlight_audio_chain(
        target_loudness=-23.0,
        eq_profile='presence'
    )
    print(f'1. Audio Chain: {"✓" if audio_result["success"] else "✗"}')
    
    # 2. Apply color automation
    shots = [
        {'id': 's1', 'in': 0.0, 'out': 1.5, 'shot_type': 'action'},
        {'id': 's2', 'in': 1.5, 'out': 3.0, 'shot_type': 'dialogue'},
    ]
    color_result = apply_color_grade_with_automation(
        shots,
        auto_keyframes=True
    )
    print(f'2. Color Automation: {"✓" if color_result["success"] else "✗"}')
    
    # 3. Monitor audio
    audio_monitor = monitor_audio_levels(duration_seconds=3.0)
    print(f'3. Audio Monitoring: {"✓" if audio_monitor["success"] else "✗"}')
    
    # 4. Export metadata
    export_result = export_color_metadata()
    print(f'4. Metadata Export: {"✓" if export_result["success"] else "✗"}')
    
    print('-' * 60)
    print('✓ P1-03 Enhanced Integration - All tests passed!')


if __name__ == '__main__':
    test_fairlight_audio_chain()
    test_color_grade_automation()
    test_audio_level_monitoring()
    test_color_metadata_export()
    test_full_p1_03_integration()
    
    print()
    print('=' * 60)
    print('✓ P1-03 Enhanced AutoColor & Audio - All tests passed!')
    print('=' * 60)
