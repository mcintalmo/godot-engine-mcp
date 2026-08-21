"""Tool handlers for Godot Scene Tree and .tscn Diffing."""

from godot_mcp.client.base import GodotClient
from godot_mcp.models.scene_diff import DiffSceneInput
from godot_mcp.tools.formatters import format_result


async def handle_diff_scene(
    client: GodotClient,
    params: DiffSceneInput,
) -> str:
    """Handle godot_diff_scene tool execution."""
    result = await client.diff_scene(
        scene_path=params.scene_path,
        target_scene_path=params.target_scene_path,
    )
    return format_result(result)
