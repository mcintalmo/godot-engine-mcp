"""Tool handlers for Godot Global Illumination & Baked Lighting."""

from godot_engine_mcp.client.base import GodotClient
from godot_engine_mcp.models.lightmap_gi import (
    BakeLightmapsInput,
    ConfigureLightmapGIInput,
)
from godot_engine_mcp.tools.formatters import format_result


async def handle_configure_lightmap_gi(
    client: GodotClient,
    params: ConfigureLightmapGIInput,
) -> str:
    """Handle godot_configure_lightmap_gi tool execution."""
    result = await client.configure_lightmap_gi(
        gi_type=params.gi_type,
        node_name=params.node_name,
        parent_path=params.parent_path,
        quality=params.quality,
        bounces=params.bounces,
        use_denoiser=params.use_denoiser,
        denoiser_name=params.denoiser_name,
        size=params.size,
        origin_offset=params.origin_offset,
        interior=params.interior,
    )
    return format_result(result)


async def handle_bake_lightmaps(
    client: GodotClient,
    params: BakeLightmapsInput,
) -> str:
    """Handle godot_bake_lightmaps tool execution."""
    result = await client.bake_lightmaps(
        lightmap_node_path=params.lightmap_node_path,
        bake_mode=params.bake_mode,
        save_path=params.save_path,
    )
    return format_result(result)
