# Tools Usage (MCP)

This document describes the initial set of MCP-exposed tools and how to use them
via the `client_simulator` CLI.

## Available tool categories
- fusion
- audio
- color
- render
- jobs

## Example tools
- `fusion.create_composition` (params: script_summary, shot_list, style)
- `fusion.apply_to_timeline` (params: composition_spec, timeline_id)
- `audio.create_chain` (params: target_loudness, compression_ratio)
- `color.auto_color_timeline` (params: timeline_id)
- `render.preview` (params: timeline_id, start_frame, end_frame)
- `jobs.status` (params: job_id)
- `jobs.cancel` (params: job_id)

## Client CLI Example
- List tools in category `fusion`:

```
tools list fusion
```

- Call a tool with JSON arguments:

```
tools call fusion.create_composition {"script_summary":"A short summary","shot_list":[{"start":0,"end":100,"desc":"opening"}]}
```

- Check job status:

```
tools status <job_id>
```

- Cancel a job:

```
tools cancel <job_id>
```

This is an initial guide; full JSON schemas and parameter descriptions will be
added with the tool API contract (next iteration).
