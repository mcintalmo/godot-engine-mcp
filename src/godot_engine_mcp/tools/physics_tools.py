"""Tool handlers for Godot 3D physics geometric queries, raycasts, shape sweeps, and body telemetry."""

from godot_engine_mcp.client.base import GodotClient
from godot_engine_mcp.models.physics import (
    CastRay3DInput,
    CastShape3DInput,
    GetBodyPhysicsState3DInput,
    SetPhysicsDebugModeInput,
)
from godot_engine_mcp.tools.formatters import format_result


async def handle_cast_ray_3d(
    client: GodotClient,
    params: CastRay3DInput,
) -> str:
    """Handle godot_cast_ray_3d tool execution."""
    result = await client.cast_ray_3d(
        from_pos=params.from_pos,
        to_pos=params.to_pos,
        collision_mask=params.collision_mask,
        collide_with_bodies=params.collide_with_bodies,
        collide_with_areas=params.collide_with_areas,
        hit_from_inside=params.hit_from_inside,
        exclude_nodes=params.exclude_nodes,
    )
    return format_result(result)


async def handle_cast_shape_3d(
    client: GodotClient,
    params: CastShape3DInput,
) -> str:
    """Handle godot_cast_shape_3d tool execution."""
    result = await client.cast_shape_3d(
        shape_type=params.shape_type.value,
        shape_params=params.shape_params,
        origin=params.origin,
        motion=params.motion,
        collision_mask=params.collision_mask,
        max_results=params.max_results,
    )
    return format_result(result)


async def handle_get_body_physics_state_3d(
    client: GodotClient,
    params: GetBodyPhysicsState3DInput,
) -> str:
    """Handle godot_get_body_physics_state_3d tool execution."""
    result = await client.get_body_physics_state_3d(
        node_path=params.node_path,
    )
    return format_result(result)


async def handle_set_physics_debug_mode(
    client: GodotClient,
    params: SetPhysicsDebugModeInput,
) -> str:
    """Handle godot_set_physics_debug_mode tool execution."""
    result = await client.set_physics_debug_mode(
        visible_collision_shapes=params.visible_collision_shapes,
        visible_paths=params.visible_paths,
        visible_navigation=params.visible_navigation,
        collision_debug_color=params.collision_debug_color,
    )
    return format_result(result)
