# DaVinci Resolve MCP Server Tools

This directory contains utilities for working with the DaVinci Resolve MCP Server:

- **benchmark_server.py**: Performance testing tool
- **batch_automation.py**: Workflow automation script
- **sample_config.json**: Example configuration file

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

```
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

### Usage

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

## Best Practices

- Always test workflows with sample data before using with production content
- Keep DaVinci Resolve open and with a project loaded before running tools
- Check the MCP server logs if operations fail
- Use the benchmark tool to identify slow operations
- Consider adding delays between operations if reliability issues occur
- Review logs after automation runs to identify any issues 