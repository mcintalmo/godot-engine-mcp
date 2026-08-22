"""Tool handlers for Godot Autoload singletons in project.godot."""

from godot_engine_mcp.client.base import GodotClient
from godot_engine_mcp.models.autoload import (
    GetAutoloadsInput,
    SetAutoloadInput,
)
from godot_engine_mcp.tools.formatters import format_result


async def handle_get_autoloads(
    client: GodotClient,
    params: GetAutoloadsInput,
) -> str:
    """Handle godot_get_autoloads tool execution."""
    result = await client.get_autoloads()
    return format_result(result)


async def handle_set_autoload(
    client: GodotClient,
    params: SetAutoloadInput,
) -> str:
    """Handle godot_set_autoload tool execution."""
    result = await client.set_autoload(
        name=params.name,
        path=params.path,
        is_singleton=params.is_singleton,
        remove=params.remove,
    )
    return format_result(result)
