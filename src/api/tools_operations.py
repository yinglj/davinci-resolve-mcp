"""Tools Operations - Bridge between MCP and Planner/Executor

This module registers a set of high-level "tools" with the proxy. Each tool
provides a small, well-defined operation that can be executed via the ToolProxy
(`proxy.execute_tool`). Tools support POC fallback (when Resolve is not
connected) and integrate with existing planner and executor modules when
available.

Registered tool names (examples):
- fusion.create_composition
- fusion.apply_to_timeline
- audio.create_chain
- color.auto_color_timeline
- render.preview
- jobs.status
- jobs.cancel

POC-mode responses are intentionally simple dictionaries to allow easy
unit-testing and predictable behavior when Resolve isn't available.
"""
from typing import Any, Dict, List, Optional
import logging
import asyncio
import uuid

from src.proxy import get_proxy

logger = logging.getLogger(__name__)

# Try to import planner/executor functions; fall back gracefully
try:
    from src.agent.planner.skills.fusion_composition import plan_fusion_composition
except Exception:
    plan_fusion_composition = None

try:
    from src.agent.executor.skills.fusion_executor import apply_fusion_composition
except Exception:
    apply_fusion_composition = None

try:
    from src.agent.executor.skills.resolve_advanced_integration import (
        create_fairlight_audio_chain,
    )
except Exception:
    create_fairlight_audio_chain = None

# Simple in-memory job store for POC job lifecycle
_JOB_STORE: Dict[str, Dict[str, Any]] = {}


# -----------------
# Tool implementations
# -----------------

def _create_job(record: Dict[str, Any]) -> str:
    job_id = str(uuid.uuid4())
    _JOB_STORE[job_id] = {"status": "queued", "progress": 0, "result": None, **record}

    # Simulate async processing
    asyncio.create_task(_run_job(job_id))
    return job_id


async def _run_job(job_id: str) -> None:
    try:
        _JOB_STORE[job_id]["status"] = "running"
        for i in range(1, 6):
            await asyncio.sleep(0.1)
            _JOB_STORE[job_id]["progress"] = i * 20
        _JOB_STORE[job_id]["status"] = "done"
        _JOB_STORE[job_id]["result"] = {"message": "Completed (POC)"}
    except Exception as e:
        logger.exception(f"Job {job_id} failed: {e}")
        _JOB_STORE[job_id]["status"] = "failed"
        _JOB_STORE[job_id]["result"] = {"error": str(e)}


# Fusion: plan composition

def create_fusion_composition(
    script_summary: str,
    shot_list: List[Dict[str, Any]],
    style: str = "modern",
    effect_intensity: float = 0.7,
    enable_3d: bool = False,
) -> Dict[str, Any]:
    """Create a Fusion composition plan. Returns a composition spec or job id.

    If planner is available, call it; otherwise return POC spec.
    """
    logger.debug("create_fusion_composition called")
    if plan_fusion_composition:
        spec = plan_fusion_composition(script_summary, shot_list, style, effect_intensity, enable_3d)
        return {"success": True, "composition_spec": spec}

    # POC response
    spec = {
        "id": f"poc_comp_{uuid.uuid4().hex[:8]}",
        "style": style,
        "effects": ["reveal"],
        "shots": shot_list,
    }
    return {"success": True, "composition_spec": spec, "note": "POC mode - planner unavailable"}


# Fusion: apply composition to timeline

def apply_fusion_to_timeline(composition_spec: Dict[str, Any], timeline_id: Optional[str] = None) -> Dict[str, Any]:
    logger.debug("apply_fusion_to_timeline called")
    if apply_fusion_composition:
        res = apply_fusion_composition(composition_spec, timeline_id)
        return {"success": True, "applied": res}

    # POC: schedule a job
    job_id = _create_job({"tool": "apply_fusion", "composition": composition_spec})
    return {"success": True, "job_id": job_id, "note": "POC scheduled job"}


# Audio: create chain

def create_audio_chain(
    target_loudness: float = -23.0,
    compression_ratio: float = 4.0,
    gate_threshold: float = -40.0,
    eq_profile: str = "neutral",
) -> Dict[str, Any]:
    logger.debug("create_audio_chain called")
    if create_fairlight_audio_chain:
        res = create_fairlight_audio_chain(target_loudness, compression_ratio, gate_threshold, eq_profile)
        return {"success": True, "chain": res}

    # POC
    chain = {
        "chain_id": f"poc_chain_{uuid.uuid4().hex[:8]}",
        "processors": [
            {"type": "Gate", "threshold": gate_threshold},
            {"type": "Compressor", "ratio": compression_ratio, "target": target_loudness},
            {"type": "EQ", "profile": eq_profile},
            {"type": "Limiter", "ceiling": -0.5},
        ],
    }
    return {"success": True, "chain": chain, "note": "POC mode - Resolve not connected"}


# Color: auto color timeline

def auto_color_timeline(timeline_id: Optional[str] = None, keyframe_strategy: str = "auto", smoothing_type: str = "medium") -> Dict[str, Any]:
    logger.debug("auto_color_timeline called")
    # POC schedule
    job_id = _create_job({"tool": "auto_color", "timeline_id": timeline_id})
    return {"success": True, "job_id": job_id}


# Render preview

def render_preview(timeline_id: str, start_frame: int, end_frame: int, preset: str = "default") -> Dict[str, Any]:
    logger.debug("render_preview called")
    job_id = _create_job({"tool": "render_preview", "timeline_id": timeline_id, "range": [start_frame, end_frame]})
    return {"success": True, "job_id": job_id}


# Job lifecycle

def job_status(job_id: str) -> Dict[str, Any]:
    logger.debug(f"job_status called for {job_id}")
    if job_id not in _JOB_STORE:
        return {"success": False, "error": "job_not_found"}
    return {"success": True, "job": _JOB_STORE[job_id]}


def cancel_job(job_id: str) -> Dict[str, Any]:
    logger.debug(f"cancel_job called for {job_id}")
    if job_id not in _JOB_STORE:
        return {"success": False, "error": "job_not_found"}
    _JOB_STORE[job_id]["status"] = "cancelled"
    return {"success": True, "job": _JOB_STORE[job_id]}


# Registration

def register_tools(proxy):
    """Register tools with the given proxy."""
    proxy.register_tool(
        "fusion.create_composition",
        create_fusion_composition,
        category="fusion",
        description="Plan a Fusion composition from script and shots",
        parameters={"script_summary": {"type": "string"}},
    )

    proxy.register_tool(
        "fusion.apply_to_timeline",
        apply_fusion_to_timeline,
        category="fusion",
        description="Apply a composition to a timeline (schedules job in POC)",
    )

    proxy.register_tool(
        "audio.create_chain",
        create_audio_chain,
        category="audio",
        description="Create or configure a Fairlight audio chain",
    )

    proxy.register_tool(
        "color.auto_color_timeline",
        auto_color_timeline,
        category="color",
        description="Automatically color grade a timeline (schedules a job)",
    )

    proxy.register_tool(
        "render.preview",
        render_preview,
        category="render",
        description="Render a preview segment of a timeline",
    )

    proxy.register_tool("jobs.status", job_status, category="jobs", description="Get job status")
    proxy.register_tool("jobs.cancel", cancel_job, category="jobs", description="Cancel a job")


# Optionally expose module-level register on import (for convenience)
if __name__ != "__main__":
    try:
        proxy = get_proxy()
        register_tools(proxy)
    except Exception:
        # Avoid noisy import-time errors in test environments
        pass
