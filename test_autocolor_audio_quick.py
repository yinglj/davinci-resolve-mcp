#!/usr/bin/env python3
"""Quick test for AutoColor & Audio integration"""
import sys
sys.path.insert(0, '/Users/Diameter/Downloads/davinci-resolve-mcp')

from src.agent.executor.skills.resolve_color_and_audio import (
    create_color_grade_from_style,
    normalize_audio_loudness,
    generate_tts_voiceover,
    apply_auto_color_to_shots,
    STYLE_PRESETS
)

print("=" * 60)
print("AutoColor & Audio Integration Test")
print("=" * 60)

# 1. Style presets
print("\n1. Available Color Styles:")
for style_name in STYLE_PRESETS:
    print(f"   - {style_name}: {STYLE_PRESETS[style_name]['description']}")

# 2. Audio normalization
print("\n2. Audio Normalization:")
result = normalize_audio_loudness(None, target_loudness=-23.0)
print(f"   Success: {result['success']}")
if result.get('settings'):
    print(f"   Algorithm: {result['settings'].get('algorithm')}")
    print(f"   Target: {result['settings'].get('target_loudness_lufs')} LUFS")

# 3. TTS generation
print("\n3. TTS Text-to-Speech Generation:")
tts_result = generate_tts_voiceover("This is a test voice over", language='en-US', rate=1.0)
print(f"   Success: {tts_result['success']}")
print(f"   Duration: {tts_result.get('duration', 0):.1f}s")
print(f"   Output Path: {tts_result.get('output_path')}")

# 4. Color grading
print("\n4. Automatic Color Grading:")
result = create_color_grade_from_style(None, style_sample='cinematic')
print(f"   Style: {result.get('style')}")
print(f"   Nodes Created: {result.get('nodes_created', 0)}")

# 5. Apply auto color to shots
print("\n5. Apply Automatic Color to Shots:")
shots = [
    {'id': 's1', 'in': 0.0, 'out': 2.0, 'shot_type': 'wide'},
    {'id': 's2', 'in': 2.0, 'out': 4.0, 'shot_type': 'close'},
    {'id': 's3', 'in': 4.0, 'out': 6.0, 'shot_type': 'action'},
]
result = apply_auto_color_to_shots(None, shots, style='vibrant', adjust_per_shot=True)
print(f"   Success: {result.get('success', False)}")
print(f"   Shots Processed: {result.get('shots_graded', 0)}/{len(shots)}")
print(f"   Style: {result.get('style')}")

print("\n" + "=" * 60)
print("✓ All Tests Complete")
print("=" * 60)
