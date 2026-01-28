import pytest
# FIXME: src.agent removed


def test_beat_to_time():
    assert beat_to_time(0, 120) == 0.0
    assert beat_to_time(1, 120) == pytest.approx(0.5)
    assert beat_to_time(4, 60) == pytest.approx(4.0)


def test_snap_to_beat():
    # 120 bpm = 0.5 sec per beat
    assert snap_to_beat(0.25, 120, 'nearest') == pytest.approx(0.0)
    assert snap_to_beat(0.3, 120, 'nearest') == pytest.approx(0.5)
    assert snap_to_beat(0.24, 120, 'down') == pytest.approx(0.0)
    assert snap_to_beat(0.5, 120, 'up') == pytest.approx(0.5)


def test_detect_beat_density():
    tight_shots = [
        {'id': 's1', 'duration': 0.5},
        {'id': 's2', 'duration': 0.6},
    ]
    assert detect_beat_density(tight_shots, 120) == 'tight'

    normal_shots = [
        {'id': 's1', 'duration': 1.0},
        {'id': 's2', 'duration': 1.2},
    ]
    assert detect_beat_density(normal_shots, 120) == 'normal'

    loose_shots = [
        {'id': 's1', 'duration': 3.0},
        {'id': 's2', 'duration': 3.5},
    ]
    assert detect_beat_density(loose_shots, 120) == 'loose'


def test_auto_cut_with_bpm():
    shots = [
        {'id': 's1', 'duration': 1.0},  # should map to ~2 beats @120bpm
        {'id': 's2', 'duration': 2.0},
    ]
    out = auto_cut_shots(shots, bpm=120)
    assert len(out) == 2
    # s1: in=0.0, out ~ 1.0
    assert out[0]['in'] == pytest.approx(0.0, abs=0.1)
    assert out[0]['out'] == pytest.approx(1.0, abs=0.1)


def test_auto_cut_with_style_tight():
    shots = [
        {'id': 's1'},  # no duration - will use style-adjusted default
        {'id': 's2'},
    ]
    out = auto_cut_shots(shots, bpm=120, style='tight')
    assert out[0]['style'] == 'tight'
    assert out[0]['out'] - out[0]['in'] < 0.5  # tight means short


def test_auto_cut_with_style_loose():
    shots = [
        {'id': 's1'},
        {'id': 's2'},
    ]
    out = auto_cut_shots(shots, bpm=120, style='loose')
    assert out[0]['style'] == 'loose'
    assert out[0]['out'] - out[0]['in'] > 1.0  # loose means longer


def test_auto_cut_without_bpm():
    shots = [
        {'id': 's1', 'duration': 1.5},
        {'id': 's2'},  # uses default 2.0
    ]
    out = auto_cut_shots(shots, bpm=None)
    assert out[0]['in'] == pytest.approx(0.0)
    assert out[0]['out'] == pytest.approx(1.5)
    assert out[1]['in'] == pytest.approx(1.5)
    assert out[1]['out'] == pytest.approx(3.5)


def test_auto_cut_min_duration_constraint():
    shots = [
        {'id': 's1', 'duration': 0.1},  # very short - should be clamped to min
    ]
    out = auto_cut_shots(shots, bpm=120, min_duration=0.5)
    assert out[0]['out'] - out[0]['in'] >= pytest.approx(0.5)


def test_auto_cut_max_duration_constraint():
    shots = [
        {'id': 's1', 'duration': 10.0},  # very long - should be clamped to max
    ]
    out = auto_cut_shots(shots, bpm=120, max_duration=3.0)
    assert out[0]['out'] - out[0]['in'] <= pytest.approx(3.1, abs=0.2)


def test_auto_cut_edge_case_missing_duration():
    shots = [
        {'id': 's1'},
        {'id': 's2'},
        {'id': 's3'},
    ]
    out = auto_cut_shots(shots, bpm=120, default_beats_per_shot=4)
    # Each should get ~2 seconds (4 beats @ 120 bpm)
    for shot in out:
        assert 'in' in shot and 'out' in shot


def test_auto_cut_snap_to_beats():
    shots = [
        {'id': 's1', 'duration': 0.7},  # odd value, should snap
    ]
    out_snapped = auto_cut_shots(shots, bpm=120, snap_to_beats=True)
    out_unsnapped = auto_cut_shots(shots, bpm=120, snap_to_beats=False)
    # snapped should have beat-aligned boundaries
    assert 'in_beat' in out_snapped[0]
    assert 'in_beat' in out_unsnapped[0]

