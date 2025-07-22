"""
file: demo.py
Show how to connect to MCP servers that use the SSE transport using our MCPTools and MultiMCPTools classes.
Check the README.md file for instructions on how to run these examples.
"""

import asyncio
from typing import cast

from agno.agent import Agent, RunResponse
from agno.models.openai import OpenAIChat
from agno.tools.mcp import MCPTools, MultiMCPTools
from agno.models.ollama import Ollama
from rich.pretty import pprint

# This is the URL of the MCP server we want to use.
server_url = "http://localhost:3001/sse"
server_url2 = "http://localhost:8000/sse"

async def run_agent(message: str) -> None:
    async with MCPTools(transport="sse", url=server_url) as mcp_tools:
        agent = Agent(
            instructions="You are a SQL query agent. Use the MCP tools to execute SQL queries.",
            model=OpenAIChat(id="gpt-4o"),
            tools=[mcp_tools],
            markdown=True,
        )
        await agent.aprint_response(message=message,
                                    stream=True,
                                    markdown=True)


# Using MultiMCPTools, we can connect to multiple MCP servers at once, even if they use different transports.
# In this example we connect to both our example server (SSE transport), and a different server (stdio transport).
async def run_agent_with_multimcp(message: str) -> None:
    async with MultiMCPTools(
            commands=["uvx mcp-server-time --local-timezone=Asia/Shanghai"],
            urls=[server_url, server_url2],
            urls_transports=["sse", "sse"],
    ) as mcp_tools:
        agent = Agent(
            name="MultiMCPAgent",
            instructions=
            "You are a database agent. Use the MCP tools to complete the user's queries.",
            # model=OpenAIChat(id="gpt-4o"),
            model=Ollama(id="hf.co/Qwen/Qwen3-0.6B-GGUF:latest"),
            tools=[mcp_tools],
            markdown=True,
            add_datetime_to_instructions=True,
            show_tool_calls=True,
        )
        run_response = await agent.arun(message=message,
                                    stream=True,
                                    markdown=True,
                                    stream_intermediate_steps=True)
        async for run_response_chunk in run_response:
            run_response_chunk = cast(RunResponse, run_response_chunk)
            pprint(run_response_chunk.to_json())

if __name__ == "__main__":
    # asyncio.run(run_agent("select 1 from dual"))
    asyncio.run(
        run_agent_with_multimcp(
            "select 1 from dual, get table define of mysql.user, 获取时间，再执行查询serv_id=100001,acct_id=-1,bill_month=-1的实时账单数据"
        )
    )
