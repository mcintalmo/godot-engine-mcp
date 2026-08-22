"""Tool handlers for Godot GPU MultiMesh Scattering & Foliage Systems."""

from godot_mcp.client.base import GodotClient
from godot_mcp.models.multimesh_scatter import (
    ConfigureLODManagerInput,
    ScatterMultiMeshInput,
)
from godot_mcp.tools.formatters import format_result


async def handle_scatter_multimesh(
    client: GodotClient,
    params: ScatterMultiMeshInput,
) -> str:
    """Handle godot_scatter_multimesh tool execution."""
    result = await client.scatter_multimesh(
        mesh_path=params.mesh_path,
        node_name=params.node_name,
        parent_path=params.parent_path,
        instance_count=params.instance_count,
        area_size=params.area_size,
        min_scale=params.min_scale,
        max_scale=params.max_scale,
        random_yaw=params.random_yaw,
        align_to_surface=params.align_to_surface,
    )
    return format_result(result)


async def handle_configure_lod_manager(
    client: GodotClient,
    params: ConfigureLODManagerInput,
) -> str:
    """Handle godot_configure_lod_manager tool execution."""
    result = await client.configure_lod_manager(
        node_path=params.node_path,
        visibility_range_begin=params.visibility_range_begin,
        visibility_range_end=params.visibility_range_end,
        visibility_range_begin_margin=params.visibility_range_begin_margin,
        visibility_range_end_margin=params.visibility_range_end_margin,
        fade_mode=params.fade_mode,
    )
    return format_result(result)
