#!/usr/bin/env python3
"""
DaVinci Resolve Connection Utilities
"""

import os
import logging

logger = logging.getLogger("davinci-resolve-mcp.connection")

def initialize_resolve():
    """Initialize connection to DaVinci Resolve application."""
    try:
        # Import the DaVinci Resolve scripting module
        import DaVinciResolveScript as dvr_script
        
        # Get the resolve object
        resolve = dvr_script.scriptapp("Resolve")
        
        if resolve is None:
            logger.error("Failed to get Resolve object. Is DaVinci Resolve running?")
            return None
        
        logger.info(f"Connected to DaVinci Resolve: {resolve.GetProductName()} {resolve.GetVersionString()}")
        return resolve
    
    except ImportError:
        logger.error("Failed to import DaVinciResolveScript. Check environment variables.")
        logger.error("RESOLVE_SCRIPT_API, RESOLVE_SCRIPT_LIB, and PYTHONPATH must be set correctly.")
        logger.error("On macOS, typically:")
        logger.error('export RESOLVE_SCRIPT_API="/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting"')
        logger.error('export RESOLVE_SCRIPT_LIB="/Applications/DaVinci Resolve/DaVinci Resolve.app/Contents/Libraries/Fusion/fusionscript.so"')
        logger.error('export PYTHONPATH="$PYTHONPATH:$RESOLVE_SCRIPT_API/Modules/"')
        return None
    
    except Exception as e:
        logger.error(f"Unexpected error initializing Resolve: {str(e)}")
        return None

def check_environment_variables():
    """Check if the required environment variables are set."""
    resolve_script_api = os.environ.get("RESOLVE_SCRIPT_API")
    resolve_script_lib = os.environ.get("RESOLVE_SCRIPT_LIB")
    
    missing_vars = []
    if not resolve_script_api:
        missing_vars.append("RESOLVE_SCRIPT_API")
    if not resolve_script_lib:
        missing_vars.append("RESOLVE_SCRIPT_LIB")
    
    return {
        "all_set": len(missing_vars) == 0,
        "missing": missing_vars,
        "resolve_script_api": resolve_script_api,
        "resolve_script_lib": resolve_script_lib
    }

def set_default_environment_variables():
    """Set the default environment variables for macOS."""
    os.environ["RESOLVE_SCRIPT_API"] = "/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting"
    os.environ["RESOLVE_SCRIPT_LIB"] = "/Applications/DaVinci Resolve/DaVinci Resolve.app/Contents/Libraries/Fusion/fusionscript.so"
    
    # Update PYTHONPATH
    python_path = os.environ.get("PYTHONPATH", "")
    modules_path = os.path.join(os.environ["RESOLVE_SCRIPT_API"], "Modules")
    
    if modules_path not in python_path:
        if python_path:
            os.environ["PYTHONPATH"] = f"{python_path}:{modules_path}"
        else:
            os.environ["PYTHONPATH"] = modules_path 