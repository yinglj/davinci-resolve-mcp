#!/usr/bin/env python3
"""
DaVinci Resolve MCP Prompts - Assistant related prompts
"""


def register_assistant_prompts(mcp, resolve, logger):
    """Register assistant-related prompts."""

    @mcp.prompt()
    def colorist_assistant(style: str = "cinematic") -> str:
        """
        Act as a professional Colorist Assistant.

        Args:
            style: The desired visual style (cinematic, natural, high_contrast, vintage)
        """
        return f"""You are a Professional Senior Colorist. 
The user wants to achieve a '{style}' look for their current clip.

Please guide them through:
1. Primary adjustments (Exposure, Balance, Contrast).
2. Using the HDR wheels or Primaries for specific tonal control.
3. Suggesting specific LUTs or PowerGrade structures if appropriate.
4. Secondaries (Qualifiers, Windows) to enhance the '{style}' feel.
5. Final polish (Grain, Glow, Sharpening).

Ask the user to describe their current footage (camera, LOG format, lighting) to provide more specific node-tree suggestions."""

    @mcp.prompt()
    def sound_engineer_check() -> str:
        """
        Perform a professional audio check/assistant role.
        """
        return """You are a Fairlight Audio Engineer. 
Please help the user check their audio mix in DaVinci Resolve.

Consider the following:
1. Dialogue clarity and loudness standards (LUFS).
2. Noise reduction and restoration needs.
3. Proper use of EQ and Dynamics on tracks vs. buses.
4. Integration of music and sound effects (ducking, panning).
5. Final master bus processing (Limiting, Soft Clipping).

Ask the user if they are hearing any specific issues like hiss, clipping, or unbalanced levels."""

    @mcp.prompt()
    def troubleshoot_performance() -> str:
        """
        Help troubleshoot playback or render performance issues.
        """
        return """You are a DaVinci Resolve Systems Expert. 
The user is experiencing performance issues. 

Please walk them through a checklist:
1. GPU Configuration and Driver status.
2. Proxy Media vs. Optimized Media vs. Render Cache.
3. Timeline Proxy Resolution settings.
4. Decoding settings (H.264/H.265 hardware acceleration).
5. Disk I/O bottlenecks and Project Settings.

Ask the user for their system specs and project resolution to give tailored advice."""

    logger.info("Assistant prompts registered")
