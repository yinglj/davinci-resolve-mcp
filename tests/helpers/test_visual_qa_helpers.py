# FIXME: src.agent removed


def test_generate_shot_timing_chart():
    shots = [
        {'id': 's1', 'in': 0.0, 'out': 1.0, 'summary': 'Wide'},
        {'id': 's2', 'in': 1.0, 'out': 3.0, 'summary': 'Close'},
    ]
    chart = generate_shot_timing_chart(shots, width=60)
    assert 's1' in chart
    assert 's2' in chart
    assert '█' in chart


def test_generate_rough_cut_summary():
    shots = [
        {'id': 's1', 'in': 0.0, 'out': 1.0},
        {'id': 's2', 'in': 1.0, 'out': 3.0},
    ]
    summary = generate_rough_cut_summary(shots)
    assert summary['shot_count'] == 2
    assert summary['total_duration'] == 3.0
    assert 'average_duration' in summary
    assert 'pacing' in summary
    assert 'recommendation' in summary


def test_generate_rough_cut_summary_pacing_detection():
    # Very fast pacing
    fast_shots = [
        {'id': 's1', 'in': 0.0, 'out': 0.5},
        {'id': 's2', 'in': 0.5, 'out': 1.0},
    ]
    fast_summary = generate_rough_cut_summary(fast_shots)
    assert fast_summary['pacing'] == 'very_fast'

    # Very slow pacing
    slow_shots = [
        {'id': 's1', 'in': 0.0, 'out': 5.0},
        {'id': 's2', 'in': 5.0, 'out': 10.0},
    ]
    slow_summary = generate_rough_cut_summary(slow_shots)
    assert slow_summary['pacing'] == 'very_slow'


def test_generate_thumbnail_reference():
    shots = [
        {'id': 's1', 'in': 0.0, 'out': 1.0, 'summary': 'Wide', 'shot_type': 'wide'},
        {'id': 's2', 'in': 1.0, 'out': 3.0, 'summary': 'Close', 'shot_type': 'close'},
    ]
    refs = generate_thumbnail_reference(shots)
    assert len(refs) == 2
    assert refs[0]['shot_id'] == 's1'
    assert 'thumbnail_time' in refs[0]
    assert refs[0]['thumbnail_time'] == 0.5  # middle of 1-second shot


def test_generate_beat_visualization():
    shots = [
        {'id': 's1', 'in': 0.0, 'out': 0.5},
        {'id': 's2', 'in': 0.5, 'out': 1.0},
    ]
    vis = generate_beat_visualization(shots, bpm=120)
    assert 's1' in vis
    assert 's2' in vis
    assert 'beat' in vis.lower()
