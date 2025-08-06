# DaVinci Resolve MCP Server

## Overview

The DaVinci Resolve MCP (Multi-Channel Processing) Server is a JSON-RPC-based server designed to facilitate interaction with a DaVinci Resolve agent. It provides a robust framework for processing queries, managing sessions, and handling streaming responses, with support for knowledge base integration and custom logging. The server is built using Python with the `aiohttp` library for asynchronous HTTP handling and integrates with various AI models and tools for enhanced query processing.

This server acts as the bridge between AI assistants (like Cursor, Claude Desktop) and DaVinci Resolve, enabling natural language control of video editing operations. It supports multiple communication protocols including stdio, SSE (Server-Sent Events), and streamable HTTP.

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

- Python 3.10+
- DaVinci Resolve 18.5+ installed and running
- Dependencies listed in `pyproject.toml`, including:
  - `agno>=1.7.0`: Core agent framework
  - `aiohttp>=3.11.16`: Asynchronous HTTP server
  - `mcp>=1.10.0`: Model Context Protocol implementation
  - `ollama>=0.5.1`: Integration with Ollama models
  - `openai-agents>=0.0.19`: Integration with OpenAI models
  - Additional utilities: `pyfiglet`, `termcolor`, etc.
- A configuration file (`mcp_config.json`) for server settings, API keys, and knowledge files
- Optional: Knowledge files (PDF, Markdown, CSV, or text) for the knowledge base

## Installation

1. **Clone the Repository**:

   ```bash
   git clone https://github.com/yinglj/davinci-resolve-mcp.git
   cd davinci-resolve-mcp
   ```

2. **Set Up a Virtual Environment**:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On macOS/Linux
   # or
   venv\Scripts\activate  # On Windows
   ```

3. **Install Dependencies**:

   ```bash
   # Using pip
   pip install -e .
   # Or using a modern Python package manager
   pip install uv
   uv pip install -e .
   ```

4. **Create Configuration File**:
   Create a `mcp_config.json` file in the `davinci_resolve_agent` directory with the following structure:

   ```json
   {
       "mcpServers": {
           "Davinci_resolve": {
               "name": "Davinci_resolve",
               "command": "sse",
               "args": ["http://localhost:8080"],
               "timeout": 10,
               "knowledgeFiles": [
                   {
                       "path": "path/to/knowledge.pdf",
                       "metadata": {"source": "DaVinci Resolve Documentation"}
                   }
               ],
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
   # On macOS/Linux
   export MCP_API_KEY=sk-1234567890abcdef
   export MCP_LOG_LEVEL=DEBUG
   
   # On Windows (PowerShell)
   $env:MCP_API_KEY="sk-1234567890abcdef"
   $env:MCP_LOG_LEVEL="DEBUG"
   ```

6. **Verify DaVinci Resolve is Running**:
   
   Before starting the server, ensure DaVinci Resolve is running. You can use the provided script:
   
   ```bash
   # On macOS/Linux
   ./scripts/check-resolve-ready.sh
   
   # On Windows
   scripts\check-resolve-ready.bat
   ```

## Usage

### Running the Server

Start the JSON-RPC server:

```bash
python agnomcp_server.py
```

The server will run on `http://localhost:8080/rpc` for standard RPC requests and `http://localhost:8080/rpc/stream` for streaming requests.

### Server Startup Modes

The DaVinci Resolve MCP Server supports three startup/connection modes (protocols):

| Mode/Protocol     | Description                                                   | Example Usage / Endpoint               | Authentication Support |
| ----------------- | ------------------------------------------------------------- | -------------------------------------- | ---------------------- |
| `stdio`           | Run as a subprocess, communicating via standard input/output. | `python src/main.py` or `./mcp-server` | None                   |
| `sse`             | Run as a network server using Server-Sent Events protocol.    | `http://localhost:8080/sse`            | Bearer/Header/None     |
| `streamable-http` | Run as a network server using HTTP with streaming responses.  | `http://localhost:8080/mcp`            | Bearer/Header/None     |

**How to choose:**

- Use **`stdio`** when integrating as a local subprocess (e.g. for Cursor/Claude or embedded agent/server scenarios).
- Use **`sse`** or **`streamable-http`** when exposing the server over the network for remote or multi-client access.

### Integration with DaVinci Resolve

The server connects to DaVinci Resolve using the official DaVinci Resolve Scripting API. Make sure DaVinci Resolve is running before starting the server. The server can control various aspects of DaVinci Resolve, including:

- Project management
- Timeline operations
- Media pool operations
- Color grading
- Delivery settings

For examples of how to interact with DaVinci Resolve through the MCP server, see the `examples/` directory in the project root.

### Using the Client Simulator

The package includes a command-line client simulator for testing and interacting with the server. This is useful for debugging and exploring the capabilities of the MCP server without needing to integrate with an external application.

Run the client simulator:

```bash
python client_simulator.py
```

**Available Commands**:

- `start session`: Start a new session with the server.
- `end session`: End the current session.
- `stream <query>`: Process a query with streaming response (real-time updates).
- `query <query>`: Process a query with a standard (non-streaming) response.
- `history`: Show command history for the current session.
- `!n`: Execute the nth command from history (e.g., `!3` executes the third command).
- `!prefix`: Execute the most recent command starting with the prefix (e.g., `!str` might execute `stream What is DaVinci Resolve?`).
- `help`: Show the help message with available commands.
- `exit`: Quit the simulator.

**Example Session**:

```bash
> [Session: None] start session
Session started: 550e8400-e29b-41d4-a716-446655440000
> [Session: 550e8400-e29b-41d4-a716-446655440000] stream What is DaVinci Resolve?
[Streaming response about DaVinci Resolve...]
[Stream Complete]
> [Session: 550e8400-e29b-41d4-a716-446655440000] stream How do I create a new project?
[Streaming response about creating a new project...]
[Stream Complete]
> [Session: 550e8400-e29b-41d4-a716-446655440000] end session
Session ended
> [Session: None] exit
Goodbye!
```

### Example Queries

Here are some example queries you can try with the client simulator:

- "What is DaVinci Resolve?"
- "How do I create a new project in DaVinci Resolve?"
- "How can I add markers to my timeline?"
- "What are the keyboard shortcuts for editing in DaVinci Resolve?"
- "How do I export my project in 4K resolution?"

The quality and accuracy of responses will depend on the knowledge files you've configured and the LLM model being used.

### Configuration

- **mcp_config.json**: Defines server configurations, API keys, knowledge files, and embedder settings.
- **Logging**: Configured via `MCP_LOG_LEVEL` environment variable or `mcp_config.ini`. Logs are stored in the `logs/` directory with daily rotation and gzip compression.
- **Knowledge Base**: Supports PDF, Markdown, CSV, and text files, loaded via `knowledgeFiles` in the configuration.

Edit the `mcp_config.json` file to configure the server. The configuration file supports the following sections:

#### Server Configuration

```json
{
  "server": {
    "host": "localhost",
    "port": 8080,
    "api_key": "your-api-key",
    "mode": "streamable-http"  // Options: "stdio", "sse", "streamable-http"
  },
  // Other configuration sections...
}
```

#### LLM Configuration

```json
{
  // Server configuration...
  "llm": {
    "provider": "openai",  // Options: "openai", "anthropic", "ollama", etc.
    "model": "gpt-4",     // Model name depends on the provider
    "api_key": "your-openai-api-key",
    "api_base": "https://api.openai.com/v1"  // Optional: custom API endpoint
  },
  // Other configuration sections...
}
```

#### Embedder Configuration

```json
{
  // Server and LLM configuration...
  "embedder": {
    "provider": "openai",  // Options: "openai", "ollama"
    "model": "text-embedding-ada-002",  // For OpenAI
    // Or "model": "llama2"  // For Ollama
    "api_key": "your-openai-api-key",
    "api_base": "https://api.openai.com/v1"  // Optional: custom API endpoint
  },
  // Knowledge files configuration...
}
```

#### Knowledge Files Configuration

The server supports multiple knowledge file types to enhance the AI's responses with domain-specific information:

```json
{
  // Server, LLM, and Embedder configuration...
  "knowledgeFiles": [
    {
      "type": "pdf",
      "path": "path/to/your/knowledge.pdf"
    },
    {
      "type": "markdown",
      "path": "path/to/your/knowledge.md"
    },
    {
      "type": "csv",
      "path": "path/to/your/data.csv"
    },
    {
      "type": "text",
      "path": "path/to/your/document.txt"
    }
  ]
}
```

#### Complete Configuration Example

```json
{
  "server": {
    "host": "localhost",
    "port": 8080,
    "api_key": "your-api-key",
    "mode": "streamable-http"
  },
  "llm": {
    "provider": "openai",
    "model": "gpt-4",
    "api_key": "your-openai-api-key"
  },
  "embedder": {
    "provider": "openai",
    "model": "text-embedding-ada-002",
    "api_key": "your-openai-api-key"
  },
  "knowledgeFiles": [
    {
      "type": "pdf",
      "path": "path/to/davinci-resolve-manual.pdf"
    },
    {
      "type": "markdown",
      "path": "path/to/davinci-resolve-tips.md"
    },
    {
      "type": "csv",
      "path": "path/to/keyboard-shortcuts.csv"
    }
  ]
}
```

## File Structure

```
.
├── agnomcp_server.py       # Main server implementation with JSON-RPC handling
├── client_simulator.py     # Client simulator for testing and demonstration
├── configure.py            # Configuration utilities for loading and validating settings
├── errors.py               # Error handling and custom exception definitions
├── logger.py               # Logging utilities with configurable levels and rotation
├── mcp_agents.py           # MCP agent implementation with multi-agent support
├── mcp_config.json         # Configuration file for server, LLM, embedder, and knowledge files
├── pyproject.toml          # Project metadata and dependencies
└── query_processor.py      # Query processing logic with vector database integration
```

### Key Components

- **agnomcp_server.py**: Implements the JSON-RPC server with endpoints for session management and query processing. Handles authentication, request validation, and response formatting.

- **mcp_agents.py**: Creates and manages the Multi-MCP Agent that interfaces with DaVinci Resolve. Supports different server modes (stdio, sse, streamable-http) and integrates with various LLM providers.

- **query_processor.py**: Processes user queries by leveraging the vector database for semantic search and retrieval from knowledge files. Manages the conversation context and formats responses.

- **configure.py**: Handles configuration loading, validation, and environment variable integration. Ensures all required settings are properly set before server startup.

- **client_simulator.py**: Provides an interactive command-line interface for testing the server without needing an external client application.

## Error Handling

The server implements standard JSON-RPC error codes and custom error handling to ensure robust operation and clear error messages.

### Standard JSON-RPC Error Codes

- `-32700`: Parse error - Invalid JSON was received.
- `-32600`: Invalid Request - The JSON sent is not a valid Request object.
- `-32601`: Method not found - The method does not exist / is not available.
- `-32602`: Invalid params - Invalid method parameter(s).
- `-32603`: Internal error - Internal JSON-RPC error.
- `-32000` to `-32099`: Server error - Reserved for implementation-defined server errors.

### Custom Error Handling

The server also implements custom error handling for specific scenarios:

- **Authentication Errors**: When API keys are invalid or missing.
- **Session Errors**: When session operations fail (e.g., trying to end a non-existent session).
- **Query Processing Errors**: When the LLM or knowledge base encounters issues.
- **DaVinci Resolve Connection Errors**: When the server cannot connect to DaVinci Resolve.

All errors are logged with appropriate severity levels and returned to the client with descriptive messages to aid in troubleshooting.

### Error Response Format

Error responses follow the JSON-RPC 2.0 specification:

```json
{
  "jsonrpc": "2.0",
  "error": {
    "code": -32000,
    "message": "Error message",
    "data": { "additional": "error details" }
  },
  "id": "request-id"
}
```

## Logging

The server uses a comprehensive logging system to track operations, errors, and performance metrics.

### Log Configuration

Logging can be configured in several ways:

1. **Environment Variable**: Set `MCP_LOG_LEVEL` to one of `DEBUG`, `INFO`, `WARNING`, `ERROR`, or `CRITICAL`.
2. **Configuration File**: Add logging settings to `mcp_config.ini`.

### Log Storage

- Logs are stored in the `logs/` directory.
- Log files use a daily rotation scheme with the format `mcp-server-YYYY-MM-DD.log`.
- Older log files are automatically compressed using gzip to save space.

### Log Format

Log entries include:

- Timestamp with millisecond precision
- Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Module/component name
- Process ID and thread ID (useful for debugging concurrency issues)
- Detailed message

Example log entry:

```
2023-06-15 14:32:45,123 - INFO - agnomcp_server - [PID:1234 TID:5678] - Server started on http://localhost:8080
```

### Performance Logging

In DEBUG mode, the server logs performance metrics such as:

- Query processing time
- LLM response time
- Vector database search time

These metrics can help identify bottlenecks and optimize server performance.

## Contributing

Contributions to the DaVinci Resolve MCP Server are welcome! Here's how you can contribute:

### Development Setup

1. Fork the repository and clone your fork
2. Create a virtual environment: `python -m venv venv`
3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - macOS/Linux: `source venv/bin/activate`
4. Install development dependencies: `pip install -e ".[dev]"`

### Contribution Guidelines

1. **Code Style**: Follow PEP 8 guidelines for Python code.
2. **Documentation**: Update documentation for any changes you make.
3. **Testing**: Add tests for new features and ensure existing tests pass.
4. **Commit Messages**: Write clear, concise commit messages describing your changes.
5. **Pull Requests**: Submit PRs against the `main` branch with a clear description of changes.

### Feature Requests and Bug Reports

If you find a bug or have a feature request, please open an issue on the GitHub repository with a clear description and, if possible, steps to reproduce.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

```
MIT License

Copyright (c) 2023 DaVinci Resolve MCP Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```