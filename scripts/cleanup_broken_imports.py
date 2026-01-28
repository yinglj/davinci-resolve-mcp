#!/usr/bin/env python3
import os
import re
from pathlib import Path


def cleanup_file(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Pattern to find the FIXME followed by dangling lines until the closing parenthesis
    # Matches: # FIXME: src.agent removed\n    item1,\n    item2\n)
    pattern = r"# FIXME: src\.agent removed\n\s+[a-zA-Z0-9_, \n]+\)"
    new_content = re.sub(pattern, "# FIXME: src.agent removed", content)

    if new_content != content:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(new_content)
        return True
    return False


if __name__ == "__main__":
    tests_dir = Path(__file__).resolve().parents[1] / "tests"
    for root, dirs, files in os.walk(tests_dir):
        for file in files:
            if file.endswith(".py"):
                if cleanup_file(Path(root) / file):
                    print(f"Cleaned up: {Path(root) / file}")
