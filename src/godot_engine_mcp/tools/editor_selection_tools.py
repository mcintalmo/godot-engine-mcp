"""Tool handlers for Godot Editor SceneTree selection management."""

from godot_engine_mcp.client.base import GodotClient
from godot_engine_mcp.models.editor_selection import (
    GetSelectedNodesInput,
    SetSelectedNodesInput,
)
from godot_engine_mcp.tools.formatters import format_result


async def handle_get_selected_nodes(
    client: GodotClient,
    params: GetSelectedNodesInput,
) -> str:
    """Handle godot_get_selected_nodes tool execution."""
    result = await client.get_selected_nodes(
        include_properties=params.include_properties
    )
    return format_result(result)


async def handle_set_selected_nodes(
    client: GodotClient,
    params: SetSelectedNodesInput,
) -> str:
    """Handle godot_set_selected_nodes tool execution."""
    result = await client.set_selected_nodes(
        node_paths=params.node_paths,
        clear_previous=params.clear_previous,
        inspect_primary=params.inspect_primary,
    )
    return format_result(result)
