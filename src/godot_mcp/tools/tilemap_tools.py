"""Tool handlers for TileMapLayer cell painting, querying, and layer management."""

from godot_mcp.client.base import GodotClient
from godot_mcp.models.tilemap import (
    CreateTileMapLayerInput,
    GetTileMapCellsInput,
    SetTileMapCellsInput,
)
from godot_mcp.tools.formatters import format_result


async def handle_set_tilemap_cells(
    client: GodotClient,
    params: SetTileMapCellsInput,
) -> str:
    """Handle godot_set_tilemap_cells tool execution."""
    raw_cells = [c.model_dump() for c in params.cells]
    result = await client.set_tilemap_cells(
        node_path=params.node_path,
        cells=raw_cells,
        clear_before_paint=params.clear_before_paint,
    )
    return format_result(result)


async def handle_get_tilemap_cells(
    client: GodotClient,
    params: GetTileMapCellsInput,
) -> str:
    """Handle godot_get_tilemap_cells tool execution."""
    result = await client.get_tilemap_cells(
        node_path=params.node_path,
        region=params.region,
    )
    return format_result(result)


async def handle_create_tilemap_layer(
    client: GodotClient,
    params: CreateTileMapLayerInput,
) -> str:
    """Handle godot_create_tilemap_layer tool execution."""
    result = await client.create_tilemap_layer(
        name=params.name,
        parent_node_path=params.parent_node_path,
        tile_set_path=params.tile_set_path,
    )
    return format_result(result)
