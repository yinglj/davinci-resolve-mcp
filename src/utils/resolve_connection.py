#!/usr/bin/env python3
"""
DaVinci Resolve Connection Utilities
"""

import os
import logging
from .platform import get_platform, get_resolve_paths, setup_environment

logger = logging.getLogger("davinci-resolve-mcp.connection")


def initialize_resolve():
    """Initialize connection to DaVinci Resolve application."""
    try:
        # Check environment variables
        env_status = check_environment_variables()
        if not env_status["all_set"]:
            logger.warning(
                f"Missing environment variables: {env_status['missing']}. Attempting to set defaults..."
            )
            set_default_environment_variables()

        # Import the DaVinci Resolve scripting module
        try:
            import DaVinciResolveScript as dvr_script
        except ImportError:
            logger.error("Failed to import DaVinciResolveScript.")
            paths = get_resolve_paths()
            logger.error(f"Please ensure PYTHONPATH includes: {paths['modules_path']}")
            return None

        # Get the resolve object
        resolve = dvr_script.scriptapp("Resolve")

        if resolve is None:
            logger.error("Failed to get Resolve object. Possible reasons:")
            logger.error("1. DaVinci Resolve is not running.")
            logger.error("2. External Scripting is disabled in Resolve Preferences.")
            logger.error(
                "   (System -> Control Panels -> External Control -> Scripting -> set to 'Local' or 'Network')"
            )
            return None

        logger.info(
            f"Connected to DaVinci Resolve: {resolve.GetProductName()} {resolve.GetVersionString()}"
        )
        return resolve

    except Exception as e:
        logger.error(f"Unexpected error initializing Resolve: {str(e)}")
        import traceback

        logger.debug(traceback.format_exc())
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
        "resolve_script_lib": resolve_script_lib,
    }


def set_default_environment_variables():
    """Set the default environment variables based on platform."""
    return setup_environment()
