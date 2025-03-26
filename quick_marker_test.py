#!/usr/bin/env python3
"""
Quick test script for the enhanced marker functionality
"""

import os
import sys

# Set environment variables for DaVinci Resolve scripting
RESOLVE_API_PATH = "/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting"
RESOLVE_LIB_PATH = "/Applications/DaVinci Resolve/DaVinci Resolve.app/Contents/Libraries/Fusion/fusionscript.so"
RESOLVE_MODULES_PATH = os.path.join(RESOLVE_API_PATH, "Modules")

os.environ["RESOLVE_SCRIPT_API"] = RESOLVE_API_PATH
os.environ["RESOLVE_SCRIPT_LIB"] = RESOLVE_LIB_PATH
sys.path.append(RESOLVE_MODULES_PATH)

# Import the timeline_operations module directly
sys.path.append(".")
from src.api.timeline_operations import add_marker

# Import DaVinci Resolve scripting
import DaVinciResolveScript as dvr_script

# Connect to Resolve
resolve = dvr_script.scriptapp("Resolve")
if not resolve:
    print("Error: Could not connect to DaVinci Resolve")
    sys.exit(1)

print(f"Connected to {resolve.GetProductName()} {resolve.GetVersionString()}")

# Test with different frames
test_frames = [None, 86450, 87000, 88000, 89000, 90000]
for frame in test_frames:
    note = f"Testing frame {frame or 'auto-selected'}"
    result = add_marker(resolve, frame, "Green", note)
    print(f"Test with frame={frame}: {result}")

print("Testing completed") 