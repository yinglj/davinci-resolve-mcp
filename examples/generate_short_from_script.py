"""Example: Generate shot-list from a short script and print JSON"""
import json
from src.agent.planner.skills import parse_script_to_shots

SAMPLE_SCRIPT = """
Shot 1: Wide establishing shot of a mountain range at dawn. Snow glints on the peaks.

Shot 2: Close up on a hiker tying boots. The hands are nervous.

Shot 3: The hiker starts walking, the camera follows from behind as they enter the forest.
"""


def main():
    shots = parse_script_to_shots(SAMPLE_SCRIPT)
    print(json.dumps({'shots': shots}, indent=2))


if __name__ == '__main__':
    main()
