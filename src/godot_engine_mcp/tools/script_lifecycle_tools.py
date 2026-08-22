"""Tool handlers for Godot Live Script Lifecycle, Hot-Reload & Exported Property Reflection."""

from godot_engine_mcp.client.base import GodotClient
from godot_engine_mcp.models.script_lifecycle import (
    AttachScriptInput,
    GetNodeScriptInfoInput,
    ReloadScriptsInput,
)
from godot_engine_mcp.tools.formatters import format_result


async def handle_attach_script(
    client: GodotClient,
    params: AttachScriptInput,
) -> str:
    """Handle godot_attach_script tool execution."""
    result = await client.attach_script(
        node_path=params.node_path,
        script_path=params.script_path,
        initial_properties=params.initial_properties,
    )
    return format_result(result)


async def handle_reload_scripts(
    client: GodotClient,
    params: ReloadScriptsInput,
) -> str:
    """Handle godot_reload_scripts tool execution."""
    result = await client.reload_scripts(
        script_paths=params.script_paths,
    )
    return format_result(result)


async def handle_get_node_script_info(
    client: GodotClient,
    params: GetNodeScriptInfoInput,
) -> str:
    """Handle godot_get_node_script_info tool execution."""
    result = await client.get_node_script_info(
        node_path=params.node_path,
    )
    return format_result(result)
