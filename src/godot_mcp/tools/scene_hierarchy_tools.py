"""Tool handlers for Godot Scene Hierarchy Mutations and Packed Scene Instantiation."""

from godot_mcp.client.base import GodotClient
from godot_mcp.models.scene_hierarchy import (
    DuplicateNodeInput,
    ReparentNodeInput,
    SetNodeOwnerInput,
)
from godot_mcp.tools.formatters import format_result


async def handle_reparent_node(
    client: GodotClient,
    params: ReparentNodeInput,
) -> str:
    """Handle godot_reparent_node tool execution."""
    result = await client.reparent_node(
        node_path=params.node_path,
        new_parent_path=params.new_parent_path,
        keep_global_transform=params.keep_global_transform,
        new_index=params.new_index,
    )
    return format_result(result)


async def handle_duplicate_node(
    client: GodotClient,
    params: DuplicateNodeInput,
) -> str:
    """Handle godot_duplicate_node tool execution."""
    result = await client.duplicate_node(
        node_path=params.node_path,
        new_name=params.new_name,
        target_parent_path=params.target_parent_path,
        duplicate_signals=params.duplicate_signals,
        duplicate_groups=params.duplicate_groups,
        duplicate_scripts=params.duplicate_scripts,
    )
    return format_result(result)


async def handle_set_node_owner(
    client: GodotClient,
    params: SetNodeOwnerInput,
) -> str:
    """Handle godot_set_node_owner tool execution."""
    result = await client.set_node_owner(
        node_path=params.node_path,
        owner_node_path=params.owner_node_path,
        recursive=params.recursive,
    )
    return format_result(result)
