#!/usr/bin/env python3
import asyncio
import json
import logging
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("demo_tools_usage")

# Determine project root and add to sys.path for imports if needed
import os
import sys

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(project_root)

# Import ClientSimulator to reuse its connection logic
# Assuming client_simulator.py is in davinci_resolve_agent/
sys.path.append(os.path.join(project_root, "davinci_resolve_agent"))

try:
    from client_simulator import ClientSimulator
except ImportError:
    # Also try direct import if running from root
    from davinci_resolve_agent.client_simulator import ClientSimulator


async def run_demo():
    print("=== DaVinci Resolve MCP Tools Demo ===")

    # Initialize client (points to default localhost:8080)
    client = ClientSimulator()

    # helper to print results
    def print_result(step_name: str, result: Dict[str, Any]):
        status = (
            "✅ Success" if result.get("success") or "result" in result else "❌ Failed"
        )
        print(f"\n--- {step_name} ---")
        print(f"Status: {status}")
        print(json.dumps(result, indent=2, ensure_ascii=False))

    # 1. List available tools
    print("\n[1] Listing available tools in 'fusion' category...")
    tools_list = await client.send_rpc_request(
        "list_tools_in_category", {"category": "fusion"}
    )
    # Correct response structure adjustment if needed (server returns result directly or wrapped)
    # The client.send_rpc_request returns the 'result' part of JSON-RPC response usually
    print_result("List Tools", tools_list)

    # 2. Create Fusion Composition (POC)
    print("\n[2] Creating Fusion Composition (POC)...")
    fusion_args = {
        "script_summary": "A futuristic sci-fi intro with neon text",
        "shot_list": [
            {"start": 0, "end": 60, "desc": "Fade in title"},
            {"start": 60, "end": 120, "desc": "Camera flythrough"},
        ],
        "style": "cyberpunk",
        "effect_intensity": 0.9,
    }
    fusion_res = await client.send_tool_request(
        "fusion.create_composition", fusion_args
    )
    print_result("Create Composition", fusion_res)

    comp_spec = fusion_res.get("composition_spec")

    # 3. Apply to Timeline (Job)
    if comp_spec:
        print("\n[3] Applying Composition to Timeline (Async Job)...")
        apply_args = {"composition_spec": comp_spec}
        apply_res = await client.send_tool_request(
            "fusion.apply_to_timeline", apply_args
        )
        print_result("Apply to Timeline", apply_res)

        job_id = apply_res.get("job_id")

        # 4. Check Job Status
        if job_id:
            print(f"\n[4] Polling Job Status for Job ID: {job_id}...")
            for _ in range(5):
                await asyncio.sleep(0.5)
                status_res = await client.send_tool_request(
                    "jobs.status", {"job_id": job_id}
                )
                status = status_res.get("job", {}).get("status")
                progress = status_res.get("job", {}).get("progress")
                print(f"   Status: {status}, Progress: {progress}%")
                if status == "done":
                    print("   Job completed!")
                    break

    # 5. Audio Chain Demo
    print("\n[5] Creating Audio Chain...")
    audio_res = await client.send_tool_request(
        "audio.create_chain", {"target_loudness": -14.0}
    )
    print_result("Create Audio Chain", audio_res)

    print("\n=== Demo Completed ===")


if __name__ == "__main__":
    try:
        asyncio.run(run_demo())
    except KeyboardInterrupt:
        print("\nDemo cancelled.")
    except Exception as e:
        print(f"\nAn error occurred: {e}")
