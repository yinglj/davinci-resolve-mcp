from __future__ import annotations

from collections.abc import Sequence
from typing import overload

import mcp.types
from mcp.types import Icon, ToolAnnotations
from fastmcp.server.providers.base import Provider
from fastmcp.tools.tool import Tool, ToolResult
from fastmcp.server.tasks.config import TaskMeta
from fastmcp.utilities.versions import VersionSpec
from mcp.server.fastmcp.server import FastMCP as LegacyFastMCP


class LegacyTool(Tool):
    _server: LegacyFastMCP
    _original_name: str | None = None

    def __init__(
        self,
        server: LegacyFastMCP,
        original_name: str,
        *,
        name: str,
        title: str | None,
        description: str | None,
        parameters: dict[str, object],
        output_schema: dict[str, object] | None,
        annotations: ToolAnnotations | None,
        meta: dict[str, object] | None,
        icons: list[Icon] | None,
    ):
        super().__init__(
            name=name,
            title=title,
            description=description,
            parameters=parameters,
            output_schema=output_schema,
            annotations=annotations,
            meta=meta,
            icons=icons,
        )
        self._server = server
        self._original_name = original_name

    @overload
    async def _run(
        self, arguments: dict[str, object], task_meta: None = None
    ) -> ToolResult: ...

    @overload
    async def _run(
        self, arguments: dict[str, object], task_meta: TaskMeta
    ) -> mcp.types.CreateTaskResult: ...

    async def _run(
        self, arguments: dict[str, object], task_meta: TaskMeta | None = None
    ) -> ToolResult | mcp.types.CreateTaskResult:
        result = await self._server.call_tool(
            self._original_name or self.name, arguments
        )
        if isinstance(result, list):
            return ToolResult(content=result)
        if isinstance(result, dict):
            return ToolResult(structured_content=result)
        return ToolResult(structured_content={"result": result})


class LegacyToolProvider(Provider):
    _server: LegacyFastMCP

    def __init__(self, server: LegacyFastMCP):
        super().__init__()
        self._server = server

    async def _list_tools(self) -> Sequence[Tool]:
        raw_tools = await self._server.list_tools()
        return [self._wrap_tool(tool) for tool in raw_tools]

    async def _get_tool(
        self, name: str, version: VersionSpec | None = None
    ) -> Tool | None:
        raw_tools = await self._server.list_tools()
        for tool in raw_tools:
            if tool.name == name:
                return self._wrap_tool(tool)
        return None

    def _wrap_tool(self, tool: mcp.types.Tool) -> LegacyTool:
        return LegacyTool(
            server=self._server,
            original_name=tool.name,
            name=tool.name,
            title=tool.title,
            description=tool.description,
            parameters=tool.inputSchema,
            output_schema=tool.outputSchema,
            annotations=tool.annotations,
            meta=tool.meta,
            icons=tool.icons,
        )
