"""Tool handlers for Godot InputMap and project input actions."""

from godot_mcp.client.base import GodotClient
from godot_mcp.models.input_map import (
    ConfigureInputActionInput,
    GetInputActionsInput,
)
from godot_mcp.tools.formatters import format_result


async def handle_get_input_actions(
    client: GodotClient,
    params: GetInputActionsInput,
) -> str:
    """Handle godot_get_input_actions tool execution."""
    result = await client.get_input_actions(
        filter_prefix=params.filter_prefix,
    )
    return format_result(result)


async def handle_configure_input_action(
    client: GodotClient,
    params: ConfigureInputActionInput,
) -> str:
    """Handle godot_configure_input_action tool execution."""
    events_payload = [e.model_dump(exclude_none=True) for e in params.events]
    result = await client.configure_input_action(
        action_name=params.action_name,
        deadzone=params.deadzone,
        events=events_payload,
        replace_existing=params.replace_existing,
        save_to_project_settings=params.save_to_project_settings,
    )
    return format_result(result)
