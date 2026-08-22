"""Tool handlers for Godot AnimationTree and State Machine graphs."""

from godot_engine_mcp.client.base import GodotClient
from godot_engine_mcp.models.anim_tree import ConfigureAnimationTreeInput
from godot_engine_mcp.tools.formatters import format_result


async def handle_configure_animation_tree(
    client: GodotClient,
    params: ConfigureAnimationTreeInput,
) -> str:
    """Handle godot_configure_animation_tree tool execution."""
    result = await client.configure_animation_tree(
        node_path=params.node_path,
        parent_path=params.parent_path,
        node_name=params.node_name,
        anim_player_path=params.anim_player_path,
        tree_type=params.tree_type,
        active=params.active,
        states=params.states,
        transitions=params.transitions,
        save_as_resource_path=params.save_as_resource_path,
    )
    return format_result(result)
