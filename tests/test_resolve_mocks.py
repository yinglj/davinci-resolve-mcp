import sys
import types


def test_resolve_mock_module():
    # Create a fake src.resolve_mcp_server module
    mod = types.ModuleType('src.resolve_mcp_server')
    class Dummy:
        def CreateTimeline(self, name):
            return f"created:{name}"
    mod.get_resolve = lambda: Dummy()

    sys.modules['src.resolve_mcp_server'] = mod

    # Now import and use
    from src.resolve_mcp_server import get_resolve
    r = get_resolve()
    assert hasattr(r, 'CreateTimeline')
    assert r.CreateTimeline('T1') == 'created:T1'
