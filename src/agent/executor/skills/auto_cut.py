"""Executor wrapper for AutoCut POC

This module exposes a callable tool `auto_cut` that TaskExecutor can invoke.
"""
from typing import List, Dict, Any, Optional
from ...planner.skills.auto_cut import auto_cut_shots
import logging

logger = logging.getLogger(__name__)


def auto_cut(shots: List[Dict[str, Any]], bpm: Optional[float] = None, options: Optional[Dict] = None) -> List[Dict[str, Any]]:
    """Apply AutoCut to a shot list and return the updated shot list with in/out times.

    This is a blocking function by design (executor runs it in a threadpool).
    """
    try:
        return auto_cut_shots(shots, bpm=bpm)
    except Exception as e:
        logger.exception("AutoCut failed: %s", str(e))
        # Fallback: return shots unmodified
        return shots
