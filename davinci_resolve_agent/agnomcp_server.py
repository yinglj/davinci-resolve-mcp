# file: agnomcp_server.py
import asyncio
import json
import socket
import sys
from logger import logger
from typing import Dict, Optional
from aiohttp import web
from configure import load_environment, load_api_keys, load_server_config
from query_processor import QueryProcessor
from errors import JSONRPC_ERROR_CODES
import pyfiglet
from termcolor import colored

logger.debug("Loading agnomcp_server module")

class JSONRPCServer:
    def __init__(self):
        logger.debug("Initializing JSONRPCServer")
        load_environment()
        self.query_processor = None
        self.is_connected = False
        self.api_keys = load_api_keys()
        self.runner = None

    def _validate_api_key(self, request: web.Request) -> tuple[bool, Optional[str]]:
        api_key = request.headers.get("Authorization", "").replace("Bearer ", "")
        if not api_key:
            api_key = request.query.get("api_key", "")
        if api_key in self.api_keys:
            logger.info(f"API key validated for user: {self.api_keys[api_key]}")
            return True, api_key
        logger.warning(f"Invalid or missing API key: {api_key}")
        return False, None

    async def handle_request(self, request: web.Request) -> web.Response:
        is_valid, api_key = self._validate_api_key(request)
        if not is_valid:
            return self._error_response("INVALID_API_KEY")

        try:
            text = await request.text()
            rpc_request = json.loads(text)
            logger.info(f"Received RPC request: {rpc_request.get('method')}, id={rpc_request.get('id')}")
            logger.debug(f"Full request: {json.dumps(rpc_request, indent=2)}")
            logger.print(f"Received RPC request: {json.dumps(rpc_request, indent=2)}")

            jsonrpc_version = rpc_request.get("jsonrpc", "2.0")
            if jsonrpc_version != "2.0":
                return self._error_response("INVALID_REQUEST", jsonrpc_version)

            method = rpc_request.get("method")
            params = rpc_request.get("params", {})
            request_id = rpc_request.get("id")

            if method != "start_session" and not self.is_connected:
                logger.error("Server not connected to any agent")
                return self._error_response("NOT_CONNECTED")

            if method != "start_session" and (not self.query_processor or not self.query_processor.agent):
                logger.error("QueryProcessor or agent not initialized")
                return self._error_response("SERVER_ERROR", "InitializationError", "No agent available")

            if method == "start_session":
                session_id = self.query_processor.start_session()
                response = {"session_id": session_id}
                logger.info(f"Session started: {session_id}")
                logger.print(f"Sending response: {json.dumps(response, indent=2)}")
                return self._success_response(response, request_id)

            elif method == "process_query":
                session_id = params.get("session_id")
                query = params.get("query")
                if not session_id or not query:
                    logger.error(f"Invalid params: session_id={session_id}, query={query}")
                    return self._error_response("INVALID_PARAMS", {"session_id": session_id, "query": query})
                if not self.query_processor.is_session_valid(session_id):
                    logger.error(f"Invalid session: {session_id}")
                    return self._error_response("INVALID_SESSION", session_id)
                logger.info(f"Processing query: {query} for session {session_id}")
                result = await self.query_processor.process_query(session_id, query)
                if "error" in result:
                    logger.error(f"Query processing failed: {result['error']}")
                    return self._error_response("SERVER_ERROR", "QueryProcessingError", result["error"], request_id)
                logger.info(f"Query processed successfully for session {session_id}")
                logger.print(f"Sending response: {json.dumps(result, indent=2)}")
                return self._success_response(result, request_id)

            elif method == "process_query_stream":
                logger.error("Streaming request sent to /rpc; should use /rpc/stream")
                return self._error_response("INVALID_REQUEST", "Use /rpc/stream for streaming", request_id)

            elif method == "end_session":
                session_id = params.get("session_id")
                if not session_id:
                    logger.error("Missing session_id for end_session")
                    return self._error_response("INVALID_PARAMS", {"session_id": session_id})
                if not self.query_processor.is_session_valid(session_id):
                    logger.error(f"Invalid session for end_session: {session_id}")
                    return self._error_response("INVALID_SESSION", session_id)
                result = self.query_processor.end_session(session_id)
                logger.info(f"Session ended: {session_id}")
                logger.print(f"Sending response: {json.dumps(result, indent=2)}")
                return self._success_response(result, request_id)

            else:
                logger.error(f"Unknown method: {method}")
                return self._error_response("METHOD_NOT_FOUND", method)

        except json.JSONDecodeError:
            logger.error(f"JSON parsing error: {text}")
            return self._error_response("PARSE_ERROR", text)
        except Exception as e:
            logger.exception("RPC handling error")
            error_type = type(e).__name__
            error_detail = str(e)
            return self._error_response("SERVER_ERROR", error_type, error_detail)

    async def handle_stream_request(self, request: web.Request) -> web.Response:
        is_valid, api_key = self._validate_api_key(request)
        if not is_valid:
            logger.error("Stream request rejected: invalid API key")
            return self._error_response("INVALID_API_KEY")

        try:
            text = await request.text()
            rpc_request = json.loads(text)
            logger.info(f"Received stream request: {rpc_request.get('method')}, id={rpc_request.get('id')}")
            logger.debug(f"Full stream request: {json.dumps(rpc_request, indent=2)}")

            jsonrpc_version = rpc_request.get("jsonrpc", "2.0")
            if jsonrpc_version != "2.0":
                logger.error(f"Invalid JSON-RPC version: {jsonrpc_version}")
                return self._error_response("INVALID_REQUEST", jsonrpc_version)

            method = rpc_request.get("method")
            params = rpc_request.get("params", {})
            request_id = rpc_request.get("id")

            if not self.is_connected:
                logger.error("Stream request rejected: server not connected")
                return self._error_response("NOT_CONNECTED")

            if not self.query_processor or not self.query_processor.agent:
                logger.error("Stream request rejected: QueryProcessor or agent not initialized")
                return self._error_response("SERVER_ERROR", "InitializationError", "No agent available")

            if method == "process_query_stream":
                session_id = params.get("session_id")
                query = params.get("query")
                if not session_id or not query:
                    logger.error(f"Invalid stream params: session_id={session_id}, query={query}")
                    return self._error_response("INVALID_PARAMS", {"session_id": session_id, "query": query})
                if not self.query_processor.is_session_valid(session_id):
                    logger.error(f"Invalid session for stream: {session_id}")
                    return self._error_response("INVALID_SESSION", session_id)

                response = web.StreamResponse(
                    status=200,
                    reason="OK",
                    headers={
                        "Content-Type": "text/event-stream",
                        "Cache-Control": "no-cache",
                        "Connection": "keep-alive",
                        "X-Accel-Buffering": "no"
                    }
                )
                await response.prepare(request)
                logger.info(f"Stream response prepared for session {session_id}, request_id={request_id}")

                last_event = asyncio.get_running_loop().time()
                stream_active = True
                keepalive_interval = 5

                async def send_sse_event(data: str, is_keepalive: bool = False) -> bool:
                    nonlocal stream_active
                    if not stream_active:
                        logger.info(f"Skipping send for session {session_id}: stream inactive")
                        return False
                    try:
                        if is_keepalive:
                            event_data = b": keepalive\n\n"
                            logger.info(f"Sending keepalive for session {session_id}, request_id={request_id}")
                        else:
                            event_data = f"data: {data}\n\n".encode("utf-8")
                            logger.info(f"Sending stream event for session {session_id}, request_id={request_id}: {data[:100]}...")
                        await response.write(event_data)
                        transport = response._req.transport
                        if transport and transport.get_extra_info('socket'):
                            transport.get_extra_info('socket').setsockopt(
                                socket.IPPROTO_TCP, socket.TCP_NODELAY, 1
                            )
                        await asyncio.sleep(0)
                        logger.debug(f"Event sent successfully for session {session_id}, request_id={request_id}")
                        return True
                    except (ConnectionResetError, BrokenPipeError) as e:
                        logger.warning(f"Client disconnected for session {session_id}: {e}")
                        stream_active = False
                        return False
                    except RuntimeError as e:
                        if "Cannot call write() after write_eof()" in str(e):
                            logger.warning(f"Stream closed for session {session_id}: {e}")
                            stream_active = False
                            return False
                        logger.error(f"Failed to send event: {e}")
                        raise
                    except Exception as e:
                        logger.error(f"Unexpected error sending event: {e}")
                        stream_active = False
                        return False

                try:
                    logger.info(f"Starting stream query processing for session {session_id}, query: {query}")
                    if not await send_sse_event("", is_keepalive=True):
                        logger.info(f"Stream stopped after initial keepalive for session {session_id}")
                        stream_active = False

                    async for event in self.query_processor.process_query_stream(session_id, query, request_id=request_id):
                        if not stream_active:
                            logger.info(f"Stream stopped for session {session_id}, discarding event")
                            break
                        logger.debug(f"Generated stream event for session {session_id}, request_id={request_id}: {json.dumps(event, indent=2)}")
                        if not isinstance(event, dict) or "jsonrpc" not in event:
                            logger.error(f"Invalid event format: {event}")
                            error_event = {
                                "jsonrpc": "2.0",
                                "error": {
                                    "code": JSONRPC_ERROR_CODES["SERVER_ERROR"]["code"],
                                    "message": "Invalid event format"
                                },
                                "id": request_id
                            }
                            await send_sse_event(json.dumps(error_event))
                            continue
                        event_data = json.dumps(event, ensure_ascii=False)
                        if not await send_sse_event(event_data):
                            logger.info(f"Stream stopped after sending event for session {session_id}")
                            stream_active = False
                            break
                        last_event = asyncio.get_running_loop().time()
                        if stream_active and asyncio.get_running_loop().time() - last_event >= keepalive_interval:
                            if not await send_sse_event("", is_keepalive=True):
                                logger.info(f"Stream stopped after keepalive for session {session_id}")
                                stream_active = False
                                break
                            last_event = asyncio.get_running_loop().time()

                    if stream_active:
                        logger.info(f"Sending stream end signal for session {session_id}, request_id={request_id}")
                        end_event = {
                            "jsonrpc": "2.0",
                            "result": {
                                "type": "stream_complete",
                                "complete": True
                            },
                            "id": request_id
                        }
                        if not await send_sse_event(json.dumps(end_event)):
                            logger.info(f"Stream stopped after sending end signal for session {session_id}")
                        else:
                            logger.info(f"Stream end signal sent for session {session_id}, request_id={request_id}")

                except asyncio.CancelledError:
                    logger.warning(f"Stream processing cancelled for session {session_id}")
                    stream_active = False
                    try:
                        await response.write_eof()
                    except Exception as e:
                        logger.warning(f"Failed to close stream on cancellation: {e}")
                except Exception as e:
                    logger.error(f"Stream processing error for session {session_id}, request_id={request_id}: {str(e)}")
                    if stream_active:
                        error_event = {
                            "jsonrpc": "2.0",
                            "error": {
                                "code": JSONRPC_ERROR_CODES["SERVER_ERROR"]["code"],
                                "message": f"Stream error: {str(e)}"
                            },
                            "id": request_id
                        }
                        await send_sse_event(json.dumps(error_event))
                        stream_active = False
                finally:
                    if stream_active:
                        try:
                            logger.info(f"Closing stream for session {session_id}, request_id={request_id}")
                            await response.write_eof()
                            logger.info(f"Stream closed normally for session {session_id}, request_id={request_id}")
                        except (RuntimeError, ConnectionResetError, BrokenPipeError) as e:
                            logger.warning(f"Failed to close stream: {e}")
                    logger.info(f"Stream query processing completed for session {session_id}, request_id={request_id}")
                return response

            else:
                logger.error(f"Unknown stream method: {method}")
                return self._error_response("METHOD_NOT_FOUND", method, request_id)

        except json.JSONDecodeError:
            logger.error(f"Stream JSON parsing error: {text}")
            return self._error_response("PARSE_ERROR", text)
        except Exception as e:
            logger.exception("Stream RPC handling error")
            error_type = type(e).__name__
            error_detail = str(e)
            return self._error_response("SERVER_ERROR", error_type, error_detail, request_id)

    def _success_response(self, result: Dict, request_id: Optional[int]) -> web.Response:
        response = {
            "jsonrpc": "2.0",
            "result": result,
            "id": request_id
        }
        return web.json_response(response)

    def _error_response(self, error_key: str, *message_details: str, request_id: Optional[int] = None) -> web.Response:
        error_info = JSONRPC_ERROR_CODES[error_key]
        message = error_info["message"]
        if message_details:
            try:
                message = message.format(*message_details)
            except IndexError:
                logger.error(f"Message formatting error for {error_key}")
                message = error_info["message"]
        response = {
            "jsonrpc": "2.0",
            "error": {
                "code": error_info["code"],
                "message": message
            },
            "id": request_id
        }
        return web.json_response(response)

    async def handle_options(self, request: web.Request) -> web.Response:
        response = web.Response(status=204)
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, api_key'
        return response

    async def start(self) -> None:
        try:
            logger.info("start JSON-RPC server")
            if 'ipykernel' in sys.modules:
                logger.warning("Detected Jupyter environment, may cause event loop conflicts, consider running in standard Python environment")

            # Load server configurations
            server_configs = load_server_config()
            if not server_configs:
                logger.warning("No valid server configurations found, continuing startup")
            else:
                logger.info(f"Loaded server configurations: {[s['name'] for s in server_configs]}")

            # Modify this part of the initialization code
            self.query_processor = QueryProcessor()
            try:
                await self.query_processor.initialize()  # Correctly await asynchronous initialization
                logger.info("QueryProcessor initialization complete")

                if self.query_processor.agent:
                    logger.info(f"Agent initialization complete: {self.query_processor.agent.name}")
                    self.is_connected = True
                else:
                    logger.warning("No valid agent found")
            except Exception as e:
                logger.error(f"QueryProcessor initialization failed: {str(e)}")
                raise RuntimeError(f"QueryProcessor initialization failed: {str(e)}")

            if not self.api_keys:
                logger.warning("No API keys found. All requests will be rejected.")

            # Check port availability
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                try:
                    s.bind(('localhost', 8080))
                except OSError as e:
                    logger.error(f"Port 8080 is already in use: {e}")
                    raise RuntimeError(f"Port 8080 is already in use: {e}")

            # Setup aiohttp application
            app = web.Application()
            app.router.add_post("/rpc", self.handle_request)
            app.router.add_post("/rpc/stream", self.handle_stream_request)
            app.router.add_options("/rpc", self.handle_options)
            app.router.add_options("/rpc/stream", self.handle_options)
            logger.info("Aiohttp application setup complete")
            runner = web.AppRunner(app)
            self.runner = runner
            await runner.setup()
            logger.info("Runner server setup complete")
            site = web.TCPSite(runner, 'localhost', 8080)
            try:
                await site.start()
                logger.print("JSON-RPC server started on http://localhost:8080/rpc")
                logger.info("Streaming endpoint available at http://localhost:8080/rpc/stream")
            except Exception as e:
                logger.error(f"Failed to start TCPSite: {e}")
                raise

            await asyncio.Event().wait()

        except asyncio.CancelledError:
            logger.warning("Server startup cancelled")
            raise
        except Exception as e:
            logger.error(f"Server startup failed: {str(e)}")
            await self.cleanup()
            raise RuntimeError(f"Server startup failed: {str(e)}")

    async def cleanup(self) -> None:
        logger.info("Starting cleanup of JSONRPCServer")
        if self.runner:
            try:
                await self.runner.cleanup()
                logger.info("Aiohttp server cleanup complete")
            except Exception as e:
                logger.error(f"Failed to cleanup Aiohttp server: {str(e)}")
            self.runner = None
        if self.query_processor:
            try:
                await self.query_processor.cleanup()
                logger.info("QueryProcessor cleanup complete")
            except Exception as e:
                logger.error(f"Failed to cleanup QueryProcessor: {str(e)}")
            self.query_processor = None
        self.is_connected = False
        logger.info("JSONRPCServer cleanup complete")

def generate_ascii_art(text: str, font: str = "slant", color: str = "green") -> str:
    try:
        ascii_art = pyfiglet.figlet_format(text, font=font)
        return colored(ascii_art, color)
    except pyfiglet.FontNotFound:
        logger.error(f"Font '{font}' not available")
        return f"Error: Font '{font}' not available"
    except Exception as e:
        logger.error(f"Error generating ASCII art: {e}")
        return f"Error generating ASCII art: {e}"

async def main() -> None:
    server = JSONRPCServer()
    try:
        await server.start()
    except asyncio.CancelledError:
        logger.warning("Main task cancelled")
        await server.cleanup()
    except Exception as e:
        logger.error(f"Server startup failed: {str(e)}")
        await server.cleanup()
        raise

if __name__ == "__main__":
    text = "JSON-RPC Server"
    ascii_art = generate_ascii_art(text)
    print(ascii_art)
    logger.print("Starting JSON-RPC server...")
    asyncio.run(main())