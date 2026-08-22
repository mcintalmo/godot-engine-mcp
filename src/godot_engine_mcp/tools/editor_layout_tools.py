"""Tool handlers for Godot Editor Workspace Layout and Screen Control."""

from godot_engine_mcp.client.base import GodotClient
from godot_engine_mcp.models.editor_layout import (
    GetEditorLayoutInput,
    SetEditorLayoutInput,
)
from godot_engine_mcp.tools.formatters import format_result


async def handle_get_editor_layout(
    client: GodotClient,
    params: GetEditorLayoutInput,
) -> str:
    """Handle godot_get_editor_layout tool execution."""
    result = await client.get_editor_layout(
        include_open_scenes=params.include_open_scenes,
    )
    return format_result(result)


async def handle_set_editor_layout(
    client: GodotClient,
    params: SetEditorLayoutInput,
) -> str:
    """Handle godot_set_editor_layout tool execution."""
    result = await client.set_editor_layout(
        main_screen=params.main_screen,
        distraction_free_mode=params.distraction_free_mode,
        active_scene_path=params.active_scene_path,
    )
    return format_result(result)
