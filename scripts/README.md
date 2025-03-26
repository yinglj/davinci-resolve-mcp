# DaVinci Resolve MCP Scripts

This directory contains all the utility and launcher scripts for the DaVinci Resolve MCP server.

## Quick Start Scripts

### run-now.sh / run-now.bat
Quick start scripts for macOS/Linux and Windows that set up the environment and start the server in one step.

```bash
# macOS/Linux
./scripts/run-now.sh

# Windows
scripts\run-now.bat
```

## Pre-Launch Check Scripts

### check-resolve-ready.sh / check-resolve-ready.bat
Scripts that verify your environment is properly configured before launching the server.

```bash
# macOS/Linux
./scripts/check-resolve-ready.sh

# Windows
scripts\check-resolve-ready.bat
```

## Client-Specific Launch Scripts

### mcp_resolve-cursor_start
Dedicated script for launching the server configured for Cursor AI integration.

```bash
./scripts/mcp_resolve-cursor_start
```

### mcp_resolve-claude_start
Dedicated script for launching the server configured for Claude Desktop integration.

```bash
./scripts/mcp_resolve-claude_start
```

## Universal Launcher

### mcp_resolve_launcher.sh
Interactive launcher script that provides a menu for managing different server instances.

```bash
./scripts/mcp_resolve_launcher.sh
```

Command-line options:
- `--start-cursor` - Start the Cursor MCP server
- `--start-claude` - Start the Claude Desktop MCP server
- `--start-both` - Start both servers
- `--stop-all` - Stop all running servers
- `--status` - Show server status
- `--force` - Skip DaVinci Resolve running check
- `--project "Project Name"` - Open a specific project on startup

## Setup and Server Management

### setup.sh
Complete installation script that sets up the environment, virtual environment, and dependencies.

```bash
./scripts/setup.sh
```

### server.sh
Consolidated server management script with commands for starting, stopping, and checking server status.

```bash
./scripts/server.sh start
./scripts/server.sh stop
./scripts/server.sh status
```

## Utility Scripts

### utils.sh
Common utility functions used by other scripts.

## Script Organization

The scripts are organized by function:
- **Quick start scripts** - For getting up and running quickly
- **Environment check scripts** - For verifying proper configuration
- **Client-specific scripts** - For launching with specific AI assistants
- **Management scripts** - For controlling server operation

## Notes for Developers

- Most scripts include environment setup to ensure DaVinci Resolve can be accessed
- The launcher scripts have symbolic links in the root directory for easier access
- Scripts check for DaVinci Resolve before starting to avoid connection issues 