"""Tool handlers for Godot Resource UIDs and Asset Dependencies."""

from godot_engine_mcp.client.base import GodotClient
from godot_engine_mcp.models.uid_dep import (
    GetDependenciesInput,
    GetUIDInput,
    ResolveUIDInput,
)
from godot_engine_mcp.tools.formatters import format_result


async def handle_get_uid(
    client: GodotClient,
    params: GetUIDInput,
) -> str:
    """Handle godot_get_uid tool execution."""
    result = await client.get_uid(
        path=params.path,
    )
    return format_result(result)


async def handle_resolve_uid(
    client: GodotClient,
    params: ResolveUIDInput,
) -> str:
    """Handle godot_resolve_uid tool execution."""
    result = await client.resolve_uid(
        uid=params.uid,
    )
    return format_result(result)


async def handle_get_dependencies(
    client: GodotClient,
    params: GetDependenciesInput,
) -> str:
    """Handle godot_get_dependencies tool execution."""
    result = await client.get_dependencies(
        path=params.path,
    )
    return format_result(result)
