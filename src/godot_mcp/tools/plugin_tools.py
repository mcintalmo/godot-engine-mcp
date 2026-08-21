"""Tool handlers for Godot Editor Plugin / Addon lifecycle management."""

from godot_mcp.client.base import GodotClient
from godot_mcp.models.plugin_mgr import (
    GetPluginsInput,
    SetPluginStatusInput,
)
from godot_mcp.tools.formatters import format_result


async def handle_get_plugins(
    client: GodotClient,
    params: GetPluginsInput,
) -> str:
    """Handle godot_get_plugins tool execution."""
    result = await client.get_plugins(
        enabled_only=params.enabled_only,
    )
    return format_result(result)


async def handle_set_plugin_status(
    client: GodotClient,
    params: SetPluginStatusInput,
) -> str:
    """Handle godot_set_plugin_status tool execution."""
    result = await client.set_plugin_status(
        plugin_name=params.plugin_name,
        enabled=params.enabled,
    )
    return format_result(result)
