"""Tool handlers for Godot 3D GridMaps & Procedural Bezier Paths."""

from godot_mcp.client.base import GodotClient
from godot_mcp.models.gridmap_path import (
    ConfigureGridMapInput,
    CreateCurvePathInput,
)
from godot_mcp.tools.formatters import format_result


async def handle_configure_gridmap(
    client: GodotClient,
    params: ConfigureGridMapInput,
) -> str:
    """Handle godot_configure_gridmap tool execution."""
    result = await client.configure_gridmap(
        gridmap_node_path=params.gridmap_node_path,
        mesh_library_path=params.mesh_library_path,
        cell_size=params.cell_size,
        cells_to_set=[c.model_dump() for c in params.cells_to_set]
        if params.cells_to_set
        else None,
        cells_to_clear=params.cells_to_clear,
        clear_all=params.clear_all,
        collision_layer=params.collision_layer,
        collision_mask=params.collision_mask,
    )
    return format_result(result)


async def handle_create_curve_path(
    client: GodotClient,
    params: CreateCurvePathInput,
) -> str:
    """Handle godot_create_curve_path tool execution."""
    result = await client.create_curve_path(
        path_type=params.path_type,
        node_name=params.node_name,
        parent_path=params.parent_path,
        points=[p.model_dump() for p in params.points],
        closed=params.closed,
        add_path_follow=params.add_path_follow,
        path_follow_name=params.path_follow_name,
    )
    return format_result(result)
