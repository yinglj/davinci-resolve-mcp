import json
from src.agent.planner.skills import parse_script_to_shots


def test_simple_script():
    script = """
    Shot 1: A wide establishing shot of a city skyline. The sun sets.

    Shot 2: Close up on the protagonist's face as they whisper.

    Shot 3: The car speeds away, tires screeching, camera pans to follow.
    """
    shots = parse_script_to_shots(script)
    assert len(shots) >= 3
    assert shots[0]['id'] == 'shot_001'
    assert shots[1]['shot_type'] == 'close' or shots[1]['summary'].lower().startswith("close")


def test_scene_headings():
    script = """
    INT. OFFICE - DAY
    A medium shot of a cluttered desk. Papers everywhere.

    INT. HALLWAY - NIGHT
    The protagonist walks slowly, heavy breathing.
    """
    shots = parse_script_to_shots(script)
    assert len(shots) >= 2
    assert 'INT. OFFICE' in shots[0]['notes'] or 'INT. OFFICE' in shots[0]['summary']


def test_long_paragraph_splits():
    script = """
    Shot 1: A long paragraph describing a scene: The camera tracks across the room. It finds a dog sleeping. A vase falls and shatters. People scream.
    """
    shots = parse_script_to_shots(script)
    # Expect the long block to be split into multiple shots
    assert len(shots) >= 3
    # Ensure ids increment
    assert shots[0]['id'] == 'shot_001'
    assert shots[1]['id'] == 'shot_002'


def test_empty_input():
    shots = parse_script_to_shots("")
    assert shots == []
