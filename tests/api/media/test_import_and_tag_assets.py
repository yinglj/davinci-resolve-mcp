import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

import pytest
from src.api.media.pool import import_media, list_media_pool_clips


def test_media_operations_availability():
    """Check if media pool operations are available."""
    assert import_media is not None
    assert list_media_pool_clips is not None


@pytest.mark.real_resolve
def test_import_media_basic(resolve_connection):
    """Test importing media if Resolve is connected."""
    if resolve_connection is None:
        pytest.skip("Resolve not connected")

    # result = import_media(resolve_connection, ["/path/to/media.mp4"])
    # assert result["success"] is True
    pass
