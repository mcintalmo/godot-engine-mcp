"""Tool handlers for Godot Play Mode and interactive debug controls."""

from godot_mcp.client.base import GodotClient
from godot_mcp.models.play import (
    GetPlayStateInput,
    PlaySceneInput,
    SetPlayStateInput,
    StopSceneInput,
)
from godot_mcp.tools.formatters import format_result


async def handle_play_scene(
    client: GodotClient,
    params: PlaySceneInput,
) -> str:
    """Handle godot_play_scene tool execution."""
    result = await client.play_scene(
        mode=params.mode.value,
        custom_scene_path=params.custom_scene_path,
    )
    return format_result(result)


async def handle_stop_scene(
    client: GodotClient,
    params: StopSceneInput,
) -> str:
    """Handle godot_stop_scene tool execution."""
    result = await client.stop_scene()
    return format_result(result)


async def handle_get_play_state(
    client: GodotClient,
    params: GetPlayStateInput,
) -> str:
    """Handle godot_get_play_state tool execution."""
    result = await client.get_play_state()
    return format_result(result)


async def handle_set_play_state(
    client: GodotClient,
    params: SetPlayStateInput,
) -> str:
    """Handle godot_set_play_state tool execution."""
    result = await client.set_play_state(
        pause=params.pause,
        time_scale=params.time_scale,
        step_frames=params.step_frames,
    )
    return format_result(result)
