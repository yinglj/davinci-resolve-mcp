import os
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Callable, Set

logger = logging.getLogger("davinci-resolve-mcp.proxy")


class ToolProxy:
    """
    Manages tool registration, filtering, and execution.
    Supports 'Search/Execute' mode to handle many tools efficiently.
    """

    def __init__(self, config_path: Optional[Path] = None):
        # 1. Try explicitly passed path
        # 2. Try current directory .resolve-mcp/config.json
        # 3. Try project root (one level up from src)
        # 4. Try home directory ~/.resolve-mcp/config.json

        locations = []
        if config_path:
            locations.append(Path(config_path))

        locations.append(Path.cwd() / ".resolve-mcp" / "config.json")

        # Try to find project root by looking for src/proxy.py
        try:
            file_dir = Path(__file__).parent.resolve()
            project_root = file_dir.parent
            locations.append(project_root / ".resolve-mcp" / "config.json")
        except:
            pass

        locations.append(Path.home() / ".resolve-mcp" / "config.json")

        self.config_path = None
        for loc in locations:
            if loc.exists():
                self.config_path = loc
                break

        if not self.config_path:
            self.config_path = Path.home() / ".resolve-mcp" / "config.json"

        logger.info(f"Using tool proxy config: {self.config_path}")
        self.config = self._load_config()
        self.tool_registry: Dict[str, Dict[str, Any]] = {}
        self.enabled_tools: Set[str] = set()
        self.categories: Dict[str, List[str]] = {}

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from JSON file."""
        if not self.config_path.exists():
            return self._default_config()

        try:
            with open(self.config_path, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            return self._default_config()

    def _default_config(self) -> Dict[str, Any]:
        """Return default configuration."""
        return {
            "mode": "search_execute",  # 'search_execute' or 'full'
            "max_tools": 40,
            "active_profile": "full",
            "profiles": {"full": {"description": "All tools", "categories": "all"}},
        }

    def register_tool(
        self,
        name: str,
        func: Callable,
        category: str = "general",
        description: str = "",
        parameters: Optional[Dict] = None,
        register_mcp: bool = False,
    ):
        """Register a tool with the proxy."""
        self.tool_registry[name] = {
            "name": name,
            "func": func,
            "category": category,
            "description": description or func.__doc__ or "",
            "parameters": parameters or {},
            "register_mcp": register_mcp,
        }

        if category not in self.categories:
            self.categories[category] = []
        if name not in self.categories[category]:
            self.categories[category].append(name)

    def execute_tool(self, tool_name: str, **kwargs) -> Any:
        """Execute a tool by name."""
        if tool_name not in self.tool_registry:
            raise ValueError(f"Tool '{tool_name}' not found")

        tool_info = self.tool_registry[tool_name]
        return tool_info["func"](**kwargs)

    def search_tools(
        self, query: str, category: Optional[str] = None, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Search for tools matching query."""
        results = []
        query_lower = query.lower()

        for name, info in self.tool_registry.items():
            if category and info["category"] != category:
                continue

            if (
                query_lower in name.lower()
                or query_lower in info.get("description", "").lower()
            ):
                results.append(
                    {
                        "name": name,
                        "category": info["category"],
                        "description": info.get("description", ""),
                        "parameters": info.get("parameters", {}),
                    }
                )

            if len(results) >= limit:
                break
        return results

    def get_categories(self) -> List[str]:
        return sorted(self.categories.keys())

    def list_tools(self, category: Optional[str] = None) -> List[str]:
        if category:
            return sorted(self.categories.get(category, []))
        return sorted(self.tool_registry.keys())


# Global proxy instance
_proxy: Optional[ToolProxy] = None


def get_proxy(config_path: Optional[Path] = None) -> ToolProxy:
    global _proxy
    if _proxy is None:
        _proxy = ToolProxy(config_path)
    return _proxy
