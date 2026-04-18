import json
import logging
import sys
from pathlib import Path

from fastmcp.resources import ResourceContent, ResourceResult

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import src.api.media as media_api
from src.mcp_resources.media import register_media_resources


class DummyMcp:
    def __init__(self):
        self.resources = {}

    def resource(self, uri: str):
        def decorator(fn):
            self.resources[uri] = fn
            return fn

        return decorator


def _register_media_pool_handler(monkeypatch, clips_payload):
    monkeypatch.setattr(media_api, "list_media_pool_clips", lambda _resolve: clips_payload)
    mcp = DummyMcp()
    register_media_resources(mcp, resolve=object(), logger=logging.getLogger("test"))
    return mcp.resources["resolve://media-pool-clips"]


def _decode_resource_payload(result: ResourceResult):
    assert isinstance(result, ResourceResult)
    assert len(result.contents) == 1
    content = result.contents[0]
    assert isinstance(content, ResourceContent)
    assert isinstance(content.content, str)
    return json.loads(content.content)


def test_media_pool_clips_returns_resource_wrapped_json(monkeypatch):
    handler = _register_media_pool_handler(
        monkeypatch,
        [{"name": "a.mp4", "duration": "00:00:37:14", "fps": 30.0}],
    )

    payload = _decode_resource_payload(handler())
    assert payload == [
        {
            "name": "a.mp4",
            "clip_name": "a.mp4",
            "clipName": "a.mp4",
            "duration": "00:00:37:14",
            "fps": 30.0,
        }
    ]


def test_media_pool_clips_empty_list_returns_empty_json_array(monkeypatch):
    handler = _register_media_pool_handler(monkeypatch, [])
    payload = _decode_resource_payload(handler())
    assert payload == []


def test_media_pool_clips_error_payload_degrades_to_empty_array(monkeypatch):
    handler = _register_media_pool_handler(
        monkeypatch,
        [{"error": "No project currently open"}],
    )
    payload = _decode_resource_payload(handler())
    assert payload == []
