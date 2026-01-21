import asyncio
from src.api import tools_operations
from src.proxy import get_proxy


def test_create_fusion_composition_poc():
    # POC mode: planner may be unavailable in test env
    resp = tools_operations.create_fusion_composition(
        "summary", [{"start": 0, "end": 10, "desc": "shot1"}]
    )
    assert resp["success"] is True
    assert "composition_spec" in resp


def test_create_audio_chain_poc():
    resp = tools_operations.create_audio_chain()
    assert resp["success"] is True
    assert "chain" in resp


def test_job_lifecycle():
    # Schedule a job (auto_color)
    job_resp = tools_operations.auto_color_timeline(None)
    assert job_resp["success"] is True
    job_id = job_resp["job_id"]

    # Small delay to allow job to start
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.sleep(0.3))

    status = tools_operations.job_status(job_id)
    assert status["success"] is True
    assert "job" in status

    cancel = tools_operations.cancel_job(job_id)
    assert cancel["success"] is True
    assert cancel["job"]["status"] in ("cancelled", "done", "running")


def test_register_tools_with_proxy():
    proxy = get_proxy()
    tools_operations.register_tools(proxy)
    # Minimal expectations: tools registered in categories
    categories = proxy.get_categories()
    assert "fusion" in categories
    assert "jobs" in categories
    # Execute a registered tool via proxy
    res = proxy.execute_tool("audio.create_chain")
    assert res["success"] is True
    assert "chain" in res


if __name__ == "__main__":
    print("Running tests...")
    test_create_fusion_composition_poc()
    print("test_create_fusion_composition_poc passed")
    test_create_audio_chain_poc()
    print("test_create_audio_chain_poc passed")

    # Run async test
    async def run_async_tests():
        # Setup loop for the test
        # We need to manually simulate what happens in the server
        # Since _create_job calls create_task, we need to be in a loop

        # Calling auto_color_timeline will verify create_task works
        # and job starts
        job_resp = tools_operations.auto_color_timeline(None)
        assert job_resp["success"] is True
        job_id = job_resp["job_id"]

        # Give the job task a moment to run
        await asyncio.sleep(0.3)

        status = tools_operations.job_status(job_id)
        assert status["success"] is True
        assert "job" in status

        cancel = tools_operations.cancel_job(job_id)
        assert cancel["success"] is True

    asyncio.run(run_async_tests())
    print("test_job_lifecycle (async) passed")

    test_register_tools_with_proxy()
    print("test_register_tools_with_proxy passed")
    print("All tests passed!")
