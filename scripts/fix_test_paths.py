#!/usr/bin/env python3
import os
import re
from pathlib import Path


def fix_file(file_path, project_root):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    try:
        rel_path = file_path.relative_to(project_root / "tests")
        depth = len(rel_path.parts) - 1
    except ValueError:
        return False

    # Standardize to use parents[depth + 1] to get project root
    # parents[0] is the file's directory
    # parents[1] is tests/ if file is in tests/ root
    # parents[2] is project_root/ if file is in tests/ root
    # Wait, parents[0] = tests/, parents[1] = project_root/
    # So for depth 0, we need parents[1].
    # For depth 1 (tests/api/file.py), parents[0]=api/, parents[1]=tests/, parents[2]=project_root/
    # So for depth 1, we need parents[2].
    # Formula: depth + 1
    new_path_logic = (
        f"sys.path.insert(0, str(Path(__file__).resolve().parents[{depth + 1}]))"
    )

    # Target our previously injected (wrong) logic as well as any other variants
    pattern1 = r'sys\.path\.insert\(0, str\(Path\(__file__\)\.resolve\(\)\.parents\[\d+\]( / "src")?\)\)'
    pattern2 = (
        r'sys\.path\.insert\(0, str\(Path\(__file__\)\.parent(\.parent)* / "src"\)\)'
    )

    new_content = re.sub(pattern1, new_path_logic, content)
    new_content = re.sub(pattern2, new_path_logic, new_content)

    if new_content != content:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(new_content)
        return True
    return False


if __name__ == "__main__":
    script_path = Path(__file__).resolve()
    project_root = script_path.parents[1]
    tests_dir = project_root / "tests"

    print(f"Project root: {project_root}")
    print(f"Fixing paths in {tests_dir}...")

    fixed_count = 0
    for root, dirs, files in os.walk(tests_dir):
        for file in files:
            if file.endswith(".py"):
                if fix_file(Path(root) / file, project_root):
                    print(f"Fixed: {Path(root) / file}")
                    fixed_count += 1

    print(f"Total files fixed: {fixed_count}")
