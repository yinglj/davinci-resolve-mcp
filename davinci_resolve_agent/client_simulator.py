# file: client_simulator.py
"""
MIT License

Copyright (c) 2025 Lijing Ying <yinglj@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

@file: client_simulator.py
@description: Client simulator for interacting with MCP server, with support for
              command history, up/down key navigation, and Linux-style ! command matching.
@license: MIT
@date: 2025-04-22
"""

import os
import asyncio
import json
from typing import AsyncGenerator, Dict, Optional
import aiohttp
import pyfiglet
from logger import logger
from prompt_toolkit import PromptSession
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.key_binding import KeyBindings
from termcolor import colored

class ClientSimulator:
    """A client simulator for interacting with MCP server.

    This class provides functionality to:
    - Connect to and communicate with an MCP RPC server
    - Manage client sessions
    - Handle streaming and non-streaming requests
    - Support command history and Linux-style ! command matching
    - Process user queries in an interactive chat loop

    Attributes:
        rpc_url (str): The URL endpoint for RPC requests
        stream_url (str): The URL endpoint for streaming requests
        api_key (str): Authentication key for the MCP server
        session_id (Optional[str]): Current active session ID
        request_id (int): Counter for tracking RPC requests
        timeout (aiohttp.ClientTimeout): Request timeout settings
        command_history (list): List of previously executed commands
        history (InMemoryHistory): Prompt toolkit history manager
        bindings (KeyBindings): Keyboard shortcut bindings
        prompt_session (PromptSession): Interactive prompt handler
    """
    def __init__(self, rpc_url: str = "http://localhost:8080/rpc", api_key: str = None, timeout: int = 120):
        self.rpc_url = rpc_url
        self.stream_url = f"{rpc_url}/stream"
        self.api_key = api_key or "sk-1234567890abcdef"
        self.session_id: Optional[str] = None
        self.request_id = 0
        self.timeout = aiohttp.ClientTimeout(total=timeout, sock_read=120)
        # Command history
        self.command_history = []
        # Prompt session with history support
        self.history = InMemoryHistory()
        self.bindings = KeyBindings()
        self.prompt_session = PromptSession(
            message="> [Session: None] ",
            history=self.history,
            key_bindings=self.bindings,
            multiline=False
        )

    async def send_rpc_request(self, method: str, params: Dict) -> Dict:
        self.request_id += 1
        request = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params,
            "id": self.request_id
        }
        headers = {"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}
        try:
            async with aiohttp.ClientSession() as session:
                logger.debug(f"Sending RPC request: {json.dumps(request, indent=2, ensure_ascii=False)}")
                logger.print(f"Sending request:\n{json.dumps(request, indent=2, ensure_ascii=False)}")
                async with session.post(self.rpc_url, json=request, headers=headers, timeout=self.timeout) as response:
                    logger.info(f"RPC response status: {response.status}")
                    if response.status != 200:
                        error_msg = f"RPC request failed with status {response.status}"
                        logger.error(error_msg)
                        return {"error": error_msg}
                    result = await response.json()
                    logger.debug(f"RPC response: {json.dumps(result, indent=2, ensure_ascii=False)}")
                    logger.print(f"Received response:\n{json.dumps(result, indent=2, ensure_ascii=False)}")
                    return result
        except asyncio.TimeoutError:
            error_msg = f"RPC request timed out after {self.timeout.total} seconds"
            logger.error(error_msg)
            return {"error": error_msg}
        except Exception as e:
            error_msg = f"RPC request error: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}

    async def send_stream_request(self, method: str, params: Dict) -> AsyncGenerator[Dict, None]:
        self.request_id += 1
        request = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params,
            "id": self.request_id
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}" if self.api_key else "",
            "Accept": "text/event-stream"
        }
        try:
            async with aiohttp.ClientSession() as session:
                logger.info(f"Sending stream RPC request with ID {self.request_id}")
                logger.debug(f"Request details: {json.dumps(request, indent=2, ensure_ascii=False)}")
                logger.print(f"Sending stream request:\n{json.dumps(request, indent=2, ensure_ascii=False)}")
                async with session.post(self.stream_url, json=request, headers=headers, timeout=self.timeout) as response:
                    logger.info("Received stream response: status=%s, headers=%s", response.status, response.headers)
                    if response.status != 200:
                        error_msg = f"Stream request failed with status {response.status}"
                        logger.error(error_msg)
                        yield {"error": error_msg}
                        return

                    # Check if the response is JSON (non-streaming error)
                    content_type = response.headers.get("Content-Type", "")
                    if "application/json" in content_type:
                        try:
                            result = await response.json()
                            logger.info(f"Received JSON response: {json.dumps(result, indent=2, ensure_ascii=False)}")
                            yield result
                            return
                        except json.JSONDecodeError as e:
                            logger.error(f"Failed to decode JSON response: {str(e)}")
                            yield {"error": {"message": f"Invalid JSON response: {str(e)}"}}
                            return

                    # Handle streaming response
                    logger.info("Starting stream content iteration")
                    try:
                        initial_wait = 5
                        start_time = asyncio.get_event_loop().time()
                        while asyncio.get_event_loop().time() - start_time < initial_wait:
                            logger.info(f"Waiting for stream data, elapsed: {asyncio.get_event_loop().time() - start_time:.2f}s")
                            async for line in response.content.iter_any():
                                line_str = line.decode("utf-8").strip()
                                logger.info(f"Received stream data: '{line_str}'")
                                if not line_str:
                                    logger.debug("Ignored empty line")
                                    continue
                                if line_str == ": keepalive":
                                    logger.info("Received keepalive signal")
                                    continue
                                if line_str.startswith("data: "):
                                    data = line_str[6:]
                                    data_parts = data.split("data: ")
                                    result = None
                                    for i, part in enumerate(data_parts):
                                        if not part:
                                            continue
                                        logger.info(f"Parsed event data part {i+1}: '{part}'")
                                        if part == "[DONE]":
                                            logger.info("Received legacy stream end signal [DONE]")
                                            return
                                        try:
                                            part_result = json.loads(part)
                                            if result is None:
                                                result = part_result
                                            else:
                                                if "result" in part_result:
                                                    result["result"] = {**result.get("result", {}), **part_result.get("result", {})}
                                                if "error" in part_result:
                                                    result["error"] = part_result["error"]
                                            logger.info(f"Parsed stream event part {i+1}: {json.dumps(part_result, indent=2, ensure_ascii=False)}")
                                        except json.JSONDecodeError as e:
                                            logger.error(f"Invalid stream event data: {part}, error: {str(e)}")
                                            yield {"error": {"message": f"Invalid stream event data: {part}, error: {str(e)}"}}
                                            continue
                                    if result:
                                        logger.info(f"Combined stream event: {json.dumps(result, indent=2, ensure_ascii=False)}")
                                        if "result" in result and result["result"].get("type") == "stream_complete":
                                            logger.info("Received stream end signal")
                                            return
                                        yield result
                                else:
                                    logger.debug(f"Ignored non-data line: '{line_str}'")
                            logger.info("Stream iteration paused, waiting 0.5s before retry")
                            await asyncio.sleep(0.5)
                        logger.info(f"Initial wait timeout after {initial_wait}s, no data received")
                    except aiohttp.ClientConnectionError as e:
                        logger.error(f"Stream connection error: {str(e)}")
                        yield {"error": {"message": f"Stream connection error: {str(e)}"}}
                        return
                    except asyncio.TimeoutError:
                        logger.error(f"Stream read timeout after {self.timeout.sock_read} seconds")
                        yield {"error": {"message": f"Stream read timeout after {self.timeout.sock_read} seconds"}}
                        return
                    except Exception as e:
                        logger.error(f"Stream iteration error: {str(e)}")
                        yield {"error": {"message": f"Stream iteration error: {str(e)}"}}
                        return
                    finally:
                        logger.info("Stream content iteration completed")
        except asyncio.TimeoutError:
            error_msg = f"Stream request timed out after {self.timeout.total} seconds"
            logger.error(error_msg)
            yield {"error": {"message": error_msg}}
        except Exception as e:
            error_msg = f"Stream request error: {str(e)}"
            logger.error(error_msg)
            yield {"error": {"message": error_msg}}
        finally:
            logger.info("Stream request processing finished")

    async def start_session(self) -> bool:
        params = {}
        response = await self.send_rpc_request("start_session", params)
        if "result" in response and "session_id" in response["result"]:
            self.session_id = response["result"]["session_id"]
            logger.info(f"Session started: {self.session_id}")
            return True
        logger.error(f"Failed to start session: {response.get('error', 'Unknown error')}")
        return False

    async def process_query(self, query: str) -> Dict:
        if not self.session_id:
            return {"error": "No active session"}
        params = {"session_id": self.session_id, "query": query}
        return await self.send_rpc_request("process_query", params)

    async def process_query_stream(self, query: str) -> AsyncGenerator[Dict, None]:
        if not self.session_id:
            yield {"error": {"message": "No active session. Please use 'start session' to begin."}}
            return
        params = {"session_id": self.session_id, "query": query}
        logger.info(f"Starting stream query processing: {query}")
        async for event in self.send_stream_request("process_query_stream", params):
            logger.info(f"Yielding stream event for query: {query}")
            logger.debug(f"Event details: {json.dumps(event, indent=2, ensure_ascii=False)}")
            yield event
        logger.info(f"Stream query processing completed: {query}")

    async def end_session(self) -> Dict:
        if not self.session_id:
            return {"error": "No active session"}
        params = {"session_id": self.session_id}
        response = await self.send_rpc_request("end_session", params)
        logger.print(f"Ending session: {self.session_id}, response: {response}")
        if "result" in response:
            self.session_id = None
        if "error" in response:
            self.session_id = None
        return response

    def _resolve_bang_command(self, query: str) -> Optional[str]:
        """Resolve !n or !prefix commands to a historical command."""
        if not query.startswith("!"):
            return query
        if not self.command_history:
            logger.print(colored("No command history available.", "red"))
            return None

        bang_cmd = query[1:].strip()
        if bang_cmd.isdigit():
            # !n: Execute the nth command
            index = int(bang_cmd) - 1
            if 0 <= index < len(self.command_history):
                resolved = self.command_history[index]
                logger.print(colored(f"Executing command #{bang_cmd}: {resolved}", "yellow"))
                return resolved
            else:
                logger.print(colored(f"Invalid history index: {bang_cmd}", "red"))
                return None
        else:
            # !prefix: Execute the most recent command starting with prefix
            for cmd in reversed(self.command_history):
                if cmd.startswith(bang_cmd):
                    logger.print(colored(f"Executing command matching '!{bang_cmd}': {cmd}", "yellow"))
                    return cmd
            logger.print(colored(f"No command found matching prefix: {bang_cmd}", "red"))
            return None

    async def chat_loop(self) -> None:
        logger.print(colored("Welcome to Composio MCP Client Simulator", "cyan"))
        logger.print("Commands:")
        logger.print("- 'start session': Start a new session")
        logger.print("- 'end session': End the current session")
        logger.print("- 'stream <query>': Process query with streaming response")
        logger.print("- 'history': Show command history")
        logger.print("- '!n': Execute the nth command from history")
        logger.print("- '!prefix': Execute the most recent command starting with prefix")
        logger.print("- 'help': Show this help message")
        logger.print("- 'exit': Quit the simulator")
        logger.print(f"Using API key: {self.api_key}")

        while True:
            try:
                status = f"Session: {self.session_id if self.session_id else 'None'}"
                self.prompt_session.message = f"> [{status}] "
                query = await self.prompt_session.prompt_async()
                query = query.strip()
                if not query:
                    continue

                logger.info(f"Received user input: {query}")
                # Store command in history
                self.command_history.append(query)
                self.history.append_string(query)

                # Handle bang (!) commands
                resolved_query = self._resolve_bang_command(query)
                if resolved_query is None:
                    continue
                query = resolved_query

                if query.lower() == "exit":
                    if self.session_id:
                        response = await self.end_session()
                        self._print_response(response, "Ending session")
                    logger.print(colored("Goodbye!", "green"))
                    break

                if query.lower() == "start session":
                    if self.session_id:
                        logger.print("A session is already active. End it first with 'end session'.")
                    elif await self.start_session():
                        logger.print(f"Session started: {self.session_id}")
                    continue

                if query.lower() == "end session":
                    if not self.session_id:
                        logger.print("No active session to end.")
                    else:
                        response = await self.end_session()
                        self._print_response(response, "Session ended")
                    continue

                if query.lower() == "history":
                    if not self.command_history:
                        logger.print("No commands in history.")
                    else:
                        logger.print("Command history:")
                        for i, cmd in enumerate(self.command_history, 1):
                            logger.print(f"{i}: {cmd}")
                    continue

                if query.lower() == "help":
                    logger.print("Commands:")
                    logger.print("- 'start session': Start a new session")
                    logger.print("- 'end session': End the current session")
                    logger.print("- 'stream <query>': Process query with streaming response")
                    logger.print("- 'history': Show command history")
                    logger.print("- '!n': Execute the nth command from history")
                    logger.print("- '!prefix': Execute the most recent command starting with prefix")
                    logger.print("- 'help': Show this help message")
                    logger.print("- 'exit': Quit the simulator")
                    continue

                if query.lower().startswith("stream "):
                    if not self.session_id:
                        logger.print("No active session. Use 'start session' to begin.")
                        continue
                    stream_query = query[7:].strip()
                    if not stream_query:
                        logger.print("Stream query cannot be empty.")
                        continue
                    logger.print(colored(f"Streaming query: {stream_query}", "cyan"))
                    async for response in self.process_query_stream(stream_query):
                        self._print_stream_response(response)
                    logger.info("Stream query execution finished")
                    continue

                if not self.session_id:
                    logger.print("No active session. Use 'start session' to begin.")
                    continue

                response = await self.process_query(query)
                self._print_response(response)

            except Exception as e:
                logger.error(f"Chat loop error: {str(e)}")
                logger.print(colored(f"Error: {str(e)}", "red"))

    def _print_response(self, response: Dict, success_msg: str = None) -> None:
        try:
            logger.info("Processing non-stream response")
            logger.debug(f"Response details: {json.dumps(response, indent=2, ensure_ascii=False)}")
            
            if "result" in response:
                result = response["result"]
                if "error" in result:
                    msg = result["error"]
                    if isinstance(msg, str):
                        decoded_msg = msg.encode().decode('unicode_escape')
                    else:
                        decoded_msg = str(msg)
                    logger.print(colored(f"Error: {decoded_msg}", "red"))
                else:
                    msg = success_msg or result.get("response", "Operation successful")
                    if isinstance(msg, str):
                        decoded_msg = msg.encode().decode('unicode_escape')
                    else:
                        decoded_msg = str(msg)
                    logger.print(colored(decoded_msg, "green"))

                if result.get("complete", False):
                    logger.print("Task completed. Start a new query or type 'end session'.")
            else:
                msg = response.get("error", "Unknown error")
                if isinstance(msg, str):
                    decoded_msg = msg.encode().decode('unicode_escape')
                else:
                    decoded_msg = str(msg)
                logger.print(colored(f"RPC Error: {decoded_msg}", "red"))

        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode JSON response: {str(e)}")
            logger.print(colored(f"Error decoding response: {str(e)}", "red"))
        except Exception as e:
            logger.error(f"Error processing response: {str(e)}")
            logger.print(colored(f"Error processing response: {str(e)}", "red"))
        finally:
            logger.info("Response processing completed")

    def _print_stream_response(self, response: Dict) -> None:
        try:
            logger.info(f"Processing stream response")
            logger.debug(f"Response details: {json.dumps(response, indent=2, ensure_ascii=False)}")
            
            # Check if the response is a JSON-RPC error response
            if "jsonrpc" in response and "error" in response:
                error = response["error"]
                error_message = error.get("message", str(error))
                request_id = response.get("id", "unknown")
                logger.error(f"JSON-RPC error (ID: {request_id}): {error_message}")
                logger.print(colored(f"Error (Request ID: {request_id}): {error_message}", "red"))
                # Suggest starting a new session if the error is about an invalid session
                if "Invalid session" in error_message or "No active session" in error_message:
                    logger.print(colored("Please use 'start session' to begin a new session.", "yellow"))
                return

            # Handle streaming events
            if "result" in response:
                result = response["result"]
                event_type = result.get("type", "unknown")
                content = result.get("content")
                # Prepare content for display
                try:
                    if isinstance(content, str):
                        try:
                            parsed_content = json.loads(content)
                            if isinstance(parsed_content, dict) and "results" in parsed_content:
                                for item in parsed_content.get("results", []):
                                    if "result" in item and "content" in item["result"]:
                                        try:
                                            item["result"]["content"] = json.loads(item["result"]["content"])
                                        except json.JSONDecodeError:
                                            pass
                            content_display = json.dumps(parsed_content, indent=2, ensure_ascii=False)
                        except json.JSONDecodeError:
                            # Decode Unicode escape sequences and replace newlines/tabs
                            content_display = content.encode().decode('unicode_escape').replace("\\n", "\n").replace("\\t", "\t")
                    else:
                        content_display = str(content)
                except Exception as e:
                    logger.error(f"Failed to process content: {str(e)}")
                    content_display = str(content) if content else "No content"

                # Handle final response
                if event_type == "final":
                    final_content = result.get("response", content_display)
                    if isinstance(final_content, str):
                        # Decode Unicode escape sequences for final response
                        final_display = final_content.encode().decode('unicode_escape').replace("\\n", "\n").replace("\\t", "\t")
                    else:
                        final_display = json.dumps(final_content, indent=2, ensure_ascii=False)
                    logger.print(colored(f"[Final] {final_display}", "green"))
                elif event_type == "message":
                    logger.print(colored(f"[Message] {content_display}", "blue"))
                elif event_type == "data":
                    logger.print(colored(f"[Data] {content_display}", "cyan"))
                elif event_type == "run_item":
                    logger.print(colored(f"[RunItem] {content_display}", "yellow"))
                elif event_type == "agent_updated":
                    logger.print(colored(f"[Agent] {content_display}", "magenta"))
                elif event_type == "stream_complete":
                    logger.print(colored("[Stream Complete]", "green"))
                if result.get("complete", False):
                    logger.print(colored("Stream completed.", "green"))
            elif "error" in response:
                error_message = response["error"].get("message", str(response["error"]))
                logger.print(colored(f"Stream Error: {error_message}", "red"))
                # Suggest starting a new session for session-related errors
                if "No active session" in error_message:
                    logger.print(colored("Please use 'start session' to begin a new session.", "yellow"))
        except Exception as e:
            logger.error(f"Error processing stream response: {str(e)}")
            logger.print(colored(f"Error processing stream response: {str(e)}, response: {response}", "red"))

    def generate_ascii_art(self, text: str, font: str = "slant", color: str = "green") -> str:
        try:
            ascii_art = pyfiglet.figlet_format(text, font=font)
            return colored(ascii_art, color)
        except pyfiglet.FontNotFound:
            logger.error(f"Font '{font}' not available")
            return f"Error: Font '{font}' not available"

async def main() -> None:
    api_key = os.getenv("MCP_API_KEY")
    simulator = ClientSimulator(api_key=api_key)
    text = "Client Simulator v1.0"
    logger.print(simulator.generate_ascii_art(text))
    await simulator.chat_loop()

if __name__ == "__main__":
    asyncio.run(main())