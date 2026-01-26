#!/usr/bin/env python3
"""
DaVinci Resolve MCP Server - Fusion Operations Utilities

This module provides functions for working with DaVinci Resolve Fusion operations:
- Add Fusion effects and generators to timeline items
- Set timeline item properties (transform/crop/composite/etc.)
"""

from typing import Dict, Any, Optional, List
import logging

# Configure logging
logger = logging.getLogger("davinci-resolve-mcp.fusion_operations")


def get_item_by_id(resolve, timeline_item_id: str):
    """
    Helper to find a TimelineItem by its unique ID.
    Note: Iterating the whole timeline is expensive.
    """
    pm = resolve.GetProjectManager()
    project = pm.GetCurrentProject()
    timeline = project.GetCurrentTimeline()

    if not timeline:
        return None

    track_count_video = timeline.GetTrackCount("video")

    for i in range(1, track_count_video + 1):
        items = timeline.GetItemListInTrack("video", i)
        if items:
            for item in items:
                try:
                    # In Resolve v19+, TimelineItem has GetUniqueId()
                    uid = item.GetUniqueId()
                    if str(uid) == str(timeline_item_id):
                        return item
                except:
                    pass

                # Fallback to name match for older versions
                if item.GetName() == timeline_item_id:
                    return item
    return None


def set_timeline_item_property(
    resolve, timeline_item_id: str, property_name: str, property_value: Any
) -> Dict[str, Any]:
    """Set a property for a timeline item (transform, crop, composite, etc.).

    Args:
        resolve: The DaVinci Resolve instance.
        timeline_item_id: Clip ID or Name.
        property_name: Property name (e.g., 'Pan', 'ZoomX').
        property_value: New value.

    Returns:
        Dict[str, Any]: Result dictionary.
    """
    item = get_item_by_id(resolve, timeline_item_id)
    if not item:
        return {
            "success": False,
            "error": f"Timeline item '{timeline_item_id}' not found",
        }

    try:
        # Resolve API: SetProperty(name, value)
        result = item.SetProperty(property_name, property_value)
        return {
            "success": bool(result),
            "item": item.GetName(),
            "property": property_name,
            "value": property_value,
        }
    except Exception as e:
        logger.error(f"Error setting timeline item property: {e}")
        return {"success": False, "error": str(e)}


def register_tools(proxy):
    """Register Fusion and Timeline Item tools with the proxy."""
    from ..resolve_mcp_server import get_resolve

    def set_transform(timeline_item_id: str, property_name: str, value: float):
        """Set transform property (Pan, Tilt, ZoomX, ZoomY, Rotation)."""
        return set_timeline_item_property(
            get_resolve(), timeline_item_id, property_name, value
        )

    proxy.register_tool(
        "set_timeline_item_transform",
        set_transform,
        "timeline",
        "Set transform property (Pan, Tilt, ZoomX, ZoomY, Rotation) for a specific clip",
        {
            "timeline_item_id": {"type": "string", "description": "Clip ID or Name"},
            "property_name": {
                "type": "string",
                "description": "Property name (e.g., 'Pan', 'ZoomX')",
            },
            "value": {"type": "number", "description": "New value"},
        },
    )
    # Register new Fusion effect and generator tools
    proxy.register_tool(
        "add_fusion_effect",
        add_fusion_effect,
        "fusion",
        "Add a Fusion effect tool to a timeline item. Settings may include keyframes.",
        {
            "timeline_item_id": {"type": "string", "description": "Timeline item ID"},
            "effect_name": {
                "type": "string",
                "description": "Name of the Fusion effect (e.g., 'Vignette')",
            },
            "settings": {
                "type": "object",
                "description": "Optional settings dict",
                "optional": True,
            },
        },
    )
    proxy.register_tool(
        "add_fusion_generator",
        add_fusion_generator,
        "fusion",
        "Add a Fusion generator tool via a Merge node. Settings may include keyframes.",
        {
            "timeline_item_id": {"type": "string", "description": "Timeline item ID"},
            "generator_name": {
                "type": "string",
                "description": "Name of the generator tool (e.g., 'Text+')",
            },
            "settings": {
                "type": "object",
                "description": "Optional settings dict",
                "optional": True,
            },
        },
    )
    return 1


def add_fusion_effect(
    resolve, timeline_item_id: str, effect_name: str, settings: Dict[str, Any] = None
) -> str:
    """Add a Fusion effect to a timeline item.

    Args:
        resolve: The DaVinci Resolve instance.
        timeline_item_id: The unique ID of the timeline item.
        effect_name: The name of the effect (e.g., 'Blur').
        settings: Optional dictionary of settings to apply to the effect.

    Returns:
        str: A message indicating success or failure.
    """
    item = get_item_by_id(resolve, timeline_item_id)
    if not item:
        return f"Error: Timeline item '{timeline_item_id}' not found."

    # Ensure a Fusion composition exists
    comp_count = item.GetFusionCompCount()
    if comp_count == 0:
        try:
            item.AddFusionComp()
        except Exception as e:
            return f"Error creating Fusion Composition: {e}"
        comp_count = item.GetFusionCompCount()

    # Use the latest composition (the one we just added or the highest index)
    comp = item.GetFusionCompByIndex(comp_count)
    if not comp:
        return "Error: Fusion Composition object is null."

    logger.info(f"Adding effect '{effect_name}' to comp")
    try:
        new_tool = comp.AddTool(effect_name)
        if not new_tool:
            return f"Error: Failed to add tool '{effect_name}'."

        # Apply settings – simple values or keyframes
        if settings:
            for key, val in settings.items():
                try:
                    if isinstance(val, dict) and "keyframes" in val:
                        kf_data = val["keyframes"]
                        # Initialise a BezierSpline for the parameter
                        init_cmd = f"{new_tool.Name}.{key} = BezierSpline()"
                        comp.Execute(init_cmd)
                        for frame, kf_val in kf_data.items():
                            try:
                                f_num = float(frame)
                                if isinstance(kf_val, str):
                                    kf_cmd = (
                                        f'{new_tool.Name}.{key}[{f_num}] = "{kf_val}"'
                                    )
                                else:
                                    kf_cmd = (
                                        f"{new_tool.Name}.{key}[{f_num}] = {kf_val}"
                                    )
                                comp.Execute(kf_cmd)
                            except Exception:
                                pass
                    else:
                        new_tool.SetInput(key, val)
                except Exception as ex:
                    logger.warning(f"Failed to set input {key}: {ex}")

        # Wire the new tool into the existing pipeline (MediaIn → NewTool → MediaOut)
        tool_list = comp.GetToolList(False)
        media_out = None
        media_in = None
        for _, tool in tool_list.items():
            if tool.ID == "MediaOut" or "MediaOut" in tool.Name:
                media_out = tool
            elif tool.ID == "MediaIn" or "MediaIn" in tool.Name:
                media_in = tool

        if media_out:
            # Grab whatever is currently feeding MediaOut
            current_input = media_out.GetInput("Input")
            if current_input:
                new_tool.SetInput("Input", current_input)
                media_out.SetInput("Input", new_tool.FindMainOutput(1))
                logger.info(
                    "Successfully wired new tool into pipeline (inserted before MediaOut)."
                )
            elif media_in:
                new_tool.SetInput("Input", media_in.FindMainOutput(1))
                media_out.SetInput("Input", new_tool.FindMainOutput(1))
                logger.info(
                    "Successfully wired new tool into pipeline (between MediaIn and MediaOut)."
                )
            else:
                # No inputs – just connect tool to MediaOut directly
                media_out.SetInput("Input", new_tool.FindMainOutput(1))
                logger.info(
                    "Wired new tool directly to MediaOut (no MediaIn detected)."
                )
        else:
            logger.warning("MediaOut not found; cannot auto‑wire tool.")

        return f"Successfully added '{effect_name}' to item '{timeline_item_id}' (ID: {comp.GetAttrs()['COMPS_Name']})"
    except Exception as e:
        tb = __import__("traceback").format_exc()
        logger.error(f"Error adding fusion effect: {tb}")
        return f"Error adding fusion effect: {e} | {tb}"


def add_fusion_generator(
    resolve, timeline_item_id: str, generator_name: str, settings: Dict[str, Any] = None
) -> str:
    """Add a Fusion generator to a timeline item.

    Args:
        resolve: The DaVinci Resolve instance.
        timeline_item_id: The unique ID of the timeline item.
        generator_name: The name of the generator (e.g., 'Text+').
        settings: Optional dictionary of settings to apply to the generator.

    Returns:
        str: A message indicating success or failure.
    """
    project = resolve.GetProjectManager().GetCurrentProject()
    timeline = project.GetCurrentTimeline()
    if not timeline:
        return "Error: No current timeline"

    # Locate the target timeline item
    target_item = None
    track_count = timeline.GetTrackCount("video")
    for i in range(1, track_count + 1):
        items = timeline.GetItemListInTrack("video", i)
        if items:
            for item in items:
                try:
                    if item.GetUniqueId() == timeline_item_id:
                        target_item = item
                        break
                except Exception:
                    pass
        if target_item:
            break

    if not target_item:
        return f"Error: Timeline item {timeline_item_id} not found"

    # Ensure a Fusion composition exists
    comp_count = target_item.GetFusionCompCount()
    if comp_count == 0:
        target_item.AddFusionComp()
        comp_count = target_item.GetFusionCompCount()
    comp = target_item.GetFusionCompByIndex(comp_count)
    if not comp:
        return "Error: Could not get Fusion composition"

    logger.info(f"Adding generator '{generator_name}' to comp")
    try:
        gen_tool = comp.AddTool(generator_name)
        if not gen_tool:
            return f"Error: Failed to add tool '{generator_name}'."
        # Apply settings similar to add_fusion_effect
        if settings:
            for key, val in settings.items():
                try:
                    if isinstance(val, dict) and "keyframes" in val:
                        kf_data = val["keyframes"]
                        init_cmd = f"{gen_tool.Name}.{key} = BezierSpline()"
                        comp.Execute(init_cmd)
                        for frame, kf_val in kf_data.items():
                            try:
                                f_num = float(frame)
                                if isinstance(kf_val, str):
                                    kf_cmd = (
                                        f'{gen_tool.Name}.{key}[{f_num}] = "{kf_val}"'
                                    )
                                else:
                                    kf_cmd = (
                                        f"{gen_tool.Name}.{key}[{f_num}] = {kf_val}"
                                    )
                                comp.Execute(kf_cmd)
                            except Exception:
                                pass
                    else:
                        gen_tool.SetInput(key, val)
                except Exception as ex:
                    logger.warning(f"Failed to set input {key}: {ex}")

        # Insert a Merge node and wire everything together
        merge_tool = comp.AddTool("Merge")
        if not merge_tool:
            return "Error: Failed to add Merge tool."

        # Find MediaIn / MediaOut in the composition
        tool_list = comp.GetToolList(False)
        media_out = None
        media_in = None
        for _, tool in tool_list.items():
            if tool.ID == "MediaOut" or "MediaOut" in tool.Name:
                media_out = tool
            elif tool.ID == "MediaIn" or "MediaIn" in tool.Name:
                media_in = tool

        if media_out:
            # Connect existing input (if any) as background of the merge
            current_input = media_out.GetInput("Input")
            if current_input:
                merge_tool.SetInput("Background", current_input)
            elif media_in:
                merge_tool.SetInput("Background", media_in.FindMainOutput(1))
            else:
                logger.warning(
                    "No MediaIn or existing input found for Merge background."
                )

            # Foreground is the generator output
            merge_tool.SetInput("Foreground", gen_tool.FindMainOutput(1))
            # Finally connect merge to MediaOut
            media_out.SetInput("Input", merge_tool.FindMainOutput(1))
            logger.info("Successfully wired generator via Merge.")
            return f"Added generator '{generator_name}'"
        else:
            return "Error: Could not find MediaOut to wire generator"
    except Exception as e:
        logger.error(f"Error adding generator: {e}")
        return f"Error adding generator: {e}"


# End of file
