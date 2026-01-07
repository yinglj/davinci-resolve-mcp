#!/usr/bin/env python3
"""Common response helpers for MCP tools.

Standardizes tool output for better AI parsing.
"""

from typing import Any, Dict, Optional


def success_response(
    data: Any = None,
    message: Optional[str] = None,
    context: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Standard success envelope."""
    resp: Dict[str, Any] = {
        "ok": True,
        "data": data,
        "error": None,
    }
    if message is not None:
        resp["message"] = message
    if context is not None:
        resp["context"] = context
    return resp


def error_response(
    code: str,
    message: str,
    *,
    details: Any = None,
    context: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Standard error envelope."""
    err: Dict[str, Any] = {
        "code": code,
        "message": message,
    }
    if details is not None:
        err["details"] = details

    resp: Dict[str, Any] = {
        "ok": False,
        "data": None,
        "error": err,
    }
    if context is not None:
        resp["context"] = context
    return resp
