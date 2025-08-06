# DaVinci Resolve MCP Server Tools

This directory contains utilities for working with the DaVinci Resolve MCP Server:

- **benchmark_server.py**: Performance testing tool
- **batch_automation.py**: Workflow automation script
- **sample_config.json**: Example configuration file
- **resolve_mcp_server.py**: Core MCP server implementation with DaVinci Resolve integration

## Benchmark Server

The benchmarking tool measures MCP server performance and reliability, helping identify bottlenecks and verify improvements.

### Features

- Measures response time for various operations
- Tracks success rates across multiple iterations
- Provides statistical analysis (min/max/avg/median/std dev)
- Monitors resource usage (memory, CPU, threads)
- Generates detailed logs and JSON reports

### Usage

```bash
python benchmark_server.py [--iterations=N] [--delay=SECONDS]
```

### Requirements

- DaVinci Resolve must be running with a project open
- DaVinci Resolve MCP Server must be running
- Python packages: `requests`, `psutil` (install with `pip install requests psutil`)

### Output

The tool generates:

1. A timestamped log file (`mcp_benchmark_*.log`)
2. A JSON results file (`benchmark_results_*.json`)
3. Console output with summary statistics

### Example Output

```txt
BENCHMARK SUMMARY
==================================================
Overall average response time: 154.32ms
Overall success rate: 97.5%

Operations ranked by speed (fastest first):
  Switch to Edit Page: 98.45ms
  Get Current Page: 102.78ms
  List Timelines: 142.33ms
  Project Settings - String: 188.92ms
  Project Settings - Integer: 192.56ms
  Clear Render Queue: 200.91ms

Resource usage change during benchmark:
  Memory: 5.24MB
  CPU: 2.3%
  threads: 0
  connections: 1
==================================================
```

## Batch Automation

The batch automation script demonstrates how to automate common DaVinci Resolve workflows using the MCP server.

### Available Workflows

- **color_grade**: Apply basic color grading to all clips
- **render_timeline**: Render a timeline with specific settings
- **organize_media**: Organize media into bins by type

### Running Batch Automation

```bash
python batch_automation.py [--workflow=NAME] [--config=FILE]
```

Where:

- `--workflow` is one of: `color_grade`, `render_timeline`, `organize_media`
- `--config` is an optional path to a JSON configuration file

### Configuration

You can customize workflows by providing a JSON configuration file. See `sample_config.json` for an example.

Key configuration options:

- `project_name`: Name of the project to create or open
- `timeline_name`: Name of the timeline to use
- `media_files`: Array of file paths to import
- `render_preset`: Render preset to use
- Various settings for color correction, project settings, etc.

### Example Workflow: Color Grade

This workflow:

1. Creates or opens a project
2. Creates a timeline
3. Imports media files (if specified)
4. Switches to the color page
5. Adds a primary correction node with warm midtones
6. Adds a contrast node
7. Saves the project

### Example Workflow: Render Timeline

This workflow:

1. Creates or opens a project
2. Creates or selects a timeline
3. Imports media (for new timelines only)
4. Sets project settings
5. Switches to the deliver page
6. Clears the render queue
7. Adds the timeline to the render queue
8. Starts rendering

### Batch Processing

The script also supports batch processing across multiple projects or media files:

```bash
python batch_automation.py --config batch_config.json
```

The batch configuration file uses the following format:

```json
{
  "projects": [
    "Project1",
    "Project2"
  ],
  "operations": [
    {
      "type": "set_project_setting",
      "params": {
        "setting_name": "timelineFrameRate",
        "setting_value": 24
      }
    },
    {
      "type": "export_timeline",
      "params": {
        "preset": "YouTube 1080p"
      }
    },
    {
      "type": "import_media",
      "params": {
        "file_paths": ["/path/to/media1.mp4", "/path/to/media2.mp4"],
        "target_bin": "Imported Media"
      }
    }
  ],
  "error_handling": {
    "max_retries": 3,
    "retry_delay": 5
  }
}
```

### Extending

You can create new workflows by adding methods to the `WorkflowManager` class:

```python
def run_workflow_custom(self) -> None:
    """My custom workflow."""
    # Implement workflow steps here
    # ...
    
# Then add it to the workflows dictionary:
workflows = {
    "color_grade": self.run_workflow_color_grade,
    "render_timeline": self.run_workflow_render_timeline,
    "organize_media": self.run_workflow_organize_media,
    "custom": self.run_workflow_custom
}
```

## MCP Server Implementation

The `resolve_mcp_server.py` file is the core implementation of the DaVinci Resolve MCP Server, providing a comprehensive API for controlling DaVinci Resolve through the Model Context Protocol (MCP).

### Features

- **Multiple Communication Modes**: Supports stdio, SSE, and streamable-HTTP protocols
- **Comprehensive API**: Provides access to all major DaVinci Resolve functions
- **AI Agent Integration**: Includes an intelligent agent for automated task planning and execution
- **Error Handling**: Robust error handling and logging
- **Resource Monitoring**: Performance tracking and resource usage monitoring

### Server Configuration

```bash
# Start the server with default settings
python src/resolve_mcp_server.py

# The server runs on http://localhost:8020/mcp by default
```

### Basic Configuration

```json
{
  "host": "localhost",
  "port": 8020,
  "mode": "http",
  "log_level": "info",
  "enable_agent": true,
  "agent_config": {
    "model": "gpt-4",
    "api_key": "your-openai-api-key"
  }
}
```

### Advanced Configuration Options

```json
{
  "host": "0.0.0.0",
  "port": 8020,
  "mode": "http",
  "log_level": "debug",
  "log_file": "/path/to/logs/mcp_server.log",
  "max_log_size": 10485760,
  "max_log_backups": 5,
  "enable_agent": true,
  "agent_config": {
    "model": "gpt-4",
    "api_key": "your-openai-api-key",
    "temperature": 0.2,
    "max_tokens": 4000,
    "memory_size": 10,
    "feedback_threshold": 0.7
  },
  "cors_origins": ["*"],
  "auth": {
    "enabled": true,
    "api_key": "your-secure-api-key"
  },
  "performance": {
    "enable_metrics": true,
    "slow_operation_threshold_ms": 500
  },
  "resolve": {
    "connection_retry_count": 3,
    "connection_retry_delay_ms": 1000,
    "operation_timeout_ms": 30000
  }
}
```

### Server Startup Options

The MCP server can be started with various command-line options:

```bash
# Start with default configuration
python resolve_mcp_server.py

# Start with a specific configuration file
python resolve_mcp_server.py --config /path/to/config.json

# Override configuration options
python resolve_mcp_server.py --host 0.0.0.0 --port 9000 --log-level debug

# Start in development mode with hot reloading
python resolve_mcp_server.py --dev

# Start with AI Agent disabled
python resolve_mcp_server.py --disable-agent

# Start with WebSocket mode instead of HTTP
python resolve_mcp_server.py --mode websocket
```

### Troubleshooting

- **Server won't start**: Ensure DaVinci Resolve is running and accessible
- **Connection errors**: Check that the host and port are correct and not blocked by firewall
- **Authentication failures**: Verify your API key if authentication is enabled
- **Slow performance**: Use the benchmark tool to identify bottlenecks
- **Operation timeouts**: Increase the operation_timeout_ms in configuration
- **Agent errors**: Check that your OpenAI API key is valid and has sufficient quota

### Available API Resources

The server exposes the following key resources:

#### Project Management
- `resolve://version` - Get DaVinci Resolve version information
- `resolve://current-page` - Get the current page in DaVinci Resolve
- `resolve://projects` - List all available projects
- `resolve://current-project` - Get the name of the currently open project
- `resolve://project-settings` - Get all project settings
- `resolve://project-setting/{setting_name}` - Get a specific project setting

#### Timeline Operations
- `resolve://timelines` - List all timelines in the current project
- `resolve://current-timeline` - Get information about the current timeline
- `resolve://timeline/{timeline_name}` - Get information about a specific timeline
- `resolve://timeline/markers` - Get all markers in the current timeline
- `resolve://timeline/tracks` - Get information about all tracks in the current timeline
- `resolve://timeline/clips` - Get information about all clips in the current timeline

#### Media Operations
- `resolve://media-pool/clips` - List all clips in the media pool
- `resolve://media-pool/bins` - List all bins in the media pool
- `resolve://media-pool/structure` - Get the complete structure of the media pool
- `resolve://media-pool/selected-clips` - Get information about currently selected clips

#### Color Grading
- `resolve://color/lut-formats` - Get available LUT export formats and sizes

### Available Tools

The server provides tools for manipulating DaVinci Resolve:

#### Project Tools
- `switch_page` - Switch to a specific page in DaVinci Resolve
- `set_project_setting` - Set a project setting to a specified value
- `create_project` - Create a new project with specified settings
- `open_project` - Open an existing project by name
- `save_project` - Save the current project
- `close_project` - Close the current project
- `delete_project` - Delete a project from the database
- `export_project` - Export the project as a .drp file
- `import_project` - Import a .drp project file
- `set_project_property` - Set a project property value
- `save_layout_preset` - Save the current UI layout as a preset
- `load_layout_preset` - Load a saved UI layout preset

#### Media Tools
- `import_media` - Import media file into the current project's media pool
- `delete_media` - Delete a media clip from the media pool
- `move_media_to_bin` - Move a media clip to a specific bin
- `auto_sync_audio` - Sync audio between clips

#### Timeline Tools
- `create_timeline` - Create a new timeline with specified settings
- `add_clip_to_timeline` - Add a clip to the timeline at a specific position
- `delete_timeline` - Delete a timeline by name
- `add_marker` - Add a marker to the timeline at the current position
- `delete_marker` - Delete a marker from the timeline by index or timecode
- `add_transition` - Add a transition between clips
- `set_timeline_fps` - Change the frame rate of a timeline
- `rename_timeline` - Rename an existing timeline
- `duplicate_timeline` - Create a copy of an existing timeline
- `export_timeline` - Export the timeline using specified render settings

#### Media Tools
- `import_media` - Import media file into the current project's media pool
- `delete_media` - Delete a media clip from the media pool
- `move_media_to_bin` - Move a media clip to a specific bin
- `auto_sync_audio` - Sync audio between clips using waveform or timecode
- `create_bin` - Create a new bin in the media pool
- `delete_bin` - Delete a bin from the media pool
- `rename_clip` - Rename a clip in the media pool
- `set_clip_metadata` - Set metadata for a clip
- `create_subclip` - Create a subclip from an existing clip

#### Color Tools
- `export_lut` - Export the current grade as a LUT file
- `export_all_powergrade_luts` - Export all PowerGrade presets as LUT files
- `apply_lut` - Apply a LUT to the current clip or selected clips
- `reset_grade` - Reset the grade of the current clip
- `copy_grade` - Copy the grade from one clip to another
- `create_color_preset` - Create a new color preset from the current grade
- `apply_color_preset` - Apply a saved color preset to clips

#### Delivery Tools
- `add_to_render_queue` - Add the current timeline to the render queue
- `start_render` - Start rendering the queued items
- `clear_render_queue` - Clear all items from the render queue
- `get_render_presets` - Get a list of available render presets
- `set_render_settings` - Configure render settings for the current job
- `get_render_status` - Get the status of current render jobs
- `stop_render` - Stop the current rendering process

### Error Handling and Logging

The MCP server includes comprehensive error handling and logging capabilities:

#### Error Handling

- **Standard JSON-RPC Error Codes**: The server uses standard JSON-RPC error codes for common errors
- **Detailed Error Messages**: All errors include detailed messages to help diagnose issues
- **Error Categories**:
  - Connection errors (when DaVinci Resolve is not running or not accessible)
  - Authentication errors (when access to DaVinci Resolve is restricted)
  - Invalid parameter errors (when tool parameters are incorrect)
  - Execution errors (when operations fail during execution)
  - Resource not found errors (when requested resources don't exist)

#### Logging

- **Log Levels**: Configurable log levels (DEBUG, INFO, WARNING, ERROR)
- **Log Output**: Logs are output to both console and log files
- **Log File Rotation**: Log files are automatically rotated to prevent excessive disk usage
- **Performance Logging**: Optional performance metrics logging for debugging

### AI Agent Integration

The server includes an AI Agent (`ResolveAgent`) that can assist with complex tasks through natural language processing and automated execution:

```python
# Example of using the AI Agent
result = await agent.process_request("Create a highlight reel from my interview clips")
```

#### Agent Architecture

The AI Agent is built with a modular architecture consisting of several specialized components:

- **Core Components**:
  - `ResolveAgent`: Main agent class that orchestrates all components
  - `AgentContext`: Maintains context information during interactions
  - `AgentState`: Tracks the current state and statistics of the agent

- **Task Management**:
  - `TaskPlanner`: Breaks down natural language requests into executable steps
  - `Plan` and `PlanStep`: Structured representations of tasks and subtasks
  - `TaskExecutor`: Executes planned steps through the DaVinci Resolve API

- **Intelligence Components**:
  - `VideoAnalyzer`: Analyzes video content for intelligent editing decisions
  - `ResolveDocRAG`: Retrieval Augmented Generation system that incorporates DaVinci Resolve documentation
  - `FeedbackLoop`: Learning system that improves from execution results and user feedback
  - `MemoryManager`: Maintains context and knowledge across multiple interactions

#### Agent Capabilities

The AI Agent provides the following capabilities:

- **Natural Language Understanding**: Processes user requests in plain language
- **Intelligent Task Planning**: Breaks down complex requests into executable steps
- **Automated Execution**: Executes plans through the DaVinci Resolve API
- **Video Content Analysis**: Analyzes video content for intelligent editing decisions
- **Documentation Integration**: Uses RAG to incorporate DaVinci Resolve documentation
- **Continuous Learning**: Improves from execution results and user feedback
- **Context Awareness**: Maintains context across interactions
- **Error Recovery**: Provides recovery suggestions when operations fail

#### Agent API Endpoints

The following agent-specific endpoints are available:

- **Tools**:
  - `agent_process_request` - Process a natural language request through the agent
  - `agent_suggest_next_actions` - Get AI-suggested next actions based on project context
  - `agent_learn_from_feedback` - Provide feedback to help the AI agent learn and improve

- **Resources**:
  - `resolve://agent/state` - Get the current state and statistics of the AI agent
  - `resolve://agent/current-task` - Get information about the task currently being executed
  - `resolve://agent/task-history` - Get recent task history from the AI agent

#### Example Agent Workflow

```python
# Initialize the agent
agent = ResolveAgent(resolve_server=mcp)

# Process a user request
result = await agent.process_request("Create a montage from clips tagged 'highlight'")

# Get suggested next actions
suggestions = await agent.suggest_next_actions()

# Provide feedback to improve the agent
await agent.learn_from_feedback(task_id="task_123", 
                              feedback="The montage transitions were too abrupt", 
                              success=True)
```

## Advanced Usage and Examples

### Combining Multiple Operations

The MCP server allows you to chain multiple operations together to create complex workflows:

```python
# Example: Import media, create timeline, add clips, and render
import requests
import json

BASE_URL = "http://localhost:8020/mcp"

# Helper function for MCP calls
def mcp_call(method, params=None):
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": method,
        "params": params or {}
    }
    response = requests.post(BASE_URL, json=payload)
    return response.json()

# 1. Import media files
media_files = ["/path/to/interview1.mp4", "/path/to/interview2.mp4", "/path/to/b-roll.mp4"]
for file in media_files:
    mcp_call("import_media", {"file_path": file})

# 2. Create a new timeline
mcp_call("create_timeline", {"name": "Interview Compilation", "width": 1920, "height": 1080, "fps": 24})

# 3. Add clips to timeline
clips = mcp_call("resolve://media-pool/clips")
for i, clip in enumerate(clips.get("result", [])):
    if "interview" in clip["name"].lower():
        mcp_call("add_clip_to_timeline", {
            "clip_name": clip["name"],
            "track": 1,
            "start_frame": i * 300  # Space clips out
        })

# 4. Switch to color page and apply a LUT
mcp_call("switch_page", {"page": "color"})
mcp_call("apply_lut", {"lut_path": "/path/to/cinematic.cube"})

# 5. Add to render queue and start rendering
mcp_call("switch_page", {"page": "deliver"})
mcp_call("add_to_render_queue", {
    "preset": "YouTube 1080p",
    "output_path": "/path/to/output/"
})
mcp_call("start_render")
```

### Using the AI Agent for Complex Tasks

```python
# Example: Using the AI Agent for a complex editing task
import requests
import json

BASE_URL = "http://localhost:8020/mcp"

# Helper function for MCP calls
def mcp_call(method, params=None):
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": method,
        "params": params or {}
    }
    response = requests.post(BASE_URL, json=payload)
    return response.json()

# Use the AI Agent to create a highlight reel
result = mcp_call("agent_process_request", {
    "request": "Create a 2-minute highlight reel from my interview footage. "
               "Use clips with positive sentiment, add smooth transitions, "
               "apply the 'Cinematic' LUT, and add background music."
})

# Check the result
print(json.dumps(result, indent=2))

# Get suggested next actions
suggestions = mcp_call("agent_suggest_next_actions")
print("Suggested next actions:")
for suggestion in suggestions.get("result", []):
    print(f"- {suggestion}")

# Provide feedback to the agent
mcp_call("agent_learn_from_feedback", {
    "task_id": result["result"]["plan_id"],
    "feedback": "The highlight reel was good, but transitions were too abrupt",
    "success": True
})
```

## Best Practices

- Always test workflows with sample data before using with production content
- Keep DaVinci Resolve open with a project loaded before running tools
- Check the MCP server logs if operations fail
- Use the benchmark tool to identify slow operations
- Consider adding delays between operations if reliability issues occur
- Review logs after automation runs to identify any issues
- When using the AI Agent, provide clear and specific instructions
- Provide feedback to the AI Agent to improve its performance over time
- Use error handling in your scripts to gracefully handle failures
- Monitor resource usage when running complex automation scripts
- Create reusable functions for common operations in your workflows

## Security Considerations

### Authentication

The MCP server supports API key authentication to prevent unauthorized access:

```json
{
  "auth": {
    "enabled": true,
    "api_key": "your-secure-api-key"
  }
}
```

When authentication is enabled, all requests must include the API key in the Authorization header:

```python
headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer your-secure-api-key"
}
response = requests.post(BASE_URL, json=payload, headers=headers)
```

### Network Security

- By default, the server only listens on localhost (127.0.0.1) to prevent external access
- If you need to access the server from other machines, set the host to "0.0.0.0" and implement proper authentication
- Consider using HTTPS with a reverse proxy like Nginx for production deployments
- Use firewall rules to restrict access to the server port

### Data Security

- The server does not store sensitive data by default
- API keys and credentials are stored in memory only
- When using the AI Agent, be aware that data may be sent to external API providers
- Implement proper access controls for media files and projects

## Performance Optimization

### Server Performance

- Use the performance metrics to identify slow operations
- Increase the operation timeout for complex operations
- Consider running the server on a dedicated machine for heavy workloads
- Monitor memory usage when processing large media files

### DaVinci Resolve Performance

- Close unnecessary projects to reduce memory usage
- Use optimized media for smoother playback during automation
- Consider hardware requirements when automating complex operations
- Batch operations when possible to reduce overhead

## API Reference Documentation

### Common Parameters

Many MCP tools share common parameters:

| Parameter | Type | Description |
|-----------|------|-------------|
| `project_name` | string | The name of the project to operate on |
| `timeline_name` | string | The name of the timeline to operate on |
| `clip_name` | string | The name of the clip to operate on |
| `track_index` | integer | The index of the track to operate on (1-based) |
| `frame_number` | integer | The frame number to operate on |
| `page` | string | The page to switch to ('media', 'cut', 'edit', 'fusion', 'color', 'fairlight', 'deliver') |

### Project Management Tools

#### create_project

Creates a new DaVinci Resolve project.

**Parameters:**
```json
{
  "project_name": "My New Project",
  "preset": "Custom Preset"  // Optional
}
```

**Returns:**
```json
{
  "result": {
    "success": true,
    "project_name": "My New Project"
  }
}
```

#### open_project

Opens an existing DaVinci Resolve project.

**Parameters:**
```json
{
  "project_name": "My Project"
}
```

**Returns:**
```json
{
  "result": {
    "success": true,
    "project_name": "My Project"
  }
}
```

### Timeline Tools

#### create_timeline

Creates a new timeline in the current project.

**Parameters:**
```json
{
  "name": "My Timeline",
  "width": 1920,         // Optional
  "height": 1080,        // Optional
  "fps": 24,             // Optional
  "use_custom_settings": true  // Optional
}
```

**Returns:**
```json
{
  "result": {
    "success": true,
    "timeline_name": "My Timeline"
  }
}
```

#### add_clip_to_timeline

Adds a clip from the media pool to the current timeline.

**Parameters:**
```json
{
  "clip_name": "Interview.mp4",
  "track": 1,                  // Optional, defaults to 1
  "start_frame": 0,            // Optional, defaults to timeline playhead
  "end_frame": null,           // Optional
  "fit_method": "fit"          // Optional: "fit", "fill", "stretch", "none"
}
```

**Returns:**
```json
{
  "result": {
    "success": true,
    "clip_name": "Interview.mp4",
    "track": 1,
    "start_frame": 0,
    "end_frame": 240
  }
}
```

### Media Tools

#### import_media

Imports media files into the media pool.

**Parameters:**
```json
{
  "file_path": "/path/to/media.mp4",
  "target_bin": "My Bin"  // Optional
}
```

**Returns:**
```json
{
  "result": {
    "success": true,
    "imported_files": ["/path/to/media.mp4"],
    "clip_names": ["media.mp4"]
  }
}
```

### Color Tools

#### apply_lut

Applies a LUT to the current clip or selected clips.

**Parameters:**
```json
{
  "lut_path": "/path/to/my_lut.cube",
  "clip_name": "Interview.mp4"  // Optional, applies to current clip if not specified
}
```

**Returns:**
```json
{
  "result": {
    "success": true,
    "applied_to": ["Interview.mp4"]
  }
}
```

### AI Agent Tools

#### agent_process_request

Sends a natural language request to the AI Agent for processing.

**Parameters:**
```json
{
  "request": "Create a highlight reel from my interview footage",
  "context": {  // Optional
    "project": "Interview Project",
    "timeline": "Main Timeline"
  }
}
```

**Returns:**
```json
{
  "result": {
    "success": true,
    "plan_id": "task-123456",
    "steps": [
      "Analyzing interview footage",
      "Identifying key moments",
      "Creating highlight timeline",
      "Adding transitions",
      "Applying color grading"
    ],
    "status": "in_progress",
    "message": "Creating your highlight reel. This may take a few minutes."
  }
}
```

## Version Compatibility

### DaVinci Resolve Version Support

| MCP Server Version | DaVinci Resolve Versions | Notes |
|--------------------|--------------------------|-------|
| 1.0.0 | 18.0 - 18.5 | Initial release |
| 1.1.0 | 18.0 - 18.6 | Added AI Agent support |
| 1.2.0 | 18.5 - 18.6 | Added delivery tools |
| 2.0.0 | 18.5 - 19.0 | Major update with new API endpoints |

### Operating System Compatibility

| Operating System | Status | Notes |
|------------------|--------|-------|
| Windows 10/11 | Fully supported | Recommended for production use |
| macOS 12+ | Fully supported | Recommended for production use |
| Linux | Limited support | Basic functionality only |

## Integration with Other Systems

### Web Applications

The MCP server can be integrated with web applications using standard HTTP requests:

```javascript
// Example: JavaScript integration
async function callMcpServer(method, params) {
  const response = await fetch('http://localhost:8020/mcp', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      jsonrpc: '2.0',
      id: 1,
      method,
      params
    })
  });
  return response.json();
}

// Example usage
const projects = await callMcpServer('resolve://projects');
console.log(projects);
```

### CI/CD Pipelines

The MCP server can be integrated with CI/CD pipelines for automated media processing:

```yaml
# Example: GitHub Actions workflow
name: Process Media

on:
  push:
    paths:
      - 'media/**'

jobs:
  process:
    runs-on: self-hosted
    steps:
      - name: Checkout code
        uses: actions/checkout@v2
      
      - name: Process media files
        run: |
          python scripts/process_media.py
```

### Custom Applications

The MCP server can be integrated with custom applications using the provided API:

```python
# Example: Custom application integration
from resolve_mcp_client import ResolveMcpClient

client = ResolveMcpClient(host='localhost', port=8020)

# Create a new project
project_name = "Generated Project"
client.create_project(project_name)

# Import media files
media_files = ["path/to/file1.mp4", "path/to/file2.mp4"]
client.import_media(media_files)

# Create a timeline
client.create_timeline("Main Timeline")

# Add clips to timeline
clips = client.get_media_pool_clips()
for clip in clips:
    client.add_clip_to_timeline(clip["name"])

# Apply color grading
client.switch_page("color")
client.apply_lut("path/to/lut.cube")

# Render the timeline
client.switch_page("deliver")
client.add_to_render_queue(preset="YouTube 1080p")
client.start_render()
```
