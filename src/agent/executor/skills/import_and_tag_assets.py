"""ImportAndTagAssets POC

Provides a minimal asset import and metadata tagging interface suitable for POC and tests.
"""
from typing import List, Dict, Any
import logging
import os

logger = logging.getLogger(__name__)

ASSET_DB: Dict[str, Dict[str, Any]] = {}


def import_assets(paths_or_urls: List[str], metadata: Dict[str, Any] = None) -> List[Dict[str, Any]]:
    """Import assets by recording metadata and returning normalized asset entries.

    This POC does not download remote URLs; it records the path/URL and metadata
    into an in-memory 'ASSET_DB' and returns entries with generated ids.
    """
    metadata = metadata or {}
    created = []
    for p in paths_or_urls:
        asset_id = f"asset_{len(ASSET_DB) + 1:06d}"
        entry = {
            'id': asset_id,
            'source': p,
            'metadata': metadata.copy(),
            'exists': os.path.exists(p)
        }
        ASSET_DB[asset_id] = entry
        created.append(entry)
        logger.info("Imported asset %s (exists=%s)", p, entry['exists'])
    return created


def query_assets_by_tag(tag: str) -> List[Dict[str, Any]]:
    results = []
    for entry in ASSET_DB.values():
        tags = entry['metadata'].get('tags', [])
        if tag in tags:
            results.append(entry)
    return results
