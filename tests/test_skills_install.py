"""`davinci-resolve-mcp skills install` writes the portable corpus where IDEs read it.

One check for the bin's skills command: the skill files land in .claude/skills/,
the rule files land in each IDE's directory, and an out-of-tree install does not
overwrite a project's own .github/copilot-instructions.md.
"""

import shutil
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
BIN = REPO / "bin" / "davinci-resolve-mcp.mjs"
EXPECTED_SKILLS = {
    p.parent.name for p in (REPO / ".agents" / "skills").glob("*/SKILL.md")
}

pytestmark = pytest.mark.skipif(
    shutil.which("node") is None or not BIN.exists(),
    reason="node (or the npm bin) is not available",
)


def _install(target):
    result = subprocess.run(
        ["node", str(BIN), "skills", "install", "--dir", str(target)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=120,
    )
    assert result.returncode == 0, result.stderr
    return result.stdout


def test_skills_install_lands_in_every_ide(tmp_path):
    assert EXPECTED_SKILLS, "the repo has no skill corpus to install"
    _install(tmp_path)

    installed = {p.parent.name for p in (tmp_path / ".claude" / "skills").glob("*/SKILL.md")}
    assert installed == EXPECTED_SKILLS

    # Each host reads a different file, and the generator is the only place
    # that knows the formats — assert one representative per host.
    for rel in (
        ".cursor/rules/resolve-color.mdc",
        ".windsurf/rules/resolve-color.md",
        ".clinerules",
        ".roo/rules/resolve-mcp.md",
        ".continue/rules/resolve-mcp.md",
        ".github/instructions/resolve-color.instructions.md",
    ):
        assert (tmp_path / rel).exists(), rel
    assert "BEGIN GENERATED: domain-routing" in (tmp_path / "AGENTS.md").read_text(encoding="utf-8")

    # An external project keeps its own Copilot instructions.
    assert not (tmp_path / ".github" / "copilot-instructions.md").exists()


def test_claude_only_skips_ide_rule_files(tmp_path):
    subprocess.run(
        ["node", str(BIN), "skills", "install", "--dir", str(tmp_path), "--claude-only"],
        check=True,
        capture_output=True,
        timeout=120,
    )
    assert (tmp_path / ".claude" / "skills").is_dir()
    assert not (tmp_path / ".cursor").exists()
    assert not (tmp_path / "AGENTS.md").exists()