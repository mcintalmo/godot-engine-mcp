"""Tool handlers for Godot Editor selection, node focus, and workspace navigation."""

from godot_mcp.client.base import GodotClient
from godot_mcp.models.editor_focus import (
    FocusNodeInput,
    SetEditorSelectionInput,
)
from godot_mcp.tools.formatters import format_result


async def handle_set_editor_selection(
    client: GodotClient,
    params: SetEditorSelectionInput,
) -> str:
    """Handle godot_set_editor_selection tool execution."""
    result = await client.set_editor_selection(
        node_paths=params.node_paths,
        clear_previous=params.clear_previous,
    )
    return format_result(result)


async def handle_focus_node(
    client: GodotClient,
    params: FocusNodeInput,
) -> str:
    """Handle godot_focus_node tool execution."""
    result = await client.focus_node(
        node_path=params.node_path,
        main_screen=params.main_screen,
    )
    return format_result(result)
