"""Tool handlers for Godot Editor Undo/Redo operations."""

from godot_engine_mcp.client.base import GodotClient
from godot_engine_mcp.models.editor_history import RedoInput, UndoInput
from godot_engine_mcp.tools.formatters import format_result


async def handle_undo(
    client: GodotClient,
    params: UndoInput,
) -> str:
    """Handle godot_undo tool execution."""
    result = await client.undo_action(history_id=params.history_id)
    return format_result(result)


async def handle_redo(
    client: GodotClient,
    params: RedoInput,
) -> str:
    """Handle godot_redo tool execution."""
    result = await client.redo_action(history_id=params.history_id)
    return format_result(result)
