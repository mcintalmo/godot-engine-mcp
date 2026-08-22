"""Tool handlers for Godot VFX particle systems."""

from godot_engine_mcp.client.base import GodotClient
from godot_engine_mcp.models.particles import ConfigureParticlesInput
from godot_engine_mcp.tools.formatters import format_result


async def handle_configure_particles(
    client: GodotClient,
    params: ConfigureParticlesInput,
) -> str:
    """Handle godot_configure_particles tool execution."""
    result = await client.configure_particles(
        node_path=params.node_path,
        parent_path=params.parent_path,
        node_name=params.node_name,
        save_path=params.save_path,
        particle_type=params.particle_type.value,
        amount=params.amount,
        lifetime=params.lifetime,
        explosiveness=params.explosiveness,
        emission_shape=params.emission_shape.value,
        emission_sphere_radius=params.emission_sphere_radius,
        emission_box_extents=params.emission_box_extents,
        direction=params.direction,
        spread=params.spread,
        initial_velocity_min=params.initial_velocity_min,
        initial_velocity_max=params.initial_velocity_max,
        gravity=params.gravity,
        color_gradient=params.color_gradient,
        scale_min=params.scale_min,
        scale_max=params.scale_max,
        emitting=params.emitting,
    )
    return format_result(result)
