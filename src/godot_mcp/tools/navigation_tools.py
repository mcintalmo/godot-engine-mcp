"""Tool handlers for NavMesh baking and NavigationRegion creation."""

from godot_mcp.client.base import GodotClient
from godot_mcp.models.navigation import (
    BakeNavMeshInput,
    CreateNavigationRegionInput,
)
from godot_mcp.tools.formatters import format_result


async def handle_bake_navmesh(
    client: GodotClient,
    params: BakeNavMeshInput,
) -> str:
    """Handle godot_bake_navmesh tool execution."""
    result = await client.bake_navmesh(
        node_path=params.node_path,
        dimension=params.dimension.value,
        on_thread=params.on_thread,
        agent_radius=params.agent_radius,
        agent_height=params.agent_height,
        agent_max_climb=params.agent_max_climb,
        agent_max_slope=params.agent_max_slope,
        cell_size=params.cell_size,
        cell_height=params.cell_height,
        save_navmesh_path=params.save_navmesh_path,
    )
    return format_result(result)


async def handle_create_navigation_region(
    client: GodotClient,
    params: CreateNavigationRegionInput,
) -> str:
    """Handle godot_create_navigation_region tool execution."""
    result = await client.create_navigation_region(
        name=params.name,
        dimension=params.dimension.value,
        parent_node_path=params.parent_node_path,
        navmesh_path=params.navmesh_path,
    )
    return format_result(result)
