"""Sync tool bodies are moved off the event loop into a worker thread so a
blocking call cannot freeze the transport."""
import threading
import unittest

import anyio

from src.server import _install_threaded_tool_dispatch


class FakeTool:
    def __init__(self, fn, is_async=False, name="t"):
        self.fn = fn
        self.is_async = is_async
        self.name = name


class FakeManager:
    def __init__(self, tools):
        self._tools = tools


class FakeMCP:
    def __init__(self, tools):
        self._tool_manager = FakeManager(tools)


class ThreadedToolDispatchTest(unittest.TestCase):
    def test_wraps_sync_tools_and_skips_async(self):
        sync_tool = FakeTool(lambda **kw: {"ok": True}, is_async=False, name="sync")
        async_fn = sync_tool  # placeholder
        async_tool = FakeTool(async_fn, is_async=True, name="async")
        mcp = FakeMCP({"sync": sync_tool, "async": async_tool})

        wrapped = _install_threaded_tool_dispatch(mcp)
        self.assertEqual(wrapped, 1)
        self.assertTrue(sync_tool.is_async)   # now presented as async
        self.assertTrue(async_tool.is_async)  # untouched

    def test_wrapped_tool_runs_off_thread_and_returns_result(self):
        main_thread = threading.current_thread().name

        def body(**kwargs):
            return {"value": kwargs["x"], "thread": threading.current_thread().name}

        tool = FakeTool(body, is_async=False, name="body")
        _install_threaded_tool_dispatch(FakeMCP({"body": tool}))

        result = anyio.run(lambda: tool.fn(x=42))
        self.assertEqual(result["value"], 42)
        self.assertNotEqual(result["thread"], main_thread)  # ran off the event-loop thread

    def test_cancel_during_body_does_not_kill_the_session(self):
        # #272: the client cancels while the body is still in its worker
        # thread, and the body finishes afterwards. run_sync shields its wait,
        # so without a cancellation checkpoint the result came back normally,
        # the SDK answered the request a second time, and its "Request already
        # responded to" assert took the whole session down. Driven through the
        # real SDK over the in-memory transport, not the fakes above.
        #
        # MCP SDK 2.x dropped `mcp.server.fastmcp` (renamed to MCPServer) and
        # `mcp.shared.memory.create_connected_server_and_client_session`, so
        # this drives fastmcp's own Client over the in-memory transport. The
        # cancellation comes from the client-side timeout, which is the same
        # cancel path a real client takes — and unlike a hand-built
        # CancelledNotification it does not need the request id, which SDK 2.x
        # keeps inside its dispatcher.
        from fastmcp import FastMCP
        from fastmcp.client import Client
        from fastmcp.client.transports import FastMCPTransport

        app = FastMCP("cancel-probe")
        release = threading.Event()

        @app.tool()
        def slow() -> str:
            release.wait(5)
            return "slow done"

        @app.tool()
        def quick() -> str:
            return "quick done"

        _install_threaded_tool_dispatch(app)
        outcome = {}

        async def scenario():
            async with Client(FastMCPTransport(app)) as client:
                async with anyio.create_task_group() as tg:
                    async def call_slow():
                        try:
                            await client.call_tool("slow", {}, timeout=0.5)
                            outcome["slow"] = "returned"
                        except Exception as exc:
                            outcome["slow"] = str(exc)

                    tg.start_soon(call_slow)
                    await anyio.sleep(0.3)
                    await anyio.sleep(0.4)  # the timeout fires here
                    release.set()  # the body finishes AFTER the cancellation
                with anyio.fail_after(5):
                    result = await client.call_tool("quick", {})
                outcome["quick"] = result.content[0].text

        try:
            anyio.run(scenario)
        finally:
            release.set()
        self.assertIn("timed out", str(outcome.get("slow")))
        self.assertEqual(outcome.get("quick"), "quick done")  # session still serving

    def test_missing_tool_manager_is_a_noop(self):
        self.assertEqual(_install_threaded_tool_dispatch(object()), 0)

    def test_non_mapping_tools_is_a_noop(self):
        # A future SDK shape that isn't a dict must degrade to inline, not crash.
        self.assertEqual(_install_threaded_tool_dispatch(FakeMCP(["not", "a", "map"])), 0)


if __name__ == "__main__":
    unittest.main()
