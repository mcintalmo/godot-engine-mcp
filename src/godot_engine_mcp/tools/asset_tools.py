"""Tool handlers for asset reimport and collision polygon creation."""

from godot_engine_mcp.client.base import GodotClient
from godot_engine_mcp.models.asset import (
    CreateCollisionPolygonInput,
    ReimportAssetInput,
)
from godot_engine_mcp.tools.formatters import format_result


async def handle_reimport_asset(
    client: GodotClient,
    params: ReimportAssetInput,
) -> str:
    """Handle godot_reimport_asset tool execution."""
    result = await client.reimport_asset(
        asset_path=params.asset_path,
        preset=params.preset.value if params.preset else None,
        custom_params=params.custom_params,
    )
    return format_result(result)


async def handle_create_collision_polygon(
    client: GodotClient,
    params: CreateCollisionPolygonInput,
) -> str:
    """Handle godot_create_collision_polygon tool execution."""
    result = await client.create_collision_polygon(
        points=params.points,
        polygon_type=params.polygon_type.value,
        parent_node_path=params.parent_node_path,
        node_name=params.node_name,
        depth=params.depth,
        disabled=params.disabled,
    )
    return format_result(result)
