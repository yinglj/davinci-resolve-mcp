# DaVinci Resolve MCP Server

[![Version](https://img.shields.io/badge/version-1.3.8-blue.svg)](https://github.com/samuelgursky/davinci-resolve-mcp/releases)
[![DaVinci Resolve](https://img.shields.io/badge/DaVinci%20Resolve-18.5+-darkred.svg)](https://www.blackmagicdesign.com/products/davinciresolve)
[![Python](https://img.shields.io/badge/python-3.6+-green.svg)](https://www.python.org/downloads/)
[![macOS](https://img.shields.io/badge/macOS-stable-brightgreen.svg)](https://www.apple.com/macos/)
[![Windows](https://img.shields.io/badge/Windows-stable-brightgreen.svg)](https://www.microsoft.com/windows)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://opensource.org/licenses/MIT)

A Model Context Protocol (MCP) server that connects AI coding assistants (Cursor, Claude Desktop) to DaVinci Resolve, enabling them to query and control DaVinci Resolve through natural language

---

## Supported Startup Modes (Protocols)

**DaVinci Resolve MCP Server** now supports three startup/connection modes (protocols):

| Mode/Protocol     | Description                                                   | Example Usage / Endpoint               | Authentication Support |
| ----------------- | ------------------------------------------------------------- | -------------------------------------- | ---------------------- |
| `stdio`           | Run as a subprocess, communicating via standard input/output. | `python src/main.py` or `./mcp-server` | None                   |
| `sse`             | Run as a network server using Server-Sent Events protocol.    | `http://localhost:8020/sse`            | Bearer/Header/None     |
| `streamable-http` | Run as a network server using HTTP with streaming responses.  | `http://localhost:8020/mcp`            | Bearer/Header/None     |

**How to choose:**

- Use **`stdio`** when integrating as a local subprocess (e.g. for Cursor/Claude or embedded agent/server scenarios).
- Use **`sse`** or **`streamable-http`** when exposing the server over the network for remote or multi-client access.

**Authentication:**

- Only `sse` and `streamable-http` modes support HTTP authentication (Bearer token, custom headers, or no auth).
- When using `stdio`, authentication is not used.

### Example (n8n node or client configuration)

| Protocol        | Endpoint/Command Example    | Authentication |
| --------------- | --------------------------- | -------------- |
| stdio           | `python src/main.py`        | None           |
| sse             | `http://localhost:8020/sse` | Optional       |
| streamable-http | `http://localhost:8020/mcp` | Optional       |

---

## Features

For a comprehensive list of implemented and planned features, see [docs/FEATURES.md](docs/FEATURES.md).

## 🤖 AI Agent Copilot (New!)

The DaVinci Resolve MCP Server now includes an intelligent AI agent that can understand complex natural language requests and automatically execute multi-step workflows. This transforms your AI assistant into a powerful video editing copilot.

### Key AI Agent Capabilities

- **Natural Language Processing**: Just describe what you want in plain English
- **Intelligent Planning**: Breaks down complex tasks into executable steps
- **Video Analysis**: Analyze composition, color, motion, and content using AI vision models
- **Self-Correction**: Automatically detects and fixes errors during execution
- **Learning Memory**: Improves over time based on your feedback

### Example AI Agent Commands

``` text
"Create a new project for my documentary, import all footage from the USB drive, 
create proxies for 4K files, and organize clips by creation date"

"Analyze the color grading in my timeline and suggest improvements for a more 
cinematic look"

"Find all shaky shots in the timeline and apply stabilization"

"Create a rough cut by selecting the best takes based on audio quality and 
removing silent sections"
```

### Using the AI Agent

Simply use the `agent_process_request` tool in your AI assistant:

```python
# In Cursor or Claude, just type:
agent_process_request("Apply a warm sunset color grade to all outdoor shots")

# For video analysis:
agent_analyze_video("current_timeline", "composition")

# Get AI suggestions:
agent_suggest_next_actions()
```

For detailed documentation about the AI Agent, see [docs/AI_AGENT_README.md](docs/AI_AGENT_README.md).

## Requirements

- **macOS** or **Windows** with DaVinci Resolve installed
- **Python 3.6+**
- DaVinci Resolve running in the background
- (Optional) Node.js/npm for some features

## Installation Guide

For detailed installation instructions, please see [INSTALL.md](INSTALL.md). This guide covers:

- Prerequisites and system requirements
- Step-by-step installation process
- Configuration details
- Common troubleshooting steps

## Platform Support

| Platform | Status          | One-Step Install | Quick Start    |
| -------- | --------------- | ---------------- | -------------- |
| macOS    | ✅ Stable        | `./install.sh`   | `./run-now.sh` |
| Windows  | ✅ Stable        | `install.bat`    | `run-now.bat`  |
| Linux    | ❌ Not supported | N/A              | N/A            |

## Quick Start Guide

### New One-Step Installation (Recommended)

The easiest way to get started is with our new unified installation script. This script does everything automatically:

- Clone the repository:
  
   ```bash
   git clone https://github.com/samuelgursky/davinci-resolve-mcp.git
   cd davinci-resolve-mcp
   ```

- Make sure DaVinci Resolve Studio is installed and running

- Run the installation script:
   **macOS/Linux:**

   ```bash
   ./install.sh
   ```

   **Windows:**

   ```batch
   install.bat
   ```

This will:

1. Automatically detect the correct paths on your system
2. Create a Python virtual environment
3. Install the MCP SDK from the official repository
4. Set up environment variables
5. Configure Cursor/Claude integration
6. Verify the installation is correct
7. Optionally start the MCP server

### Alternative Quick Start

You can also use the original quick start scripts:

**Windows Users:**

```bash
run-now.bat
```

**macOS Users:**

```bash
chmod +x run-now.sh
./run-now.sh
```

## Configuration

For configuration of DaVinci Resolve MCP with different AI assistant clients like Cursor or Claude, see the [config-templates](config-templates) directory.

## Troubleshooting

For detailed troubleshooting guidance, refer to the [INSTALL.md](INSTALL.md#troubleshooting) file which contains solutions to common issues.

### Common Issues

#### Path Resolution

- The installation scripts now use more robust path resolution, fixing issues with `run-now.sh` looking for files in the wrong locations
- Always let the scripts determine the correct paths based on their location

#### DaVinci Resolve Detection

- We've improved the process detection to reliably find DaVinci Resolve regardless of how it appears in the process list
- Make sure DaVinci Resolve is running before starting the MCP server

#### Environment Variables

- Make sure all required environment variables are set correctly
- Review the log file at `scripts/cursor_resolve_server.log` for troubleshooting

### Windows

- Make sure to use forward slashes (/) in configuration files
- Python must be installed and paths configured in configs
- DaVinci Resolve must be running before starting the server

### macOS

- Make sure scripts have execute permissions
- Check Console.app for any Python-related errors
- Verify environment variables are set correctly
- DaVinci Resolve must be running before starting the server

## Support

For issues and feature requests, please use the GitHub issue tracker.

## Launch Options

After installation, you have several ways to start the server:

### Client-Specific Launch Scripts

The repository includes dedicated scripts for launching with specific clients:

```bash
# For Cursor integration (macOS)
chmod +x scripts/mcp_resolve-cursor_start
./scripts/mcp_resolve-cursor_start

# For Claude Desktop integration (macOS)
chmod +x scripts/mcp_resolve-claude_start
./scripts/mcp_resolve-claude_start
```

These specialized scripts:

- Set up the proper environment for each client
- Verify DaVinci Resolve is running
- Configure client-specific settings
- Start the MCP server with appropriate parameters

### Pre-Launch Check

Before connecting AI assistants, verify your environment is properly configured:

```bash
# On macOS
./scripts/check-resolve-ready.sh

# On Windows
./scripts/check-resolve-ready.bat
```

These scripts will:

- Verify DaVinci Resolve is running (and offer to start it)
- Check environment variables are properly set
- Ensure the Python environment is configured correctly
- Validate Cursor/Claude configuration
- Optionally launch Cursor

### Universal Launcher

For advanced users, our unified launcher provides full control over both Cursor and Claude Desktop servers:

```bash
# Make the script executable (macOS only)
chmod +x scripts/mcp_resolve_launcher.sh

# Run in interactive mode
./scripts/mcp_resolve_launcher.sh

# Or use command line options
./scripts/mcp_resolve_launcher.sh --start-cursor    # Start Cursor server (uses mcp_resolve-cursor_start)
./scripts/mcp_resolve_launcher.sh --start-claude    # Start Claude Desktop server (uses mcp_resolve-claude_start)
./scripts/mcp_resolve_launcher.sh --start-both      # Start both servers
./scripts/mcp_resolve_launcher.sh --stop-all        # Stop all running servers
./scripts/mcp_resolve_launcher.sh --status          # Show server status
```

Additional options:

- Force mode (skip Resolve running check): `--force`
- Project selection: `--project "Project Name"`

## Full Installation

For a complete manual installation:

1. Clone this repository:

   ```bash
   git clone https://github.com/samuelgursky/davinci-resolve-mcp.git
   cd davinci-resolve-mcp
   ```

2. Create a Python virtual environment:

   ```bash
   # Create virtual environment
   python -m venv venv
   
   # Activate it
   # On macOS/Linux:
   source venv/bin/activate
   # On Windows:
   venv\Scripts\activate
   
   # Install dependencies from requirements.txt
   pip install -r requirements.txt
   
   # Alternatively, install MCP SDK directly
   pip install git+https://github.com/modelcontextprotocol/python-sdk.git
   ```

3. Set up DaVinci Resolve scripting environment variables:

   **For macOS**:

   ```bash
   export RESOLVE_SCRIPT_API="/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting"
   export RESOLVE_SCRIPT_LIB="/Applications/DaVinci Resolve/DaVinci Resolve.app/Contents/Libraries/Fusion/fusionscript.so"
   export PYTHONPATH="$PYTHONPATH:$RESOLVE_SCRIPT_API/Modules/"
   ```

   **For Windows**:

   ```bash
   set RESOLVE_SCRIPT_API=C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting
   set RESOLVE_SCRIPT_LIB=C:\Program Files\Blackmagic Design\DaVinci Resolve\fusionscript.dll
   set PYTHONPATH=%PYTHONPATH%;%RESOLVE_SCRIPT_API%\Modules
   ```

   Alternatively, run the pre-launch check script which will set these for you:

   ```bash
   # On macOS
   ./scripts/check-resolve-ready.sh
   
   # On Windows
   ./scripts/check-resolve-ready.bat
   ```

4. Configure Cursor to use the server by creating a configuration file:

   **For macOS** (`~/.cursor/mcp.json`):

   ```json
   {
     "mcpServers": {
       "davinci-resolve": {
         "name": "DaVinci Resolve MCP",
         "command": "/path/to/your/venv/bin/python",
         "args": [
           "/path/to/your/davinci-resolve-mcp/src/main.py"
         ]
       }
     }
   }
   ```

   **For Windows** (`%APPDATA%\Cursor\mcp.json`):

   ```json
   {
     "mcpServers": {
       "davinci-resolve": {
         "name": "DaVinci Resolve MCP",
         "command": "C:\\path\\to\\venv\\Scripts\\python.exe",
         "args": ["C:\\path\\to\\davinci-resolve-mcp\\src\\main.py"]
       }
     }
   }
   ```

5. Start the server using one of the client-specific scripts:

   ```bash
   # For Cursor
   ./scripts/mcp_resolve-cursor_start
   
   # For Claude Desktop
   ./scripts/mcp_resolve-claude_start
   ```

## Usage with AI Assistants

### Using with Cursor

1. Start the Cursor server using the dedicated script:

   ```bash
   ./scripts/mcp_resolve-cursor_start
   ```

   Or use the universal launcher:

   ```bash
   ./scripts/mcp_resolve_launcher.sh --start-cursor
   ```

2. Start Cursor and open a project.

3. In Cursor's AI chat, you can now interact with DaVinci Resolve. Try commands like:
   - "What version of DaVinci Resolve is running?"
   - "List all projects in DaVinci Resolve"
   - "Create a new timeline called 'My Sequence'"
   - "Add a marker at the current position"

### Using with Claude Desktop

1. Create a `claude_desktop_config.json` file in your Claude Desktop configuration directory using the template in the `config-templates` directory.

2. Run the Claude Desktop server using the dedicated script:

   ```bash
   ./scripts/mcp_resolve-claude_start
   ```

   Or use the universal launcher:

   ```bash
   ./scripts/mcp_resolve_launcher.sh --start-claude
   ```

3. In Claude Desktop, you can now interact with DaVinci Resolve using the same commands as with Cursor.

## Available Features

### General

- Get DaVinci Resolve version
- Get/switch current page (Edit, Color, Fusion, etc.)

### Project Management

- List available projects
- Get current project name
- Open project by name
- Create new project
- Save current project

### Timeline Operations

- List all timelines
- Get current timeline info
- Create new timeline
- Switch to timeline by name
- Add marker to timeline

### Media Pool Operations

- List media pool clips
- Import media file
- Create media bin
- Add clip to timeline

## Windows Support Notes

Windows support is stable in v1.3.3 and should not require additional troubleshooting:

- Ensure DaVinci Resolve is installed in the default location
- Environment variables are properly set as described above
- Windows paths may require adjustment based on your installation
- For issues, please check the logs in the `logs/` directory

### DaVinci Resolve Connection

Make sure DaVinci Resolve is running before starting the server. If the server can't connect to Resolve, check that:

1. Your environment variables are set correctly
2. You have the correct paths for your DaVinci Resolve installation
3. You have restarted your terminal after setting environment variables

## Project Structure

After cleanup, the project has the following structure:

- `resolve_mcp_server.py` - The main MCP server implementation
- `run-now.sh` - Quick start script that handles setup and runs the server
- `setup.sh` - Complete setup script for installation
- `check-resolve-ready.sh` - Pre-launch check to verify DaVinci Resolve is ready
- `start-server.sh` - Script to start the server
- `run-server.sh` - Simplified script to run the server directly

```plaintext
davinci-resolve-mcp/
├── README.md               # This file
├── docs/                   # Documentation
│   ├── FEATURES.md         # Feature list and status
│   ├── CHANGELOG.md        # Version history
│   ├── VERSION.md          # Version information
│   ├── TOOLS_README.md     # Tools documentation
│   ├── PROJECT_MCP_SETUP.md # Project setup guide
│   └── COMMIT_MESSAGE.txt  # Latest commit information
├── config-templates/       # Configuration templates
│   ├── sample_config.json  # Example configuration
│   ├── cursor-mcp-example.json # Cursor config example
│   └── mcp-project-template.json # MCP project template
├── scripts/                # Utility scripts
│   ├── tests/              # Test scripts
│   │   ├── benchmark_server.py # Performance tests
│   │   ├── test_improvements.py # Test scripts
│   │   ├── test_custom_timeline.py # Timeline tests
│   │   ├── create_test_timeline.py # Create test timeline
│   │   ├── test-after-restart.sh # Test after restart (Unix)
│   │   └── test-after-restart.bat # Test after restart (Windows)
│   ├── batch_automation.py # Batch automation script
│   ├── restart-server.sh   # Server restart script (Unix)
│   ├── restart-server.bat  # Server restart script (Windows)
│   ├── run-now.sh          # Quick start script (Unix)
│   └── run-now.bat         # Quick start script (Windows)
├── resolve_mcp_server.py   # Main server implementation
├── src/                    # Source code
│   ├── api/                # API implementation
│   ├── features/           # Feature modules
│   └── utils/              # Utility functions
├── logs/                   # Log files
├── tools/                  # Development tools
├── assets/                 # Project assets
└── examples/               # Example code
```

## License

MIT

## Acknowledgments

- Blackmagic Design for DaVinci Resolve and its API
- The MCP protocol team for enabling AI assistant integration

## Author

Samuel Gursky (<samgursky@gmail.com>)

- GitHub: [github.com/samuelgursky](https://github.com/samuelgursky)

## Future Plans

- Windows and Linux support
- Additional DaVinci Resolve features
- Support for Claude Desktop

## Development

If you'd like to contribute, please check the feature checklist in the repo and pick an unimplemented feature to work on. The code is structured with clear sections for different areas of functionality.

**Key Directories:**

- `src/` - Source code and modules
- `assets/` - Project assets and resources
- `logs/` - Log files directory
- `scripts/` - Helper scripts

When developing, it's recommended to use `./run-now.sh` which sets up the environment and launches the server in one step.

## Changelog

See [docs/CHANGELOG.md](docs/CHANGELOG.md) for a detailed history of changes.

### Cursor-Specific Setup

When integrating with Cursor, follow these specific steps:

1. Make sure DaVinci Resolve is running before starting Cursor

2. Install required dependencies:

   ```bash
   # From the davinci-resolve-mcp directory:
   pip install -r requirements.txt
   ```

   Note: This will install the MCP package and other dependencies automatically.

3. Set up the MCP server configuration in Cursor:

   Create or edit `~/.cursor/mcp.json` on macOS (or `%USERPROFILE%\.cursor\mcp.json` on Windows):

   ```json
   {
     "mcpServers": {
       "davinci-resolve": {
         "name": "DaVinci Resolve MCP",
         "command": "/path/to/your/venv/bin/python",
         "args": [
           "/path/to/your/davinci-resolve-mcp/src/main.py"
         ]
       }
     }
   }
   ```

   **Important Notes:**
   - Use `main.py` as the entry point (not `resolve_mcp_server.py`)
   - Use absolute paths in the configuration

4. Common issues:
   - "Client closed" error: Check that paths are correct in mcp.json and dependencies are installed
   - Connection problems: Make sure DaVinci Resolve is running before starting Cursor
   - Environment variables: The main.py script will handle setting environment variables
