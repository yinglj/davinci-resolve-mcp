import pytest
from src.agent.planner.skills.auto_cut import beat_to_time, auto_cut_shots


def test_beat_to_time():
    assert beat_to_time(0, 120) == 0.0
    assert beat_to_time(1, 120) == pytest.approx(0.5)
    assert beat_to_time(4, 60) == pytest.approx(4.0)


def test_auto_cut_with_bpm():
    shots = [
        {'id': 's1', 'duration': 1.0},  # should map to 2 beats @120bpm
        {'id': 's2', 'duration': 2.0},
    ]
    out = auto_cut_shots(shots, bpm=120)
    assert len(out) == 2
    # s1: beats 0..2 -> in=0.0, out=1.0
    assert out[0]['in'] == pytest.approx(0.0)
    assert out[0]['out'] == pytest.approx(1.0)
    # s2: beats 2..6 -> in=1.0, out=3.0
    assert out[1]['in'] == pytest.approx(1.0)
    assert out[1]['out'] == pytest.approx(3.0)


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
