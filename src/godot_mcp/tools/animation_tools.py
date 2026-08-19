"""Tool handlers for animation track and keyframe creation."""

from godot_mcp.client.base import GodotClient
from godot_mcp.models.animation import CreateAnimationInput
from godot_mcp.tools.formatters import format_result


async def handle_create_animation(
    client: GodotClient,
    params: CreateAnimationInput,
) -> str:
    """Handle godot_create_animation tool execution."""
    raw_tracks = [t.model_dump() for t in params.tracks]
    result = await client.create_animation(
        animation_name=params.animation_name,
        length=params.length,
        loop_mode=params.loop_mode.value,
        step=params.step,
        tracks=raw_tracks,
        animation_player_path=params.animation_player_path,
        save_path=params.save_path,
    )
    return format_result(result)
