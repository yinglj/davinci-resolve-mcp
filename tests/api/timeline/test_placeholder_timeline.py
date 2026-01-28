# FIXME: src.agent removed


def test_create_placeholder_basic():
    shots = [
        {'id': 'shot_001', 'summary': 'A wide shot of mountains', 'duration': 5, 'shot_type': 'wide'},
        {'id': 'shot_002', 'summary': 'Close up of hiker', 'duration': 4, 'shot_type': 'close'},
    ]
    res = create_placeholder_timeline(shots, project='TestProj', options={'timeline_name': 'TestTL'})
    assert res['timeline_name'] == 'TestTL'
    assert res['created_shots_count'] == 2
    assert res['project'] == 'TestProj'
    assert res['shots'][0]['id'] == 'shot_001'


def test_create_placeholder_defaults():
    shots = []
    res = create_placeholder_timeline(shots)
    assert res['timeline_name'] == 'AutoTimeline'
    assert res['created_shots_count'] == 0
