# Project-Specific DaVinci Resolve Integration with Cursor

This guide explains how to set up project-specific DaVinci Resolve integration with Cursor using MCP.

## Overview

Project-specific integration allows Cursor to interact with a specific DaVinci Resolve project automatically. When you open a Cursor project, it can automatically connect to a matching DaVinci Resolve project.

## Setup Steps

### 1. Copy the Template

Create a new file called `mcp.json` in your Cursor project's root directory (not in the `.cursor` folder). Copy the contents from `mcp-project-template.json`:

```json
{
  "mcpServers": {
    "davinci-resolve": {
      "name": "DaVinci Resolve Project-Specific",
      "command": "${PROJECT_ROOT}/mcp_resolve-cursor_start",
      "args": ["--project", "${PROJECT_NAME}"]
    }
  }
}
```

### 2. Copy the Script

Copy the `mcp_resolve-cursor_start` script to your project root:

```bash
cp /path/to/davinci-resolve-mcp-20250326/mcp_resolve-cursor_start /path/to/your/project/
```

Also copy the `run-direct-server.sh` and `direct_resolve_server.py` files:

```bash
cp /path/to/davinci-resolve-mcp-20250326/run-direct-server.sh /path/to/your/project/
cp /path/to/davinci-resolve-mcp-20250326/direct_resolve_server.py /path/to/your/project/
```

Make them executable:

```bash
chmod +x /path/to/your/project/mcp_resolve-cursor_start
chmod +x /path/to/your/project/run-direct-server.sh
chmod +x /path/to/your/project/direct_resolve_server.py
```

### 3. Create a Python Virtual Environment

```bash
cd /path/to/your/project/
python -m venv venv
source venv/bin/activate
pip install jsonrpcserver
```

### 4. Modify Variable Replacement

By default, Cursor will replace:
- `${PROJECT_ROOT}` with the absolute path to your project
- `${PROJECT_NAME}` with the name of your project folder

If your DaVinci Resolve project has a different name than your Cursor project folder, you'll need to manually edit the `mcp.json` file in your project to specify the correct project name:

```json
{
  "mcpServers": {
    "davinci-resolve": {
      "name": "DaVinci Resolve Project-Specific",
      "command": "${PROJECT_ROOT}/mcp_resolve-cursor_start",
      "args": ["--project", "Your DaVinci Resolve Project Name"]
    }
  }
}
```

## Troubleshooting

1. **Make sure DaVinci Resolve is running** before you start Cursor or open your project.

2. **Check the log files** for errors:
   - `cursor_resolve_server.log` - Created by the startup script
   - `resolve_direct_server.log` - Created by the direct server

3. **Verify project exists** - Make sure the project name specified in your `mcp.json` exists in DaVinci Resolve.

4. **Permission issues** - Ensure all scripts are executable and have the right permissions.

5. **Test manually** by running:
   ```bash
   cd /path/to/your/project/
   ./mcp_resolve-cursor_start --project "Your Project Name"
   ```

## Advanced Configuration

If you need additional arguments or setup for your project integration, you can modify:

1. The `mcp.json` file in your project to add more arguments
2. The `mcp_resolve-cursor_start` script to include custom setup steps

## Support

For further assistance, please refer to the main documentation or reach out to the development team. 