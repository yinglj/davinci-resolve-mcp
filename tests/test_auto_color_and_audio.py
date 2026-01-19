from src.agent.executor.skills.auto_color_and_audio import apply_auto_color, process_audio


def test_apply_auto_color():
    shots = [{'id': 's1'}, {'id': 's2'}]
    res = apply_auto_color(shots, style_sample='cinematic')
    assert res['graded'] is True
    assert 'applied_lut' in res
    assert res['shots_graded'] == 2


def test_process_audio_with_tts_and_path():
    res = process_audio(audio_path='/tmp/sample.wav', tts_text='Hello world')
    assert res['normalized'] is True
    assert res['noise_reduced'] is True
    assert res['tts_generated'] is True
    assert 'tts_path' in res
    assert res['source'] == '/tmp/sample.wav'
