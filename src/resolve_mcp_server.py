#!/usr/bin/env python3
"""
DaVinci Resolve MCP Server - Granular Entry Point
Version: 2.0.7
"""

import sys
import os
import logging
from pathlib import Path

# Add parent directory to path
project_dir = Path(__file__).parent.parent
if str(project_dir) not in sys.path:
    sys.path.insert(0, str(project_dir))

from src.granular.common import mcp, VERSION

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("davinci-resolve-mcp-granular")

# Import granular tools
from src.granular import (
    folder, gallery, graph, media_pool, media_pool_item,
    media_storage, project, resolve_control, timeline, timeline_item,
    render, presets, layout, cloud
)

def main():
    logger.info(f"Starting DaVinci Resolve MCP Server (Granular Mode) v{VERSION}")
    logger.info("342 granular tools available")
    mcp.run()

if __name__ == "__main__":
    main()
