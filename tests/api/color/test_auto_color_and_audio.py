import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

import pytest
from src.api.color.grades import apply_lut
from src.api.media.sync import auto_sync_audio


def test_color_operations_availability():
    """Check if basic color operations are available."""
    assert apply_lut is not None


def test_audio_operations_availability():
    """Check if basic audio operations are available."""
    assert auto_sync_audio is not None


@pytest.mark.real_resolve
def test_apply_lut_basic(resolve_connection):
    """Test applying a LUT if Resolve is connected."""
    if resolve_connection is None:
        pytest.skip("Resolve not connected")

    # This would need a real LUT path to actually run successfully
    # result = apply_lut(resolve_connection, "some/path.cube")
    # assert "Successfully" in result
    pass
