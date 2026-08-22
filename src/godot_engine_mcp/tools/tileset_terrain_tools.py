"""Tool handlers for Godot TileSet Terrain and Autotiling configuration."""

from godot_engine_mcp.client.base import GodotClient
from godot_engine_mcp.models.tileset_terrain import ConfigureTileSetTerrainInput
from godot_engine_mcp.tools.formatters import format_result


async def handle_configure_tileset_terrain(
    client: GodotClient,
    params: ConfigureTileSetTerrainInput,
) -> str:
    """Handle godot_configure_tileset_terrain tool execution."""
    result = await client.configure_tileset_terrain(
        tileset_path=params.tileset_path,
        terrain_set=params.terrain_set,
        mode=params.mode,
        terrains=params.terrains,
        tile_peering_bits=params.tile_peering_bits,
        save_path=params.save_path,
    )
    return format_result(result)
