#!/usr/bin/env python3
"""DaVinci Resolve MCP Prompts - Analysis workflow prompts."""


def register_analysis_prompts(mcp, resolve, logger):
    """Register analysis-related prompts."""

    @mcp.prompt()
    def analyze_media(
        target: str = "file",
        depth: str = "full",
        finished_video: bool = False,
        include_visuals: bool = True,
        include_transcription: bool = True,
        persist: bool = True,
    ) -> str:
        """
        Source-safe media-analysis workflow for a file, clip, bin, timeline, or project.

        Args:
            target: What to analyze (file, clip, bin, timeline, project)
            depth: Analysis depth (quick, full, deep)
            finished_video: Whether this is for a finished video
            include_visuals: Include visual inspection
            include_transcription: Include audio transcription
            persist: Persist analysis results
        """
        return f"""You are a DaVinci Resolve Media Analyst.
The user wants to analyze a {target} with {depth} depth.

Configuration:
- Finished video: {finished_video}
- Visual inspection: {'enabled' if include_visuals else 'disabled'}
- Transcription: {'enabled' if include_transcription else 'disabled'}
- Persist results: {'yes' if persist else 'no'}

Please perform a source-safe analysis of the specified target:
1. Inspect the media file/clip properties (codec, resolution, frame rate, color space).
2. Run visual analysis if enabled - detect black frames, fades, scene cuts, silence.
3. Run audio analysis if enabled - detect silence, noise, levels.
4. Check for motion blur, stabilization artifacts, or other quality issues.
5. Write results to sidecar files (never modify source media).

Ask the user for the specific file path, clip name, or folder to analyze."""

    @mcp.prompt()
    def analyze_and_propose_grade(hero_clip_id: str) -> str:
        """
        Hero-clip color pipeline end-to-end.

        Args:
            hero_clip_id: The unique ID of the hero/reference clip
        """
        return f"""You are a Professional Colorist.
The user wants to analyze a hero clip and propose a grade based on it.

Hero clip ID: {hero_clip_id}

Please perform the following pipeline:
1. Analyze the hero clip's exposure, contrast, color balance, and skin tones.
2. Capture representative frames from the hero clip for visual evidence.
3. Build a grade_evidence_base documenting the creative decisions.
4. Propose a color grading strategy that matches the hero clip's look.
5. Suggest a node structure for applying the grade to other clips.

Before applying any grade, always inspect the hero clip's characteristics:
- Camera format and LOG profile
- Lighting conditions
- Color temperature and mood
- Skin tone placement in vectorscope

Ask the user to confirm the grade proposal before applying it to other clips."""

    @mcp.prompt()
    def match_bin_to_hero(
        hero_clip_id: str,
        method: str = "visual_match",
    ) -> str:
        """
        Match bin clips to a hero grade via dry-run first.

        Args:
            hero_clip_id: The hero/reference clip ID
            method: Matching method (visual_match, metadata_match, hybrid)
        """
        return f"""You are a Professional Colorist Assistant.
The user wants to match clips in a bin to a hero clip's grade.

Hero clip: {hero_clip_id}
Matching method: {method}

Please perform the following:
1. First, analyze the hero clip's grade characteristics (node structure, LUTs, wheel settings).
2. List all clips in the target bin/folder.
3. For each clip, perform a dry-run matching analysis:
   - Compare camera format, white balance, exposure
   - Assess grade transfer feasibility
   - Flag clips that need manual adjustment
4. Generate a match report showing:
   - Clips that match well
   - Clips that need adjustment
   - Clips that can't be matched (different cameras/lighting)
5. Only proceed with actual grade application after user confirmation.

Ask the user for the bin/folder name and review the dry-run report."""

    @mcp.prompt()
    def verify_timeline_coverage() -> str:
        """Verify current timeline has full media analysis coverage."""
        return """Verify the current timeline has full analysis coverage.

1. Confirm with timeline(action="get_current") that a timeline is open.
2. Call media_analysis(action="analyze_sequence", params={"track_types": ["video"]}).
3. Inspect the returned manifest: clip_count vs successful_clip_count vs failed_clip_count.
4. If partial_success is true, surface failed_clip_ids and recommend retry-only-failed.
5. Call media_analysis(action="summarize") and read the provenance.source_reports
   list to verify every contributing clip has a current analysis_signature.
6. Report any clips in provenance.missing_reports as coverage gaps."""

    @mcp.prompt()
    def open_and_analyze_selection() -> str:
        """Launch the control panel and analyze the current Resolve clip selection."""
        return """Open the analysis control panel and analyze the selected clips.

1. Call resolve_control(action="open_control_panel"). Surface the returned URL.
2. Call media_analysis(action="analyze_clip", params={"selected": true}).
3. Report manifest.successful_clip_count and any vision_pending count.
4. If vision_pending > 0, walk each pending clip's frame_paths and call
   media_analysis(action="commit_vision") per the host_chat_paths protocol.
5. Direct the user to the control panel URL for inline review of results."""

    @mcp.prompt()
    def prep_color_handoff(output_dir: str = "") -> str:
        """
        Generate a coverage + provenance + render-presets handoff packet for online/color.

        Args:
            output_dir: Custom output directory (defaults to ~/Documents/davinci-resolve-mcp-analysis/handoff)
        """
        target_dir = output_dir or "~/Documents/davinci-resolve-mcp-analysis/handoff"
        return f"""Prepare a color/online handoff packet.

1. Call media_analysis(action="summarize") and capture provenance.source_reports.
2. Call render(action="list_render_presets") and timeline(action="probe_timeline_structure").
3. Call timeline_versioning(action="list_versions") for the current timeline.
4. Write a handoff manifest to: {target_dir}/handoff_<timestamp>.json containing:
   - provenance source_reports list (clip signatures + paths)
   - render preset names
   - timeline version list
   - any caps usage at the time of handoff (media_analysis.get_caps)
5. Surface the manifest path back to the user. Do not write beside source media."""

    logger.info("Analysis prompts registered")
