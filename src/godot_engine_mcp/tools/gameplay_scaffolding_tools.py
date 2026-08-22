"""Tool handlers for Godot Gameplay AI & State Machine Scaffolding."""

from godot_engine_mcp.client.base import GodotClient
from godot_engine_mcp.models.gameplay_scaffolding import (
    CreateDialogueResourceInput,
    ScaffoldStateMachineInput,
)
from godot_engine_mcp.tools.formatters import format_result


async def handle_scaffold_state_machine(
    client: GodotClient,
    params: ScaffoldStateMachineInput,
) -> str:
    """Handle godot_scaffold_state_machine tool execution."""
    result = await client.scaffold_state_machine(
        target_dir=params.target_dir,
        machine_name=params.machine_name,
        states=params.states,
        generate_node_hierarchy=params.generate_node_hierarchy,
        parent_node_path=params.parent_node_path,
    )
    return format_result(result)


async def handle_create_dialogue_resource(
    client: GodotClient,
    params: CreateDialogueResourceInput,
) -> str:
    """Handle godot_create_dialogue_resource tool execution."""
    result = await client.create_dialogue_resource(
        resource_path=params.resource_path,
        format=params.format,
        dialogue_nodes=[n.model_dump() for n in params.dialogue_nodes],
    )
    return format_result(result)
