"""Tool handlers for Godot WorldEnvironment, post-processing, and lighting."""

from godot_engine_mcp.client.base import GodotClient
from godot_engine_mcp.models.environment import ConfigureEnvironmentInput
from godot_engine_mcp.tools.formatters import format_result


async def handle_configure_environment(
    client: GodotClient,
    params: ConfigureEnvironmentInput,
) -> str:
    """Handle godot_configure_environment tool execution."""
    result = await client.configure_environment(
        save_path=params.save_path,
        node_path=params.node_path,
        background_mode=params.background_mode.value
        if params.background_mode
        else None,
        background_color=params.background_color,
        sky_type=params.sky_type.value if params.sky_type else None,
        sky_params=params.sky_params,
        ambient_light_source=params.ambient_light_source,
        ambient_light_color=params.ambient_light_color,
        ambient_light_energy=params.ambient_light_energy,
        tonemap_mode=params.tonemap_mode.value if params.tonemap_mode else None,
        tonemap_exposure=params.tonemap_exposure,
        glow_enabled=params.glow_enabled,
        glow_intensity=params.glow_intensity,
        glow_bloom=params.glow_bloom,
        glow_blend_mode=params.glow_blend_mode.value
        if params.glow_blend_mode
        else None,
        ssao_enabled=params.ssao_enabled,
        ssao_radius=params.ssao_radius,
        ssao_intensity=params.ssao_intensity,
        ssil_enabled=params.ssil_enabled,
        ssr_enabled=params.ssr_enabled,
        volumetric_fog_enabled=params.volumetric_fog_enabled,
        volumetric_fog_density=params.volumetric_fog_density,
        volumetric_fog_albedo=params.volumetric_fog_albedo,
    )
    return format_result(result)
