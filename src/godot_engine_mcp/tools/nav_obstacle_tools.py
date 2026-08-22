"""Tool handlers for Godot Navigation Obstacles and Avoidance."""

from godot_engine_mcp.client.base import GodotClient
from godot_engine_mcp.models.nav_obstacle import ConfigureNavigationObstacleInput
from godot_engine_mcp.tools.formatters import format_result


async def handle_configure_navigation_obstacle(
    client: GodotClient,
    params: ConfigureNavigationObstacleInput,
) -> str:
    """Handle godot_configure_navigation_obstacle tool execution."""
    result = await client.configure_navigation_obstacle(
        node_path=params.node_path,
        parent_path=params.parent_path,
        node_name=params.node_name,
        is_3d=params.is_3d,
        radius=params.radius,
        velocity=params.velocity,
        vertices=params.vertices,
        avoidance_layers=params.avoidance_layers,
        affect_navigation_mesh=params.affect_navigation_mesh,
        carve_navigation_mesh=params.carve_navigation_mesh,
    )
    return format_result(result)
