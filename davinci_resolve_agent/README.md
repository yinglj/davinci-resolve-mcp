# DaVinci Resolve MCP Server

## Overview

The DaVinci Resolve MCP (Multi-Channel Processing) Server is a JSON-RPC-based server designed to facilitate interaction with a DaVinci Resolve agent. It provides a robust framework for processing queries, managing sessions, and handling streaming responses, with support for knowledge base integration and custom logging. The server is built using Python with the `aiohttp` library for asynchronous HTTP handling and integrates with various AI models and tools for enhanced query processing.

## Features

- **JSON-RPC Server**: Handles JSON-RPC 2.0 requests for session management, query processing, and streaming responses.
- **Session Management**: Supports starting, validating, and ending sessions with unique session IDs.
- **Streaming Support**: Provides Server-Sent Events (SSE) for real-time query processing with keepalive mechanisms.
- **Knowledge Base Integration**: Utilizes a vector database (`LanceDb`) with support for PDF and text-based knowledge files.
- **Custom Logging**: Implements a custom logger with daily rotation, gzip compression, and enhanced debugging capabilities.
- **API Key Authentication**: Validates requests using API keys loaded from a configuration file.
- **Client Simulator**: Includes a command-line client simulator with command history and Linux-style `!` command matching.
- **Multi-Agent Support**: Integrates with multiple AI models (e.g., OpenAI, Ollama) via the `MultiMCPTools` framework.

## Requirements

- Python 3.8+
- Dependencies listed in `requirements.txt` (e.g., `aiohttp`, `pyfiglet`, `termcolor`, `prompt_toolkit`, etc.)
- A configuration file (`mcp_config.json`) for server settings, API keys, and knowledge files.
- Optional: Knowledge files (PDF, Markdown, or text) for the knowledge base.

## Installation

1. **Clone the Repository**:

   ```bash
   git clone https://github.com/yinglj/davinci-resolve-mcp.git
   cd davinci-resolve-mcp
   ```

2. **Set Up a Virtual Environment**:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

4. **Create Configuration File**:
   Create a `mcp_config.json` file in the project root with the following structure:

   ```json
   {
       "mcpServers": {
           "Davinci_resolve": {
               "name": "Davinci_resolve",
               "command": "sse",
               "args": ["http://localhost:8080"],
               "timeout": 10,
               "knowledgeFiles": ["path/to/knowledge.pdf"],
               "embedder": {
                   "type": "ollama",
                   "model": "hf.co/jinaai/jina-embeddings-v4-text-retrieval-GGUF:Q4_K_M",
                   "dimensions": 2048
               }
           }
       },
       "apiKeys": {
           "sk-1234567890abcdef": "user1"
       },
       "timeout": 10.0,
       "llm_preference": "ollama"
   }
   ```

5. **Set Environment Variables** (optional):

   ```bash
   export MCP_API_KEY=sk-1234567890abcdef
   export MCP_LOG_LEVEL=DEBUG
   ```

## Usage

### Running the Server

Start the JSON-RPC server:

```bash
python agnomcp_server.py
```

The server will run on `http://localhost:8080/rpc` for standard RPC requests and `http://localhost:8080/rpc/stream` for streaming requests.

### Using the Client Simulator

Run the client simulator to interact with the server:

```bash
python client_simulator.py
```

**Available Commands**:

- `start session`: Start a new session.
- `end session`: End the current session.
- `stream <query>`: Process a query with streaming response.
- `history`: Show command history.
- `!n`: Execute the nth command from history.
- `!prefix`: Execute the most recent command starting with the prefix.
- `help`: Show the help message.
- `exit`: Quit the simulator.

Example:

```bash
> [Session: None] start session
Session started: 550e8400-e29b-41d4-a716-446655440000
> [Session: 550e8400-e29b-41d4-a716-446655440000] stream What is DaVinci Resolve?
[Stream Complete]
> [Session: 550e8400-e29b-41d4-a716-446655440000] end session
Session ended
> [Session: None] exit
Goodbye!
```

### Configuration

- **mcp_config.json**: Defines server configurations, API keys, knowledge files, and embedder settings.
- **Logging**: Configured via `MCP_LOG_LEVEL` environment variable or `mcp_config.ini`. Logs are stored in the `logs/` directory with daily rotation and gzip compression.
- **Knowledge Base**: Supports PDF, Markdown, and text files, loaded via `knowledgeFiles` in the configuration.

## File Structure

- `agnomcp_server.py`: Main server implementation with JSON-RPC handling.
- `client_simulator.py`: Command-line client for testing server interactions.
- `configure.py`: Configuration loading for servers, API keys, and knowledge bases.
- `errors.py`: Defines JSON-RPC error codes and messages.
- `logger.py`: Custom logging with daily rotation and console output.
- `mcp_agents.py`: Agent creation and management for query processing.
- `query_processor.py`: Handles query processing, session management, and knowledge base integration.

## Error Handling

The server uses a standardized JSON-RPC error format, defined in `errors.py`. Common errors include:

- `INVALID_API_KEY`: Invalid or missing API key.
- `INVALID_SESSION`: Session ID is invalid or does not exist.
- `NOT_CONNECTED`: Server is not connected to an agent.
- `SERVER_ERROR`: General server errors with detailed messages.

## Logging

Logs are stored in the `logs/` directory with filenames based on the main script name (e.g., `agnomcp_server.log`). Logs rotate daily and are compressed using gzip. The log level can be set via the `MCP_LOG_LEVEL` environment variable (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`).

## Contributing

Contributions are welcome! Please submit pull requests or open issues on the repository for bug reports or feature requests.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.