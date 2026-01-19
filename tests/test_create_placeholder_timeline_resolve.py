from src.agent.executor.skills.create_placeholder_timeline import create_placeholder_timeline
import sys
import types


def test_create_placeholder_with_resolve_mock():
    # Prepare script-level mock of src.resolve_mcp_server.get_resolve
    mod = types.ModuleType('src.resolve_mcp_server')
    # Import our detailed mock
    from tests.mocks.resolve_mock import DummyResolve
    mod.get_resolve = lambda: DummyResolve()
    sys.modules['src.resolve_mcp_server'] = mod

    shots = [
        {'id': 'shot_001', 'summary': 'A wide shot', 'duration': 5, 'shot_type': 'wide'},
        {'id': 'shot_002', 'summary': 'Close up', 'duration': 4, 'shot_type': 'close'},
    ]

    # Place markers at the start (default)
    res = create_placeholder_timeline(shots, project='TestProj', options={'timeline_name': 'MockTL', 'frame_rate': 24, 'marker_position': 'start'})
    assert res['timeline_name'] == 'MockTL'
    assert res['created_shots_count'] == 2
    assert 'markers' in res
    assert len(res['markers']) == 2
    # Validate marker frames roughly equal cumulative seconds * frame_rate
    assert res['markers'][0]['frame'] == 0
    assert res['markers'][1]['frame'] == 5 * 24

    # Middle markers
    res_mid = create_placeholder_timeline(shots, project='TestProj', options={'timeline_name': 'MockTL_MID', 'frame_rate': 24, 'marker_position': 'middle'})
    assert len(res_mid['markers']) == 2
    assert res_mid['markers'][0]['frame'] == int( (0 + 5/2) * 24 )

    # Test track and offset per shot
    shots_with_track = [
        {'id': 'shot_010', 'summary': 'Track test', 'duration': 4, 'shot_type': 'wide', 'marker_track': 2, 'offset': 1},
    ]
    res_track = create_placeholder_timeline(shots_with_track, project='TestProj', options={'timeline_name': 'MockTL_TRACK', 'frame_rate': 24, 'marker_position': 'start'})
    assert res_track['markers'][0]['track'] == 2
    assert res_track['markers'][0]['frame'] == 1 * 24
