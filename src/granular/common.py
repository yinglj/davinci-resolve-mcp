#!/usr/bin/env python3
"""DaVinci Resolve MCP Granular Server - Common Utilities."""

import os
import sys
import platform
from pathlib import Path

def get_platform():
    system = platform.system().lower()
    if system == "darwin":
        return "mac"
    elif system == "windows":
        return "windows"
    return system

def get_resolve_paths():
    system = get_platform()
    if system == "mac":
        api_path = "/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting/Modules"
        lib_path = "/Applications/DaVinci Resolve.app/Contents/Libraries/Fusion"
        modules_path = api_path
    elif system == "windows":
        api_path = "C:\\Program Files\\Blackmagic Design\\DaVinci Resolve\\Developer\\Scripting\\Modules"
        lib_path = "C:\\Program Files\\Blackmagic Design\\DaVinci Resolve\\Fusion.dll"
        modules_path = api_path
    else:
        api_path = os.environ.get("RESOLVE_SCRIPT_API", "")
        lib_path = os.environ.get("RESOLVE_SCRIPT_LIB", "")
        modules_path = os.environ.get("RESOLVE_MODULES_PATH", api_path)
    return {"api_path": api_path, "lib_path": lib_path, "modules_path": modules_path, "platform": system}

paths = get_resolve_paths()
api_path = os.environ.get("RESOLVE_SCRIPT_API") or paths["api_path"]
lib_path = os.environ.get("RESOLVE_SCRIPT_LIB") or paths["lib_path"]
modules_path = os.path.join(api_path, "Modules") if api_path else paths["modules_path"]

if api_path:
    os.environ["RESOLVE_SCRIPT_API"] = api_path
if lib_path:
    os.environ["RESOLVE_SCRIPT_LIB"] = lib_path
if modules_path and modules_path not in sys.path:
    sys.path.append(modules_path)

VERSION = "2.0.7"

import logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("davinci-resolve-mcp-granular")

try:
    import DaVinciResolveScript as dvr_script
    _resolve_instance = dvr_script.scriptapp("DaVinciResolve")
except Exception:
    _resolve_instance = None

def get_resolve():
    """Get the Resolve instance, reconnecting if necessary."""
    global _resolve_instance

    # If we have a cached instance, return it
    if _resolve_instance is not None:
        return _resolve_instance

    # Try to get from resolve_manager (used by compound server)
    try:
        import importlib
        resolve_manager = importlib.import_module("src.utils.resolve_manager").resolve_manager
        if resolve_manager.instance is not None:
            _resolve_instance = resolve_manager.instance
            return _resolve_instance
        # Try to reconnect
        if resolve_manager.connect():
            _resolve_instance = resolve_manager.instance
            return _resolve_instance
    except Exception:
        pass

    # Try to reconnect via DaVinciResolveScript
    try:
        import DaVinciResolveScript as dvr_script
        _resolve_instance = dvr_script.scriptapp("DaVinciResolve")
        return _resolve_instance
    except Exception:
        return None

resolve = _resolve_instance  # Backward compatibility alias

try:
    from fastmcp import FastMCP
    mcp = FastMCP("DaVinciResolveMCP-Granular", on_duplicate="ignore")
except ImportError:
    mcp = None

def get_project_manager():
    if resolve:
        return resolve.GetProjectManager()
    return None

def get_current_project():
    pm = get_project_manager()
    if pm:
        return pm.GetCurrentProject()
    return None

def get_current_timeline():
    project = get_current_project()
    if project:
        return project.GetCurrentTimeline()
    return None

def get_media_pool():
    project = get_current_project()
    if project:
        return project.GetMediaPool()
    return None

def get_media_storage():
    if resolve:
        return resolve.GetMediaStorage()
    return None

def get_fusion():
    if resolve:
        return resolve.Fusion()
    return None
