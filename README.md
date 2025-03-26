# DaVinci Resolve MCP Server

A Model Context Protocol (MCP) server that connects AI coding assistants (Cursor, Claude Desktop) to DaVinci Resolve, enabling them to query and control DaVinci Resolve through natural language.

## Features

- **Connect to DaVinci Resolve**: Query information and control DaVinci Resolve from your AI assistant
- **Project Management**: List, open, and create DaVinci Resolve projects
- **Timeline Operations**: Create timelines, switch between them, add markers
- **Media Management**: Import media, create bins, list clips
- **Multi-Client Support**: Works with both Cursor and Claude Desktop

## Requirements

- **macOS** with DaVinci Resolve installed
- **Python 3.6+**
- DaVinci Resolve running in the background

## Quick Start

The easiest way to get started is with our quick setup script:

```bash
# Clone the repository 
git clone https://github.com/samuelgursky/davinci-resolve-mcp.git
cd davinci-resolve-mcp

# Make the script executable
chmod +x scripts/run-now.sh

# Run the quick setup script (this creates a virtual environment)
./scripts/run-now.sh
```

This will:
1. Create a Python virtual environment
2. Install the necessary dependencies
3. Set up environment variables
4. Start the MCP server in development mode

## Pre-Launch Check

To ensure smooth operation, we've included a pre-launch check script that verifies all necessary components are installed and DaVinci Resolve is running before connecting Cursor:

```bash
# Make the script executable
chmod +x scripts/check-resolve-ready.sh

# Run the pre-launch check
./scripts/check-resolve-ready.sh
```

This script will:
1. Check if DaVinci Resolve is running (and offer to start it if not)
2. Verify environment variables are properly set
3. Ensure the Python virtual environment is ready
4. Check and update Cursor MCP configuration as needed
5. Optionally launch Cursor when ready

**Using the pre-launch script is strongly recommended before working with DaVinci Resolve and Cursor together.**

## Full Installation

For a complete installation with AI assistant integration:

1. Clone this repository:
   ```bash
   git clone https://github.com/samuelgursky/davinci-resolve-mcp.git
   cd davinci-resolve-mcp
   ```

2. Run the setup script:
   ```bash
   chmod +x scripts/setup.sh
   ./scripts/setup.sh
   ```

3. Set up DaVinci Resolve scripting environment variables. Add the following to your shell profile (`.zshrc`, `.bash_profile`, etc.):
   ```bash
   export RESOLVE_SCRIPT_API="/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting"
   export RESOLVE_SCRIPT_LIB="/Applications/DaVinci Resolve/DaVinci Resolve.app/Contents/Libraries/Fusion/fusionscript.so"
   export PYTHONPATH="$PYTHONPATH:$RESOLVE_SCRIPT_API/Modules/"
   ```

4. Make sure DaVinci Resolve is running before starting the server.

## Server Management

The project includes a consolidated server management script:

```bash
# Start the server in the background
./scripts/server.sh start

# Check server status
./scripts/server.sh status

# Start in development mode (foreground)
./scripts/server.sh dev

# Stop the server
./scripts/server.sh stop

# Restart the server
./scripts/server.sh restart
```

## Usage with Cursor

1. The setup script will automatically configure Cursor to use the server, or you can manually create a `.cursor/mcp.json` file:
   ```json
   {
     "mcpServers": {
       "davinci-resolve": {
         "name": "DaVinci Resolve MCP",
         "command": "/path/to/venv/bin/python",
         "args": ["/path/to/davinci-resolve-mcp/resolve_mcp_server.py"]
       }
     }
   }
   ```

2. **Important**: Run the pre-launch check script before starting Cursor to ensure all components are ready:
   ```bash
   ./scripts/check-resolve-ready.sh
   ```
   This script will verify DaVinci Resolve is running and all components are properly configured.

3. In Cursor's AI chat, you can now interact with DaVinci Resolve. Try commands like:
   - "What version of DaVinci Resolve is running?"
   - "List all projects in DaVinci Resolve"
   - "Create a new timeline called 'My Sequence'"
   - "Add a marker at the current position"

## Usage with Claude Desktop

1. Create a `claude_desktop_config.json` file in your Claude Desktop configuration directory. The setup script can do this for you, or you can create it manually using the template in the `config-templates` directory.

2. In Claude Desktop, you can now interact with DaVinci Resolve using the same commands as with Cursor.

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

## Troubleshooting

### Python Environment Issues
If you encounter Python installation errors, the setup script creates a virtual environment to avoid system conflicts. If you need to manually set it up:

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Install MCP
pip install mcp
```

### DaVinci Resolve Connection
Make sure DaVinci Resolve is running before starting the server. If the server can't connect to Resolve, check that:

1. Your environment variables are set correctly
2. You have the correct paths for your DaVinci Resolve installation
3. You have restarted your terminal after setting environment variables

## Project Structure

```
davinci-resolve-mcp/
├── README.md                 # Main documentation
├── CHANGELOG.md              # Version history
├── FEATURES.md               # Feature matrix
├── LICENSE                   # License information
├── resolve_mcp_server.py     # Main server implementation
├── config-templates/         # Configuration templates
│   ├── cursor-mcp.template.json
│   └── claude-desktop.template.json
├── scripts/                  # Helper scripts
│   ├── run-now.sh            # Quick start script
│   ├── setup.sh              # Full installation
│   ├── server.sh             # Consolidated server management
│   └── check-resolve-ready.sh # Pre-launch check
├── examples/                 # Example usage scripts
│   ├── markers/              # Marker-related examples
│   ├── timeline/             # Timeline examples
│   └── media/                # Media management examples
└── venv/                     # Python virtual environment (created by setup script)
```

## License

MIT

## Acknowledgments

- Blackmagic Design for DaVinci Resolve and its API
- The MCP protocol team for enabling AI assistant integration

## Author

Samuel Gursky (samgursky@gmail.com)
- GitHub: [github.com/samuelgursky](https://github.com/samuelgursky)

## Future Plans

- Windows and Linux support
- Additional DaVinci Resolve features
- Support for Claude Desktop

## Development

If you'd like to contribute, please check the feature checklist in the repo and pick an unimplemented feature to work on. The code is structured with clear sections for different areas of functionality.

## License

MIT

## Acknowledgments

- Blackmagic Design for DaVinci Resolve and its API
- The MCP protocol team for enabling AI assistant integration

## Project Structure

After cleanup, the project has the following structure:

- `resolve_mcp_server.py` - The main MCP server implementation
- `run-now.sh` - Quick start script that handles setup and runs the server
- `setup.sh` - Complete setup script for installation
- `check-resolve-ready.sh` - Pre-launch check to verify DaVinci Resolve is ready
- `start-server.sh` - Script to start the server
- `run-server.sh` - Simplified script to run the server directly

**Key Directories:**
- `src/` - Source code and modules
- `assets/` - Project assets and resources
- `logs/` - Log files directory
- `scripts/` - Helper scripts

When developing, it's recommended to use `./run-now.sh` which sets up the environment and launches the server in one step. 